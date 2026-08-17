// Lógica del sistema de niveles (A1 → A2 → B1 → B2). Sin DOM: recibe datos
// planos (vocab, cardStates) y devuelve decisiones/datos, la UI vive en app.js.
import { State } from './fsrs.js';
import { buildQuestion } from './quiz.js';

export const LEVEL_ORDER = ['A1', 'A2', 'B1', 'B2'];

// Umbral estilo Anki: intervalo de 21+ días = tarjeta "madura".
const MATURE_MIN_SCHEDULED_DAYS = 21;
// % de tarjetas maduras del nivel actual para sugerir pasar al siguiente.
export const MASTERY_SUGGEST_THRESHOLD = 0.8;
// % de aciertos en el test de diagnóstico para aprobarlo.
export const DIAGNOSTIC_PASS_THRESHOLD = 0.85;
export const DIAGNOSTIC_QUESTION_COUNT = 15;
// Días que se silencia el banner de sugerencia después de "Ahora no".
const BANNER_SNOOZE_DAYS = 7;

/**
 * Próximo nivel bloqueado según el orden fijo A1→A2→B1→B2, o null si ya
 * están todos desbloqueados.
 */
export function nextLockedLevel(unlockedLevels) {
  return LEVEL_ORDER.find((lvl) => !unlockedLevels.includes(lvl)) || null;
}

/**
 * Un nivel se puede desbloquear manualmente solo si es el próximo en la
 * secuencia (no se puede saltar de A1 a B1 sin pasar por A2).
 */
export function canUnlock(level, unlockedLevels) {
  return nextLockedLevel(unlockedLevels) === level;
}

/**
 * % de tarjetas "maduras" (repaso con intervalo largo) dentro de un conjunto
 * de cardStates — pensado para pasarle solo las tarjetas del nivel más alto
 * desbloqueado.
 */
export function computeMastery(cardStatesForLevel) {
  const total = cardStatesForLevel.length;
  if (total === 0) return { total: 0, matureCount: 0, ratio: 0 };
  const matureCount = cardStatesForLevel.filter(
    (c) => c.state === State.Review && c.scheduled_days >= MATURE_MIN_SCHEDULED_DAYS
  ).length;
  return { total, matureCount, ratio: matureCount / total };
}

/**
 * ¿Corresponde mostrar el banner de "ya dominás este nivel, ¿sumamos el
 * siguiente?"? Solo si hay un próximo nivel bloqueado, se superó el umbral
 * de dominio, y no está dentro del período de "silenciado" tras un "Ahora no".
 */
export function shouldShowLevelBanner({ unlockedLevels, mastery, dismissedUntilIso, now = new Date() }) {
  if (!nextLockedLevel(unlockedLevels)) return false;
  if (mastery.total < 10) return false; // muestra chica, todavía no es representativo
  if (mastery.ratio < MASTERY_SUGGEST_THRESHOLD) return false;
  if (dismissedUntilIso && new Date(dismissedUntilIso) > now) return false;
  return true;
}

export function snoozeBannerUntil(now = new Date()) {
  const d = new Date(now);
  d.setDate(d.getDate() + BANNER_SNOOZE_DAYS);
  return d.toISOString();
}

/**
 * Arma el test de diagnóstico: N preguntas de opción múltiple (reutiliza
 * quiz.js) muestreadas al azar del vocabulario del nivel dado, sin repetir
 * palabra, mezclando dirección alemán/español.
 */
export function buildDiagnosticQuestions(vocabForLevel, allVocab, n = DIAGNOSTIC_QUESTION_COUNT) {
  const sample = shuffle(vocabForLevel).slice(0, Math.min(n, vocabForLevel.length));
  return sample.map((entry) => {
    const direction = Math.random() < 0.5 ? 'de-es' : 'es-de';
    return buildQuestion(entry, allVocab, direction);
  });
}

export function scoreDiagnostic(answers) {
  // answers: [{ correct: boolean }]
  const total = answers.length;
  const correct = answers.filter((a) => a.correct).length;
  const ratio = total > 0 ? correct / total : 0;
  return { total, correct, ratio, passed: ratio >= DIAGNOSTIC_PASS_THRESHOLD };
}

function shuffle(array) {
  const copy = [...array];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}
