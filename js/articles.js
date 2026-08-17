// Lógica pura del drill de artículos (der/die/das). Sin DOM, sin FSRS —
// es un ejercicio focalizado e independiente de la cola de repaso diaria
// (ver decisión de diseño en el plan de v3).

const ARTICLES = ['der', 'die', 'das'];

/**
 * Arma una pregunta de opción múltiple (3 opciones fijas: der/die/das) para
 * un sustantivo. La mayoría de vocab.de ya trae el artículo incluido (ej.
 * "das Haus"), pero algunas entradas (ej. los días de la semana) lo tienen
 * solo en el campo `articulo` y no en `de` — se contempla ambos casos.
 *
 * @param {object} nounEntry - entrada de vocabulario con tipo "sustantivo" y articulo
 * @returns {{ promptText: string, options: {id:string, text:string}[], correctId: string, vocabEntry: object }}
 */
export function buildArticleQuestion(nounEntry) {
  const articulo = nounEntry.articulo;
  const bareNoun = nounEntry.de.toLowerCase().startsWith(`${articulo.toLowerCase()} `)
    ? nounEntry.de.slice(articulo.length + 1)
    : nounEntry.de;

  const options = shuffle(ARTICLES).map((art) => ({ id: art, text: art }));

  return {
    promptText: bareNoun,
    options,
    correctId: articulo,
    vocabEntry: nounEntry,
  };
}

/**
 * Arma una tanda de N preguntas, muestreando sustantivos únicos (con
 * artículo) del pool de vocabulario dado.
 */
export function buildArticleQuestions(nouns, n = 15) {
  const eligible = nouns.filter((v) => v.tipo === 'sustantivo' && v.articulo);
  const sample = shuffle(eligible).slice(0, Math.min(n, eligible.length));
  return sample.map(buildArticleQuestion);
}

function shuffle(array) {
  const copy = [...array];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}
