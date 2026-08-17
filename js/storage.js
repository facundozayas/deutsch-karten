// Capa de persistencia (IndexedDB). No sabe nada de UI ni de FSRS directamente:
// recibe y devuelve objetos planos. `due` / `last_review` / `reviewedAt` se
// guardan como strings ISO (comparables lexicográficamente, sin problemas de
// structured-clone entre navegadores).

const DB_NAME = 'german-app-db';
const DB_VERSION = 2;

const STORE_CARDS = 'cardStates';
const STORE_LOG = 'reviewLog';
const STORE_META = 'meta';
const STORE_CUSTOM_VOCAB = 'customVocab';

let dbPromise = null;

export function openDatabase() {
  if (dbPromise) return dbPromise;
  dbPromise = new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);

    req.onupgradeneeded = () => {
      const db = req.result;

      if (!db.objectStoreNames.contains(STORE_CARDS)) {
        const cards = db.createObjectStore(STORE_CARDS, { keyPath: 'id' });
        cards.createIndex('by_due', 'due', { unique: false });
        cards.createIndex('by_state', 'state', { unique: false });
      }

      if (!db.objectStoreNames.contains(STORE_LOG)) {
        const log = db.createObjectStore(STORE_LOG, { keyPath: 'logId', autoIncrement: true });
        log.createIndex('by_cardId', 'cardId', { unique: false });
        log.createIndex('by_reviewedAt', 'reviewedAt', { unique: false });
      }

      if (!db.objectStoreNames.contains(STORE_META)) {
        db.createObjectStore(STORE_META, { keyPath: 'key' });
      }

      // v2: vocabulario que no viene de los archivos estáticos (data/vocab-*.json)
      // — mazos importados de Anki y, a futuro, palabras agregadas a mano.
      if (!db.objectStoreNames.contains(STORE_CUSTOM_VOCAB)) {
        db.createObjectStore(STORE_CUSTOM_VOCAB, { keyPath: 'id' });
      }
    };

    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
  return dbPromise;
}

function tx(db, storeNames, mode = 'readonly') {
  return db.transaction(storeNames, mode);
}

