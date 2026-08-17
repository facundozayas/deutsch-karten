// Wrapper sobre ts-fsrs. Esta es la única capa que importa la librería
// directamente — si alguna vez cambia la versión o la API, solo hay que
// tocar este archivo.
import {
  fsrs,
  generatorParameters,
  createEmptyCard,
  Rating,
  State,
} from './vendor/ts-fsrs.mjs';

export { Rating, State };

const params = generatorParameters({
  // request_retention default (0.9) está bien para arrancar; se puede
  // exponer como setting más adelante si hace falta ajustar el volumen
  // diario de repasos.
  enable_fuzz: true,
});

const scheduler = fsrs(params);

/**
 * Crea el estado FSRS inicial para una tarjeta nueva.
 * @param {Date} [now]
 * @returns {object} objeto "Card" de ts-fsrs (due, stability, difficulty, etc.)
 */
export function createNewCardState(now = new Date()) {
  return createEmptyCard(now);
}

/**
 * Calcula el próximo estado de una tarjeta dado el grado de recuerdo.
 * @param {object} cardState - estado FSRS actual de la tarjeta
 * @param {1|2|3|4} grade - Rating.Again=1, Hard=2, Good=3, Easy=4
 * @param {Date} [now]
 * @returns {{card: object, log: object}}
 */
export function scheduleReview(cardState, grade, now = new Date()) {
  const result = scheduler.next(cardState, now, grade);
  return result; // { card, log }
}

/**
 * ¿Esta tarjeta está vencida (due) a esta fecha?
 */
export function isDue(cardState, now = new Date()) {
  return new Date(cardState.due).getTime() <= now.getTime();
}

/**
 * Nombre legible en español del estado FSRS, para la pantalla de stats.
 */
export function stateLabel(state) {
  switch (state) {
    case State.New: return 'Nuevas';
    case State.Learning: return 'Aprendiendo';
    case State.Review: return 'En repaso';
    case State.Relearning: return 'Reaprendiendo';
    default: return 'Desconocido';
  }
}
