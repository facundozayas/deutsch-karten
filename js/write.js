// Lógica pura del modo "Escribir la palabra" (producción activa, sin DOM).
// El usuario tipea la respuesta en alemán y la comparamos contra la
// respuesta correcta con una normalización tolerante — no es un auto-grade
// para FSRS (eso lo decide el usuario con los botones de calificación de
// siempre), es solo para mostrarle un ✅/❌ y no ser innecesariamente
// estricto con mayúsculas, espacios, puntuación final o diéresis tipeadas
// como ae/oe/ue/ss (común en teclados sin ä/ö/ü/ß).

const UMLAUT_ALTERNATIVES = [
  ['ä', 'ae'],
  ['ö', 'oe'],
  ['ü', 'ue'],
  ['ß', 'ss'],
];

/**
 * Normaliza un texto para comparación: minúsculas, sin espacios de más,
 * sin puntuación final, y con las variantes ae/oe/ue/ss convertidas a sus
 * diéresis reales para que ambas formas de tipeo cuenten como iguales.
 */
export function normalizeAnswer(text) {
  if (!text) return '';
  let normalized = text
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .replace(/[.,;:!?¡¿]+$/g, '')
    .trim();

  for (const [umlaut, alt] of UMLAUT_ALTERNATIVES) {
    normalized = normalized.split(alt).join(umlaut);
  }

  return normalized;
}

/**
 * Compara la respuesta del usuario contra la correcta, ya normalizadas.
 * @returns {{ correct: boolean, normalizedInput: string, normalizedCorrect: string }}
 */
export function checkAnswer(userInput, correctAnswer) {
  const normalizedInput = normalizeAnswer(userInput);
  const normalizedCorrect = normalizeAnswer(correctAnswer);
  return {
    correct: normalizedInput.length > 0 && normalizedInput === normalizedCorrect,
    normalizedInput,
    normalizedCorrect,
  };
}
