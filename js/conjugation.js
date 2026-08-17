// Lógica del drill de conjugación (presente). Sin DOM, sin FSRS — igual que
// articles.js, es un ejercicio focalizado e independiente de la cola de
// repaso diaria. Usa un dataset propio (data/conjugaciones.json), no el
// vocabulario general.

const PERSON_ORDER = ['ich', 'du', 'er_sie_es', 'wir', 'ihr', 'sie_Sie'];
const PERSON_LABELS = {
  ich: 'ich',
  du: 'du',
  er_sie_es: 'er / sie / es',
  wir: 'wir',
  ihr: 'ihr',
  sie_Sie: 'sie / Sie',
};

let cachedVerbs = null;
let loadPromise = null;

/**
 * Fetchea y cachea en memoria data/conjugaciones.json (una sola vez por
 * sesión de la página — mismo patrón que fetchVocabFile en app.js).
 */
export function loadConjugations() {
  if (cachedVerbs) return Promise.resolve(cachedVerbs);
  if (loadPromise) return loadPromise;

  loadPromise = fetch('./data/conjugaciones.json')
    .then((res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then((verbs) => {
      cachedVerbs = verbs;
      return verbs;
    })
    .catch((err) => {
      console.warn('No se pudo cargar data/conjugaciones.json', err);
      cachedVerbs = [];
      return cachedVerbs;
    });

  return loadPromise;
}

/**
 * Arma una pregunta de opción múltiple: elige un pronombre al azar para un
 * verbo, y arma hasta 3 distractores. Los distractores preferidos son OTRAS
 * personas del MISMO verbo (mejor pedagógicamente, porque obliga a
 * distinguir ich/du/er/wir/ihr/sie) — si el verbo no tiene suficientes
 * formas con texto distinto (pasa con algunos modales, ej. "kann" se repite
 * en ich y er), se completa con formas de otros verbos al azar.
 *
 * @param {object} verbEntry - { infinitivo, es, conjugacion: {ich, du, ...} }
 * @param {object[]} allVerbs - pool completo, para completar distractores si hace falta
 * @returns {{ promptText: string, contextText: string, options: {id:string,text:string}[], correctId: string, vocabEntry: object }}
 */
export function buildConjugationQuestion(verbEntry, allVerbs) {
  const person = PERSON_ORDER[Math.floor(Math.random() * PERSON_ORDER.length)];
  const correctForm = verbEntry.conjugacion[person];

  const usedTexts = new Set([correctForm]);
  const distractors = [];

  // 1) otras personas del mismo verbo, con texto distinto al correcto
  const sameVerbForms = shuffle(
    PERSON_ORDER.filter((p) => p !== person).map((p) => verbEntry.conjugacion[p])
  );
  for (const form of sameVerbForms) {
    if (distractors.length >= 3) break;
    if (!usedTexts.has(form)) {
      usedTexts.add(form);
      distractors.push(form);
    }
  }

  // 2) si no alcanzó, completar con formas de otros verbos al azar
  if (distractors.length < 3) {
    const otherVerbs = shuffle(allVerbs.filter((v) => v.infinitivo !== verbEntry.infinitivo));
    for (const other of otherVerbs) {
      if (distractors.length >= 3) break;
      const p = PERSON_ORDER[Math.floor(Math.random() * PERSON_ORDER.length)];
      const form = other.conjugacion[p];
      if (!usedTexts.has(form)) {
        usedTexts.add(form);
        distractors.push(form);
      }
    }
  }

  const options = shuffle([correctForm, ...distractors]).map((text) => ({ id: text, text }));

  return {
    promptText: PERSON_LABELS[person],
    contextText: verbEntry.infinitivo,
    options,
    correctId: correctForm,
    vocabEntry: verbEntry,
    person,
  };
}

export function buildConjugationQuestions(verbs, n = 15) {
  const sample = shuffle(verbs).slice(0, Math.min(n, verbs.length));
  return sample.map((verb) => buildConjugationQuestion(verb, verbs));
}

function shuffle(array) {
  const copy = [...array];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}
