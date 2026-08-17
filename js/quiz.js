// Lógica pura del modo Quiz (sin DOM). Arma preguntas de opción múltiple a
// partir del vocabulario: 1 respuesta correcta + 3 distractores, preferentemente
// de la misma categoría para que sea un desafío real (si no hay suficientes
// en la categoría, completa con vocabulario de cualquier categoría).

/**
 * @param {object} vocabEntry - entrada de vocabulario a preguntar
 * @param {object[]} allVocab - pool completo de vocabulario disponible
 * @param {'de-es'|'es-de'} direction
 * @returns {{ promptText: string, options: {id:string, text:string}[], correctId: string, direction: string, vocabEntry: object }}
 */
export function buildQuestion(vocabEntry, allVocab, direction) {
  const sameCategory = allVocab.filter(
    (v) => v.id !== vocabEntry.id && v.categoria === vocabEntry.categoria
  );
  const pool = sameCategory.length >= 3
    ? sameCategory
    : allVocab.filter((v) => v.id !== vocabEntry.id);

  const distractors = pickRandom(pool, Math.min(3, pool.length));
  const answerField = direction === 'de-es' ? 'es' : 'de';
  const promptField = direction === 'de-es' ? 'de' : 'es';

  const candidates = shuffle([vocabEntry, ...distractors]);
  const options = candidates.map((v) => ({
    id: v.id,
    text: capitalize(v[answerField]),
  }));

  return {
    promptText: promptField === 'es' ? capitalize(vocabEntry[promptField]) : vocabEntry[promptField],
    options,
    correctId: vocabEntry.id,
    direction,
    vocabEntry,
  };
}

function pickRandom(array, n) {
  return shuffle(array).slice(0, n);
}

function shuffle(array) {
  const copy = [...array];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function capitalize(text) {
  if (!text) return text;
  return text.charAt(0).toUpperCase() + text.slice(1);
}
