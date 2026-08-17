// Import de mazos de Anki (.apkg). JSZip y sql.js se cargan de forma
// perezosa (inyectando <script> clásicos, no ES modules — así vienen
// empaquetados esas librerías) la primera vez que se usa esta función, para
// no engordar el precache de la PWA con ~700KB que la mayoría de las
// sesiones nunca va a necesitar. Ver service-worker.js.

const JSZIP_URL = './js/vendor/jszip.js';
const SQLJS_URL = './js/vendor/sql-wasm.js';
const SQLJS_WASM_URL = './js/vendor/sql-wasm.wasm';

let librariesPromise = null;

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = src;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error(`No se pudo cargar ${src} (¿estás offline?)`));
    document.head.appendChild(s);
  });
}

export function loadLibraries() {
  if (librariesPromise) return librariesPromise;
  librariesPromise = (async () => {
    if (!window.JSZip) await loadScript(JSZIP_URL);
    if (!window.initSqlJs) await loadScript(SQLJS_URL);
    const SQL = await window.initSqlJs({ locateFile: () => SQLJS_WASM_URL });
    return { JSZip: window.JSZip, SQL };
  })();
  return librariesPromise;
}

/**
 * Parsea un archivo .apkg (ZIP con una base SQLite de Anki adentro) y
 * devuelve los nombres de campo del primer modelo de nota encontrado + las
 * notas con sus campos ya separados (el separador de Anki es \x1f).
 *
 * @param {File} file
 * @returns {Promise<{ fieldNames: string[], notes: {id:number, fields:string[], tags:string}[] }>}
 */
export async function parseApkg(file) {
  const { JSZip, SQL } = await loadLibraries();

  const zip = await JSZip.loadAsync(file);
  const dbFileName = zip.file('collection.anki21')
    ? 'collection.anki21'
    : zip.file('collection.anki2')
      ? 'collection.anki2'
      : null;

  if (!dbFileName) {
    throw new Error(
      'No se encontró una base de Anki compatible en este archivo. Si tu mazo usa el formato más nuevo (.anki21b comprimido), probá reexportarlo desde Anki Desktop con "Support older Anki versions" activado.'
    );
  }

  const dbBytes = await zip.file(dbFileName).async('uint8array');
  const db = new SQL.Database(dbBytes);

  let fieldNames = [];
  try {
    const colResult = db.exec('SELECT models FROM col LIMIT 1');
    if (colResult.length > 0) {
      const modelsJson = JSON.parse(colResult[0].values[0][0]);
      const firstModel = Object.values(modelsJson)[0];
      if (firstModel && Array.isArray(firstModel.flds)) {
        fieldNames = firstModel.flds.map((f) => f.name);
      }
    }
  } catch (err) {
    console.warn('No se pudieron leer los nombres de campo del modelo de Anki', err);
  }

  const notesResult = db.exec('SELECT id, flds, tags FROM notes');
  const notes = [];
  let maxFieldCount = 0;
  if (notesResult.length > 0) {
    for (const row of notesResult[0].values) {
      const [id, flds, tags] = row;
      const fields = String(flds).split('\x1f');
      maxFieldCount = Math.max(maxFieldCount, fields.length);
      notes.push({ id, fields, tags });
    }
  }

  db.close();

  if (notes.length === 0) {
    throw new Error('El mazo no tiene notas (¿archivo vacío o corrupto?).');
  }

  for (let i = fieldNames.length; i < maxFieldCount; i++) {
    fieldNames.push(`Campo ${i + 1}`);
  }

  return { fieldNames, notes };
}

/**
 * Convierte notas ya parseadas al formato interno de vocabulario de la app,
 * usando los índices de campo que el usuario eligió para alemán/español en
 * el preview. Notas sin ambos campos completos se descartan.
 */
export function notesToVocabEntries(notes, { deFieldIndex, esFieldIndex, categoria, nivel, idPrefix }) {
  const entries = [];
  const seenIds = new Set();

  for (const note of notes) {
    const de = stripHtml(note.fields[deFieldIndex] || '').trim();
    const es = stripHtml(note.fields[esFieldIndex] || '').trim();
    if (!de || !es) continue;

    const baseId = `${idPrefix}${slugify(de)}`;
    let id = baseId;
    let n = 1;
    while (seenIds.has(id)) {
      n++;
      id = `${baseId}-${n}`;
    }
    seenIds.add(id);

    entries.push({
      id,
      de,
      es,
      en: '',
      categoria: categoria || 'Importado (Anki)',
      nivel: nivel || 'A1',
      ejemplo_de: '',
      ejemplo_es: '',
      tipo: 'importado',
      articulo: '',
    });
  }

  return entries;
}

function stripHtml(text) {
  const div = document.createElement('div');
  div.innerHTML = text;
  return div.textContent || div.innerText || '';
}

function slugify(text) {
  return (
    text
      .normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '') || 'entry'
  );
}