function reqToPromise(req) {
  return new Promise((resolve, reject) => {
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

// ---- serialización de cardState (Date <-> ISO string) ----

function serializeCardState(id, card) {
  return {
    id,
    due: toIso(card.due),
    stability: card.stability,
    difficulty: card.difficulty,
    elapsed_days: card.elapsed_days,
    scheduled_days: card.scheduled_days,
    learning_steps: card.learning_steps,
    reps: card.reps,
    lapses: card.lapses,
    state: card.state,
    last_review: card.last_review ? toIso(card.last_review) : null,
  };
}

function deserializeCardState(record) {
  if (!record) return null;
  return {
    ...record,
    due: new Date(record.due),
    last_review: record.last_review ? new Date(record.last_review) : undefined,
  };
}

function toIso(date) {
  return (date instanceof Date ? date : new Date(date)).toISOString();
}

// ---- cardStates ----

export async function getCardState(id) {
  const db = await openDatabase();
  const store = tx(db, STORE_CARDS).objectStore(STORE_CARDS);
  const record = await reqToPromise(store.get(id));
  return deserializeCardState(record);
}

export async function getAllCardStates() {
  const db = await openDatabase();
  const store = tx(db, STORE_CARDS).objectStore(STORE_CARDS);
  const records = await reqToPromise(store.getAll());
  return records.map(deserializeCardState);
}

export async function putCardState(id, card) {
  const db = await openDatabase();
  const store = tx(db, STORE_CARDS, 'readwrite').objectStore(STORE_CARDS);
  await reqToPromise(store.put(serializeCardState(id, card)));
}

/**
 * Inserta estado FSRS inicial para cualquier id de vocabulario que todavía
 * no tenga tarjeta en la base. Idempotente — se puede llamar en cada boot.
 */
export async function bulkInitCardStates(vocabEntries, createNewCardState) {
  const db = await openDatabase();
  const store = tx(db, STORE_CARDS, 'readwrite').objectStore(STORE_CARDS);
  const existingIds = new Set(await reqToPromise(store.getAllKeys()));

  let added = 0;
  for (const entry of vocabEntries) {
    if (!existingIds.has(entry.id)) {
      const card = createNewCardState();
      store.put(serializeCardState(entry.id, card));
      added++;
    }
  }
  await txDone(store.transaction);
  return added;
}

export async function getDueCards(now = new Date()) {
  const db = await openDatabase();
  const store = tx(db, STORE_CARDS).objectStore(STORE_CARDS);
  const index = store.index('by_due');
  const range = IDBKeyRange.upperBound(toIso(now));
  const records = await reqToPromise(index.getAll(range));
  return records.map(deserializeCardState);
}

export async function getStateCounts() {
  const all = await getAllCardStates();
  const counts = { 0: 0, 1: 0, 2: 0, 3: 0 }; // New, Learning, Review, Relearning
  for (const c of all) {
    counts[c.state] = (counts[c.state] || 0) + 1;
  }
  return { counts, total: all.length };
}

// ---- reviewLog ----

export async function saveReview(id, updatedCard, reviewLogEntry) {
  const db = await openDatabase();
  const transaction = tx(db, [STORE_CARDS, STORE_LOG], 'readwrite');
  transaction.objectStore(STORE_CARDS).put(serializeCardState(id, updatedCard));
  transaction.objectStore(STORE_LOG).add({
    cardId: id,
    grade: reviewLogEntry.rating,
    reviewedAt: toIso(new Date()),
    elapsedDays: reviewLogEntry.scheduled_days ?? null,
    stability: reviewLogEntry.stability,
    difficulty: reviewLogEntry.difficulty,
  });
  await txDone(transaction);
}

export async function getReviewLogSince(sinceDate) {
  const db = await openDatabase();
  const store = tx(db, STORE_LOG).objectStore(STORE_LOG);
  const index = store.index('by_reviewedAt');
  const range = IDBKeyRange.lowerBound(toIso(sinceDate));
  return reqToPromise(index.getAll(range));
}

export async function getAllReviewLog() {
  const db = await openDatabase();
  const store = tx(db, STORE_LOG).objectStore(STORE_LOG);
  return reqToPromise(store.getAll());
}

// ---- meta ----

export async function getMeta(key, fallback = null) {
  const db = await openDatabase();
  const store = tx(db, STORE_META).objectStore(STORE_META);
  const record = await reqToPromise(store.get(key));
  return record ? record.value : fallback;
}

export async function setMeta(key, value) {
  const db = await openDatabase();
  const store = tx(db, STORE_META, 'readwrite').objectStore(STORE_META);
  await reqToPromise(store.put({ key, value }));
}

// ---- niveles ----

export async function getUnlockedLevels() {
  return getMeta('unlockedLevels', ['A1']);
}

export async function setUnlockedLevels(levels) {
  await setMeta('unlockedLevels', levels);
}

// ---- vocabulario personalizado (import de Anki, agregado a mano) ----

export async function getAllCustomVocab() {
  const db = await openDatabase();
  const store = tx(db, STORE_CUSTOM_VOCAB).objectStore(STORE_CUSTOM_VOCAB);
  return reqToPromise(store.getAll());
}

export async function addCustomVocabEntries(entries) {
  const db = await openDatabase();
  const store = tx(db, STORE_CUSTOM_VOCAB, 'readwrite').objectStore(STORE_CUSTOM_VOCAB);
  for (const entry of entries) store.put(entry);
  await txDone(store.transaction);
}

export async function deleteCustomVocabEntry(id) {
  const db = await openDatabase();
  const store = tx(db, STORE_CUSTOM_VOCAB, 'readwrite').objectStore(STORE_CUSTOM_VOCAB);
  await reqToPromise(store.delete(id));
}

// ---- stats ----

export async function getStatsSnapshot() {
  const { counts, total } = await getStateCounts();

  const startOfToday = new Date();
  startOfToday.setHours(0, 0, 0, 0);
  const todayLog = await getReviewLogSince(startOfToday);

  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  const recentLog = await getReviewLogSince(thirtyDaysAgo);
  const goodOrEasy = recentLog.filter((r) => r.grade === 3 || r.grade === 4).length;
  const retention = recentLog.length > 0 ? Math.round((goodOrEasy / recentLog.length) * 100) : null;

  const allLog = await getAllReviewLog();
  const streak = computeStreak(allLog);

  return {
    reviewedToday: todayLog.length,
    streak,
    retention,
    total,
    counts,
  };
}

function computeStreak(logEntries) {
  if (logEntries.length === 0) return 0;

  const days = new Set(
    logEntries.map((e) => new Date(e.reviewedAt).toDateString())
  );

  let streak = 0;
  const cursor = new Date();
  cursor.setHours(0, 0, 0, 0);

  // Si todavía no repasó hoy, el streak cuenta desde ayer hacia atrás
  // (no se rompe la racha hasta que termine el día).
  if (!days.has(cursor.toDateString())) {
    cursor.setDate(cursor.getDate() - 1);
  }

  while (days.has(cursor.toDateString())) {
    streak++;
    cursor.setDate(cursor.getDate() - 1);
  }

  return streak;
}

// ---- backup export/import ----

export async function exportBackup() {
  const cards = await getAllCardStates();
  const log = await getAllReviewLog();
  const customVocab = await getAllCustomVocab();
  const db = await openDatabase();
  const metaStore = tx(db, STORE_META).objectStore(STORE_META);
  const metaRows = await reqToPromise(metaStore.getAll());

  return {
    exportedAt: new Date().toISOString(),
    version: 2,
    cardStates: cards.map((c) => serializeCardState(c.id, c)),
    reviewLog: log,
    meta: metaRows,
    customVocab,
  };
}

export async function importBackup(data) {
  if (!data || !Array.isArray(data.cardStates)) {
    throw new Error('Archivo de backup inválido');
  }
  const db = await openDatabase();
  const transaction = tx(db, [STORE_CARDS, STORE_LOG, STORE_META, STORE_CUSTOM_VOCAB], 'readwrite');

  const cardsStore = transaction.objectStore(STORE_CARDS);
  cardsStore.clear();
  for (const c of data.cardStates) cardsStore.put(c);

  const logStore = transaction.objectStore(STORE_LOG);
  logStore.clear();
  for (const entry of data.reviewLog || []) {
    const { logId, ...rest } = entry;
    logStore.add(rest);
  }

  const metaStore = transaction.objectStore(STORE_META);
  metaStore.clear();
  for (const m of data.meta || []) metaStore.put(m);

  // customVocab es nuevo desde la v2 del backup; los backups viejos (v1,
  // hechos antes de esta función) simplemente no traen nada acá.
  const customVocabStore = transaction.objectStore(STORE_CUSTOM_VOCAB);
  customVocabStore.clear();
  for (const entry of data.customVocab || []) customVocabStore.put(entry);

  await txDone(transaction);
}

function txDone(transaction) {
  return new Promise((resolve, reject) => {
    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error);
    transaction.onabort = () => reject(transaction.error);
  });
}
