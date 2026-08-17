import * as storage from './storage.js';
import * as fsrsWrap from './fsrs.js';
import * as tts from './tts.js';
import * as levels from './levels.js';
import { buildQuestion } from './quiz.js';
import * as ankiImport from './anki-import.js';
import * as writeLogic from './write.js';
import * as articles from './articles.js';
import * as conjugation from './conjugation.js';

const { Rating, State, createNewCardState, scheduleReview, stateLabel } = fsrsWrap;

// Cuántas tarjetas NUEVAS (nunca vistas) se introducen por día como máximo.
// Con sesiones de 5-10 min, 10 tarjetas nuevas + los repasos que vayan
// venciendo es un ritmo razonable. Ajustable a futuro desde Ajustes.
const NEW_CARDS_PER_DAY = 10;

// ---------------------------------------------------------------------------
// Estado en memoria
// ---------------------------------------------------------------------------

let vocabById = new Map();
let allVocabArray = [];
let unlockedLevels = ['A1'];
let queue = [];        // [{ vocab, cardState }]
let queueIndex = 0;
let sessionReviewed = 0;
let currentDirection = 'de-es'; // 'de-es' | 'es-de'
let revealed = false;
let reviewMode = 'flashcards'; // 'flashcards' | 'quiz' | 'write'
let diagnosticState = null;
let ankiParsedDeck = null; // { fieldNames, notes } — resultado de anki-import.parseApkg
let audioOnlyMode = false; // toggle de Ajustes, solo afecta a Flashcards
let drillState = null; // { title, questions, index, correctCount, retryFn }

// ---------------------------------------------------------------------------
// Elementos del DOM
// ---------------------------------------------------------------------------

const el = (id) => document.getElementById(id);

const els = {
  dueCount: el('due-count'),
  viewTitle: el('view-title'),

  modeSwitch: el('mode-switch'),

  levelBanner: el('level-banner'),
  levelBannerText: el('level-banner-text'),
  levelBannerTest: el('level-banner-test'),
  levelBannerDismiss: el('level-banner-dismiss'),

  reviewEmpty: el('review-empty'),
  reviewLoading: el('review-loading'),
  reviewCardWrap: el('review-card-wrap'),
  sessionComplete: el('session-complete'),
  sessionSummary: el('session-summary'),
  btnReviewMore: el('btn-review-more'),

  progressFill: el('progress-fill'),
  cardCategory: el('card-category'),
  cardTerm: el('card-term'),
  btnListen: el('btn-listen'),
  btnListenBack: el('btn-listen-back'),
  btnReveal: el('btn-reveal'),
  cardBack: el('card-back'),
  cardAnswer: el('card-answer'),
  cardExtra: el('card-extra'),
  exampleDe: el('example-de'),
  exampleEs: el('example-es'),
  gradeButtons: el('grade-buttons'),

  quizCardWrap: el('quiz-card-wrap'),
  quizProgressFill: el('quiz-progress-fill'),
  quizCategory: el('quiz-category'),
  quizTerm: el('quiz-term'),
  quizBtnListen: el('quiz-btn-listen'),
  quizOptions: el('quiz-options'),

  writeCardWrap: el('write-card-wrap'),
  writeProgressFill: el('write-progress-fill'),
  writeCategory: el('write-category'),
  writeTerm: el('write-term'),
  writeForm: el('write-form'),
  writeInput: el('write-input'),
  writeFeedback: el('write-feedback'),
  writeFeedbackStatus: el('write-feedback-status'),
  writeAnswer: el('write-answer'),
  writeBtnListen: el('write-btn-listen'),
  writeExampleDe: el('write-example-de'),
  writeExampleEs: el('write-example-es'),
  writeGradeButtons: el('write-grade-buttons'),

  toggleAudioOnly: el('toggle-audio-only'),
  btnDrillArticles: el('btn-drill-articles'),
  btnDrillConjugation: el('btn-drill-conjugation'),

  drillModal: el('drill-modal'),
  drillRunning: el('drill-running'),
  drillResult: el('drill-result'),
  drillTitle: el('drill-title'),
  drillProgress: el('drill-progress'),
  drillContext: el('drill-context'),
  drillTerm: el('drill-term'),
  drillOptions: el('drill-options'),
  drillResultTitle: el('drill-result-title'),
  drillResultText: el('drill-result-text'),
  drillRetryBtn: el('drill-retry-btn'),
  drillCloseBtn: el('drill-close-btn'),

  statToday: el('stat-today'),
  statStreak: el('stat-streak'),
  statRetention: el('stat-retention'),
  statTotal: el('stat-total'),
  stateBreakdown: el('state-breakdown'),

  toggleDark: el('toggle-dark'),
  btnExport: el('btn-export'),
  importFile: el('import-file'),
  backupStatus: el('backup-status'),

  levelsList: el('levels-list'),

  diagnosticModal: el('diagnostic-modal'),
  diagnosticRunning: el('diagnostic-running'),
  diagnosticResult: el('diagnostic-result'),
  diagnosticProgress: el('diagnostic-progress'),
  diagnosticTerm: el('diagnostic-term'),
  diagnosticOptions: el('diagnostic-options'),
  diagnosticResultTitle: el('diagnostic-result-title'),
  diagnosticResultText: el('diagnostic-result-text'),
  diagnosticUnlockBtn: el('diagnostic-unlock-btn'),
  diagnosticCloseBtn: el('diagnostic-close-btn'),

  ankiFile: el('anki-file'),
  ankiStatus: el('anki-status'),
  ankiModal: el('anki-modal'),
  ankiModalLoading: el('anki-modal-loading'),
  ankiModalPreview: el('anki-modal-preview'),
  ankiPreviewSummary: el('anki-preview-summary'),
  ankiFieldDe: el('anki-field-de'),
  ankiFieldEs: el('anki-field-es'),
  ankiCategoria: el('anki-categoria'),
  ankiNivel: el('anki-nivel'),
  ankiPreviewTable: el('anki-preview-table'),
  ankiConfirmBtn: el('anki-confirm-btn'),
  ankiCancelBtn: el('anki-cancel-btn'),

  onboarding: el('onboarding'),
  onboardingOk: el('onboarding-ok'),

  toast: el('toast'),
  tabbar: el('tabbar'),
};

const STATE_COLORS = { 0: '#6c8cff', 1: '#e0a13d', 2: '#3fb27f', 3: '#e5555a' };

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------

async function boot() {
  registerServiceWorker();
  applyStoredTheme();
  wireStaticUI();

  try {
    unlockedLevels = await storage.getUnlockedLevels();
    audioOnlyMode = await storage.getMeta('audioOnlyMode', false);
    if (els.toggleAudioOnly) els.toggleAudioOnly.checked = audioOnlyMode;
    await loadVocabAndInit();
    await maybeShowOnboarding();
    await loadQueue();
    renderCurrent();
    await refreshDueCount();
    renderLevelsSettings();
    await refreshLevelBanner();
  } catch (err) {
    console.error('Error al iniciar la app', err);
    els.reviewLoading.classList.add('hidden');
    els.reviewEmpty.classList.remove('hidden');
    els.reviewEmpty.querySelector('p').textContent = 'Ups, hubo un problema cargando el contenido. Probá recargar.';
  }
}

function registerServiceWorker() {
  if (!('serviceWorker' in navigator)) return;
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./service-worker.js').catch((err) => {
      console.warn('No se pudo registrar el service worker', err);
    });
  });

  // iOS no revisa el SW en background: forzamos un chequeo al volver a foco.
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      navigator.serviceWorker.getRegistration().then((reg) => reg && reg.update());
    }
  });
}

async function fetchVocabFile(path) {
  try {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    // Un nivel sin contenido todavía (ej. B1/B2 antes de generarse) no debe
    // tirar abajo el boot entero de la app.
    console.warn(`No se pudo cargar ${path}`, err);
    return [];
  }
}

/**
 * Reconstruye vocabById a partir de los niveles desbloqueados + el
 * vocabulario personalizado (importado de Anki / agregado a mano), e
 * inicializa el estado FSRS de cualquier tarjeta nueva. Se llama en el boot
 * y cada vez que cambia el set de niveles o se importa contenido nuevo.
 */
async function loadVocabAndInit() {
  vocabById = new Map();

  for (const level of unlockedLevels) {
    const vocab = await fetchVocabFile(`./data/vocab-${level.toLowerCase()}.json`);
    vocab.forEach((entry) => vocabById.set(entry.id, entry));
  }

  const custom = await storage.getAllCustomVocab();
  custom.forEach((entry) => vocabById.set(entry.id, entry));

  allVocabArray = Array.from(vocabById.values());
  await storage.bulkInitCardStates(allVocabArray, createNewCardState);
}

async function maybeShowOnboarding() {
  const seen = await storage.getMeta('onboardingSeen', false);
  if (!seen) {
    els.onboarding.classList.remove('hidden');
  }
}

// ---------------------------------------------------------------------------
// Cola de repaso diaria
// ---------------------------------------------------------------------------

async function loadQueue() {
  els.reviewLoading.classList.remove('hidden');
  els.reviewCardWrap.classList.add('hidden');
  els.quizCardWrap.classList.add('hidden');
  els.reviewEmpty.classList.add('hidden');
  els.sessionComplete.classList.add('hidden');

  const now = new Date();
  const dueStates = await storage.getDueCards(now);

  const dueNonNew = [];
  const dueNew = [];
  for (const cardState of dueStates) {
    const vocab = vocabById.get(cardState.id);
    if (!vocab) continue; // tarjeta huérfana (contenido cambió), la ignoramos
    if (cardState.state === State.New) dueNew.push({ vocab, cardState });
    else dueNonNew.push({ vocab, cardState });
  }

  dueNonNew.sort((a, b) => a.cardState.due - b.cardState.due);

  const remainingNewBudget = await getRemainingNewBudget();
  const selectedNew = dueNew.slice(0, Math.max(0, remainingNewBudget));

  queue = [...dueNonNew, ...selectedNew];
  queueIndex = 0;
  sessionReviewed = 0;

  els.reviewLoading.classList.add('hidden');
}

async function getRemainingNewBudget() {
  const today = todayStr();
  const storedDate = await storage.getMeta('newIntroducedDate', null);
  let count = await storage.getMeta('newIntroducedCount', 0);
  if (storedDate !== today) {
    count = 0;
    await storage.setMeta('newIntroducedDate', today);
    await storage.setMeta('newIntroducedCount', 0);
  }
  return NEW_CARDS_PER_DAY - count;
}

async function registerNewCardIntroduced() {
  const today = todayStr();
  const storedDate = await storage.getMeta('newIntroducedDate', today);
  let count = await storage.getMeta('newIntroducedCount', 0);
  if (storedDate !== today) count = 0;
  await storage.setMeta('newIntroducedDate', today);
  await storage.setMeta('newIntroducedCount', count + 1);
}

function todayStr() {
  return new Date().toDateString();
}

async function refreshDueCount() {
  const now = new Date();
  const due = await storage.getDueCards(now);
  els.dueCount.textContent = due.length > 0 ? `${due.length} pendientes` : '';
}

// ---------------------------------------------------------------------------
// Grading compartido (flashcards y quiz alimentan el mismo pipeline FSRS)
// ---------------------------------------------------------------------------

async function recordReview(grade) {
  const { vocab, cardState } = queue[queueIndex];
  const wasNew = cardState.state === State.New;

  const { card: nextCard, log } = scheduleReview(cardState, grade, new Date());
  await storage.saveReview(vocab.id, nextCard, log);

  if (wasNew) await registerNewCardIntroduced();

  sessionReviewed++;
  queueIndex++;
}

function renderCurrent() {
  if (reviewMode === 'quiz') renderQuiz();
  else if (reviewMode === 'write') renderWrite();
  else renderFlashcard();
}

// ---------------------------------------------------------------------------
// Render: modo Flashcards
// ---------------------------------------------------------------------------

function renderFlashcard() {
  if (queueIndex >= queue.length) {
    showSessionComplete();
    return;
  }

  els.sessionComplete.classList.add('hidden');
  els.reviewEmpty.classList.add('hidden');
  els.quizCardWrap.classList.add('hidden');
  els.writeCardWrap.classList.add('hidden');
  els.reviewCardWrap.classList.remove('hidden');

  const { vocab } = queue[queueIndex];
  revealed = false;
  currentDirection = audioOnlyMode ? 'de-es' : (Math.random() < 0.5 ? 'de-es' : 'es-de');

  els.progressFill.style.width = `${Math.round((queueIndex / queue.length) * 100)}%`;
  els.cardCategory.textContent = vocab.categoria;

  const germanTerm = formatGerman(vocab);

  if (currentDirection === 'de-es') {
    if (audioOnlyMode) {
      els.cardTerm.textContent = '🔊 Escuchá y pensá la traducción';
      tts.speak(vocab.de); // best-effort: si el navegador bloquea el autoplay, el botón de abajo es el fallback
    } else {
      els.cardTerm.textContent = germanTerm;
    }
    els.btnListen.classList.remove('hidden');
    els.btnListen.onclick = () => tts.speak(vocab.de);
  } else {
    els.cardTerm.textContent = capitalize(vocab.es);
    els.btnListen.classList.add('hidden');
  }

  els.cardBack.classList.add('hidden');
  els.btnReveal.classList.remove('hidden');
  els.gradeButtons.classList.add('hidden');
}

function formatGerman(vocab) {
  return vocab.de; // el artículo ya viene incluido en "de" cuando corresponde (ej. "das Haus")
}

function capitalize(text) {
  if (!text) return text;
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function revealCard() {
  if (revealed) return;
  revealed = true;
  const { vocab } = queue[queueIndex];

  if (currentDirection === 'de-es') {
    if (audioOnlyMode) els.cardTerm.textContent = formatGerman(vocab); // ya no hace falta ocultarlo
    els.cardAnswer.textContent = capitalize(vocab.es);
    els.cardExtra.textContent = vocab.en ? `English: ${vocab.en}` : '';
    els.btnListenBack.classList.add('hidden');
  } else {
    els.cardAnswer.textContent = formatGerman(vocab);
    els.cardExtra.textContent = vocab.en ? `English: ${vocab.en}` : '';
    els.btnListenBack.classList.remove('hidden');
    els.btnListenBack.onclick = () => tts.speak(vocab.de);
  }

  els.exampleDe.textContent = vocab.ejemplo_de || '';
  els.exampleEs.textContent = vocab.ejemplo_es || '';

  els.cardBack.classList.remove('hidden');
  els.btnReveal.classList.add('hidden');
  els.gradeButtons.classList.remove('hidden');
}

async function gradeCard(grade) {
  await recordReview(grade);
  renderCurrent();
  refreshDueCount();
  refreshLevelBanner();
}

function showSessionComplete() {
  els.reviewCardWrap.classList.add('hidden');
  els.quizCardWrap.classList.add('hidden');
  els.writeCardWrap.classList.add('hidden');
  els.sessionComplete.classList.remove('hidden');
  els.sessionSummary.textContent = sessionReviewed > 0
    ? `¡Repasaste ${sessionReviewed} tarjeta${sessionReviewed === 1 ? '' : 's'}! 🎉`
    : 'No hay tarjetas pendientes por ahora.';
}

// ---------------------------------------------------------------------------
// Render: modo Quiz (opción múltiple, alimenta el mismo FSRS)
// ---------------------------------------------------------------------------

function renderQuiz() {
  if (queueIndex >= queue.length) {
    showSessionComplete();
    return;
  }

  els.sessionComplete.classList.add('hidden');
  els.reviewEmpty.classList.add('hidden');
  els.reviewCardWrap.classList.add('hidden');
  els.writeCardWrap.classList.add('hidden');
  els.quizCardWrap.classList.remove('hidden');

  const { vocab } = queue[queueIndex];
  const direction = Math.random() < 0.5 ? 'de-es' : 'es-de';
  const question = buildQuestion(vocab, allVocabArray, direction);

  els.quizProgressFill.style.width = `${Math.round((queueIndex / queue.length) * 100)}%`;
  els.quizCategory.textContent = vocab.categoria;
  els.quizTerm.textContent = question.promptText;

  if (direction === 'de-es') {
    els.quizBtnListen.classList.remove('hidden');
    els.quizBtnListen.onclick = () => tts.speak(vocab.de);
  } else {
    els.quizBtnListen.classList.add('hidden');
  }

  els.quizOptions.innerHTML = '';
  question.options.forEach((opt) => {
    const btn = document.createElement('button');
    btn.className = 'quiz-option';
    btn.textContent = opt.text;
    btn.dataset.id = opt.id;
    els.quizOptions.appendChild(btn);
  });

  els.quizOptions.onclick = (e) => {
    const btn = e.target.closest('.quiz-option');
    if (!btn || btn.disabled) return;
    handleQuizAnswer(btn, question);
  };
}

async function handleQuizAnswer(selectedBtn, question) {
  const correct = selectedBtn.dataset.id === question.correctId;

  [...els.quizOptions.children].forEach((btn) => {
    btn.disabled = true;
    if (btn.dataset.id === question.correctId) btn.classList.add('correct');
    else if (btn === selectedBtn) btn.classList.add('incorrect');
  });

  await new Promise((resolve) => setTimeout(resolve, 600));
  await recordReview(correct ? Rating.Good : Rating.Again);
  renderCurrent();
  refreshDueCount();
  refreshLevelBanner();
}

// ---------------------------------------------------------------------------
// Render: modo Escribir (producción activa, español→alemán, alimenta FSRS)
// ---------------------------------------------------------------------------

function renderWrite() {
  if (queueIndex >= queue.length) {
    showSessionComplete();
    return;
  }

  els.sessionComplete.classList.add('hidden');
  els.reviewEmpty.classList.add('hidden');
  els.reviewCardWrap.classList.add('hidden');
  els.quizCardWrap.classList.add('hidden');
  els.writeCardWrap.classList.remove('hidden');

  const { vocab } = queue[queueIndex];

  els.writeProgressFill.style.width = `${Math.round((queueIndex / queue.length) * 100)}%`;
  els.writeCategory.textContent = vocab.categoria;
  els.writeTerm.textContent = capitalize(vocab.es);

  els.writeInput.value = '';
  els.writeInput.disabled = false;
  els.writeFeedback.classList.add('hidden');
  els.writeGradeButtons.classList.add('hidden');
  els.writeForm.classList.remove('hidden');
  els.writeInput.focus();
}

function handleWriteCheck() {
  if (queueIndex >= queue.length) return;
  const { vocab } = queue[queueIndex];
  const correctAnswer = formatGerman(vocab);
  const result = writeLogic.checkAnswer(els.writeInput.value, correctAnswer);

  els.writeInput.disabled = true;
  els.writeForm.classList.add('hidden');

  els.writeFeedbackStatus.textContent = result.correct ? '✅ ¡Correcto!' : '❌ Casi — fijate la diferencia';
  els.writeFeedbackStatus.className = `write-feedback-status ${result.correct ? 'correct' : 'incorrect'}`;
  els.writeAnswer.textContent = correctAnswer;
  els.writeBtnListen.onclick = () => tts.speak(vocab.de);
  els.writeExampleDe.textContent = vocab.ejemplo_de || '';
  els.writeExampleEs.textContent = vocab.ejemplo_es || '';

  els.writeFeedback.classList.remove('hidden');
  els.writeGradeButtons.classList.remove('hidden');
}

// ---------------------------------------------------------------------------
// Render: vista Estadísticas
// ---------------------------------------------------------------------------

async function renderStats() {
  const snapshot = await storage.getStatsSnapshot();

  els.statToday.textContent = snapshot.reviewedToday;
  els.statStreak.textContent = snapshot.streak;
  els.statRetention.textContent = snapshot.retention === null ? '–' : `${snapshot.retention}%`;
  els.statTotal.textContent = snapshot.total;

  els.stateBreakdown.innerHTML = '';
  [State.New, State.Learning, State.Review, State.Relearning].forEach((s) => {
    const row = document.createElement('div');
    row.className = 'state-row';
    row.innerHTML = `
      <span><span class="state-dot" style="background:${STATE_COLORS[s]}"></span>${stateLabel(s)}</span>
      <strong>${snapshot.counts[s] || 0}</strong>
    `;
    els.stateBreakdown.appendChild(row);
  });
}

// ---------------------------------------------------------------------------
// Sistema de niveles
// ---------------------------------------------------------------------------

function currentMaxLevel() {
  return levels.LEVEL_ORDER.filter((lvl) => unlockedLevels.includes(lvl)).slice(-1)[0];
}

function renderLevelsSettings() {
  els.levelsList.innerHTML = '';
  levels.LEVEL_ORDER.forEach((lvl) => {
    const isUnlocked = unlockedLevels.includes(lvl);
    const canUnlockNow = levels.canUnlock(lvl, unlockedLevels);

    let statusText = '';
    let actionsHtml = '';

    if (isUnlocked) {
      statusText = lvl === 'A1' ? 'Activo' : 'Activo ✅';
    } else if (canUnlockNow) {
      statusText = 'Podés activarlo cuando quieras';
      actionsHtml = `
        <button class="btn btn-secondary" data-action="test" data-level="${lvl}">Test</button>
        <button class="btn btn-primary" data-action="unlock" data-level="${lvl}">Desbloquear</button>
      `;
    } else {
      const prevIdx = levels.LEVEL_ORDER.indexOf(lvl) - 1;
      const prevLevel = levels.LEVEL_ORDER[prevIdx];
      statusText = `Bloqueado (activá ${prevLevel} primero)`;
    }

    const row = document.createElement('div');
    row.className = 'level-row';
    row.innerHTML = `
      <div class="level-row-info">
        <div class="level-row-name">${lvl}</div>
        <div class="level-row-status">${statusText}</div>
      </div>
      <div class="level-row-actions">${actionsHtml}</div>
    `;
    els.levelsList.appendChild(row);
  });
}

async function unlockLevel(level) {
  if (!levels.canUnlock(level, unlockedLevels)) return;
  unlockedLevels = [...unlockedLevels, level];
  await storage.setUnlockedLevels(unlockedLevels);
  await storage.setMeta('levelBannerDismissedUntil', null);
  showToast(`¡Nivel ${level} desbloqueado! 🎉`);

  await loadVocabAndInit();
  await loadQueue();
  renderCurrent();
  await refreshDueCount();
  renderLevelsSettings();
  await refreshLevelBanner();
}

async function refreshLevelBanner() {
  const maxLevel = currentMaxLevel();
  const next = levels.nextLockedLevel(unlockedLevels);
  if (!next) {
    els.levelBanner.classList.add('hidden');
    return;
  }

  const vocabIdsForMaxLevel = new Set(
    allVocabArray.filter((v) => v.nivel === maxLevel).map((v) => v.id)
  );
  const allCardStates = await storage.getAllCardStates();
  const cardStatesForLevel = allCardStates.filter((c) => vocabIdsForMaxLevel.has(c.id));
  const mastery = levels.computeMastery(cardStatesForLevel);

  const dismissedUntil = await storage.getMeta('levelBannerDismissedUntil', null);
  const show = levels.shouldShowLevelBanner({ unlockedLevels, mastery, dismissedUntilIso: dismissedUntil });

  if (show) {
    els.levelBannerText.textContent = `Ya dominás la mayoría de ${maxLevel} (${Math.round(mastery.ratio * 100)}%). ¿Querés sumar ${next}?`;
    els.levelBanner.dataset.nextLevel = next;
    els.levelBanner.classList.remove('hidden');
  } else {
    els.levelBanner.classList.add('hidden');
  }
}

// ---- Test de diagnóstico ----

// El nivel evaluado por el diagnóstico todavía no está desbloqueado, así que
// su vocabulario no forma parte de allVocabArray (eso solo trae los niveles
// ya activos + vocabulario personalizado). Lo pedimos aparte, sin mergearlo
// permanentemente hasta que el usuario efectivamente desbloquee el nivel.
async function openDiagnosticModal(level) {
  let vocabForLevel = allVocabArray.filter((v) => v.nivel === level);

  if (vocabForLevel.length === 0) {
    vocabForLevel = await fetchVocabFile(`./data/vocab-${level.toLowerCase()}.json`);
  }

  if (vocabForLevel.length === 0) {
    showToast(`Todavía no hay contenido cargado para ${level}.`);
    return;
  }

  const questions = levels.buildDiagnosticQuestions(vocabForLevel, vocabForLevel, levels.DIAGNOSTIC_QUESTION_COUNT);
  diagnosticState = { level, questions, index: 0, answers: [] };

  els.diagnosticModal.classList.remove('hidden');
  els.diagnosticRunning.classList.remove('hidden');
  els.diagnosticResult.classList.add('hidden');
  renderDiagnosticQuestion();
}

function renderDiagnosticQuestion() {
  const { questions, index } = diagnosticState;
  const q = questions[index];

  els.diagnosticProgress.style.width = `${Math.round((index / questions.length) * 100)}%`;
  els.diagnosticTerm.textContent = q.promptText;

  els.diagnosticOptions.innerHTML = '';
  q.options.forEach((opt) => {
    const btn = document.createElement('button');
    btn.className = 'quiz-option';
    btn.textContent = opt.text;
    btn.dataset.id = opt.id;
    els.diagnosticOptions.appendChild(btn);
  });
}

function handleDiagnosticAnswer(selectedBtn) {
  const q = diagnosticState.questions[diagnosticState.index];
  const correct = selectedBtn.dataset.id === q.correctId;
  diagnosticState.answers.push({ correct });

  [...els.diagnosticOptions.children].forEach((btn) => {
    btn.disabled = true;
    if (btn.dataset.id === q.correctId) btn.classList.add('correct');
    else if (btn === selectedBtn) btn.classList.add('incorrect');
  });

  setTimeout(() => {
    diagnosticState.index++;
    if (diagnosticState.index >= diagnosticState.questions.length) {
      finishDiagnostic();
    } else {
      renderDiagnosticQuestion();
    }
  }, 600);
}

function finishDiagnostic() {
  const score = levels.scoreDiagnostic(diagnosticState.answers);
  const pct = Math.round(score.ratio * 100);

  els.diagnosticRunning.classList.add('hidden');
  els.diagnosticResult.classList.remove('hidden');

  if (score.passed) {
    els.diagnosticResultTitle.textContent = '¡Aprobado! 🎉';
    els.diagnosticResultText.textContent = `Acertaste ${score.correct}/${score.total} (${pct}%). Ya podés pasar a ${diagnosticState.level}.`;
    els.diagnosticUnlockBtn.classList.remove('hidden');
    els.diagnosticUnlockBtn.onclick = async () => {
      await unlockLevel(diagnosticState.level);
      els.diagnosticModal.classList.add('hidden');
    };
  } else {
    const passPct = Math.round(levels.DIAGNOSTIC_PASS_THRESHOLD * 100);
    els.diagnosticResultTitle.textContent = 'Todavía no';
    els.diagnosticResultText.textContent = `Acertaste ${score.correct}/${score.total} (${pct}%). Necesitás al menos ${passPct}% para pasar a ${diagnosticState.level}. ¡Seguí practicando!`;
    els.diagnosticUnlockBtn.classList.add('hidden');
  }
}

// ---------------------------------------------------------------------------
// Drills independientes (artículos der/die/das, conjugaciones) — NO tocan
// FSRS ni reviewLog, son ejercicios focalizados aparte de la cola diaria.
// ---------------------------------------------------------------------------

function runDrill(title, questions, retryFn) {
  if (questions.length === 0) {
    showToast('No hay suficiente contenido todavía para este ejercicio.');
    return;
  }

  drillState = { title, questions, index: 0, correctCount: 0, retryFn };

  els.drillTitle.textContent = title;
  els.drillModal.classList.remove('hidden');
  els.drillRunning.classList.remove('hidden');
  els.drillResult.classList.add('hidden');
  renderDrillQuestion();
}

function renderDrillQuestion() {
  const { questions, index } = drillState;
  const q = questions[index];

  els.drillProgress.style.width = `${Math.round((index / questions.length) * 100)}%`;
  els.drillContext.textContent = q.contextText || '';
  els.drillTerm.textContent = q.promptText;

  els.drillOptions.innerHTML = '';
  q.options.forEach((opt) => {
    const btn = document.createElement('button');
    btn.className = 'quiz-option';
    btn.textContent = opt.text;
    btn.dataset.id = opt.id;
    els.drillOptions.appendChild(btn);
  });
}

function handleDrillAnswer(selectedBtn) {
  const q = drillState.questions[drillState.index];
  const correct = selectedBtn.dataset.id === q.correctId;
  if (correct) drillState.correctCount++;

  [...els.drillOptions.children].forEach((btn) => {
    btn.disabled = true;
    if (btn.dataset.id === q.correctId) btn.classList.add('correct');
    else if (btn === selectedBtn) btn.classList.add('incorrect');
  });

  setTimeout(() => {
    drillState.index++;
    if (drillState.index >= drillState.questions.length) {
      finishDrill();
    } else {
      renderDrillQuestion();
    }
  }, 600);
}

function finishDrill() {
  const { questions, correctCount, retryFn } = drillState;
  const pct = Math.round((correctCount / questions.length) * 100);

  els.drillRunning.classList.add('hidden');
  els.drillResult.classList.remove('hidden');
  els.drillResultTitle.textContent = pct >= 70 ? '¡Bien ahí! 💪' : 'Seguí practicando';
  els.drillResultText.textContent = `Acertaste ${correctCount}/${questions.length} (${pct}%). Esto no afecta tus estadísticas de repaso.`;
  els.drillRetryBtn.onclick = retryFn;
}

function openArticlesDrill() {
  const nouns = allVocabArray.filter((v) => v.tipo === 'sustantivo' && v.articulo);
  const start = () => runDrill('Artículos: der / die / das', articles.buildArticleQuestions(nouns, 15), start);
  start();
}

async function openConjugationDrill() {
  const verbs = await conjugation.loadConjugations();
  const start = () => runDrill('Conjugación (presente)', conjugation.buildConjugationQuestions(verbs, 15), start);
  start();
}

// ---------------------------------------------------------------------------
// Import de mazos Anki (.apkg)
// ---------------------------------------------------------------------------

async function handleAnkiFileSelected(file) {
  els.ankiStatus.textContent = '';
  els.ankiModal.classList.remove('hidden');
  els.ankiModalLoading.classList.remove('hidden');
  els.ankiModalPreview.classList.add('hidden');
  els.ankiModalLoading.textContent = 'Procesando archivo…';

  try {
    ankiParsedDeck = await ankiImport.parseApkg(file);
    renderAnkiPreview();
  } catch (err) {
    console.error(err);
    els.ankiModal.classList.add('hidden');
    showToast('No se pudo leer el mazo ❌');
    els.ankiStatus.textContent = err.message || 'Error desconocido al procesar el archivo.';
  }
}

function renderAnkiPreview() {
  const { fieldNames, notes } = ankiParsedDeck;

  els.ankiModalLoading.classList.add('hidden');
  els.ankiModalPreview.classList.remove('hidden');

  els.ankiPreviewSummary.textContent = `${notes.length} notas encontradas, ${fieldNames.length} campos por nota.`;

  els.ankiFieldDe.innerHTML = fieldNames.map((name, i) => `<option value="${i}">${name}</option>`).join('');
  els.ankiFieldEs.innerHTML = fieldNames.map((name, i) => `<option value="${i}">${name}</option>`).join('');
  els.ankiFieldDe.value = '0';
  els.ankiFieldEs.value = fieldNames.length > 1 ? '1' : '0';

  els.ankiNivel.innerHTML = levels.LEVEL_ORDER
    .filter((lvl) => unlockedLevels.includes(lvl))
    .map((lvl) => `<option value="${lvl}">${lvl}</option>`)
    .join('');
  els.ankiNivel.value = currentMaxLevel();

  els.ankiPreviewTable.innerHTML = notes
    .slice(0, 8)
    .map((note) => `<div class="anki-preview-row">${note.fields.map((f) => stripHtmlPreview(f)).join(' · ')}</div>`)
    .join('');
}

function stripHtmlPreview(text) {
  const div = document.createElement('div');
  div.innerHTML = text;
  return (div.textContent || div.innerText || '').slice(0, 40);
}

async function confirmAnkiImport() {
  if (!ankiParsedDeck) return;

  const deFieldIndex = Number(els.ankiFieldDe.value);
  const esFieldIndex = Number(els.ankiFieldEs.value);
  const categoria = els.ankiCategoria.value.trim() || 'Importado (Anki)';
  const nivel = els.ankiNivel.value || 'A1';
  const idPrefix = `anki-${Date.now()}-`;

  const entries = ankiImport.notesToVocabEntries(ankiParsedDeck.notes, {
    deFieldIndex,
    esFieldIndex,
    categoria,
    nivel,
    idPrefix,
  });

  if (entries.length === 0) {
    showToast('Ninguna nota tenía ambos campos completos ❌');
    return;
  }

  await storage.addCustomVocabEntries(entries);
  els.ankiModal.classList.add('hidden');
  ankiParsedDeck = null;
  showToast(`${entries.length} tarjetas importadas ✅`);

  await loadVocabAndInit();
  await loadQueue();
  renderCurrent();
  await refreshDueCount();
  renderLevelsSettings();
}

// ---------------------------------------------------------------------------
// Tema / dark mode
// ---------------------------------------------------------------------------

function applyStoredTheme() {
  const theme = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', theme);
  if (els.toggleDark) els.toggleDark.checked = theme === 'dark';
}

function toggleTheme(isDark) {
  const theme = isDark ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}

// ---------------------------------------------------------------------------
// Backup (export / import)
// ---------------------------------------------------------------------------

async function exportProgress() {
  const data = await storage.exportBackup();
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const stamp = new Date().toISOString().slice(0, 10);
  a.href = url;
  a.download = `deutsch-karten-backup-${stamp}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  showToast('Progreso exportado ✅');
}

async function importProgress(file) {
  try {
    const text = await file.text();
    const data = JSON.parse(text);
    await storage.importBackup(data);
    showToast('Progreso importado ✅');
    unlockedLevels = await storage.getUnlockedLevels();
    await loadVocabAndInit();
    await loadQueue();
    renderCurrent();
    await refreshDueCount();
    renderLevelsSettings();
    await refreshLevelBanner();
    if (!el('view-stats').classList.contains('hidden')) renderStats();
  } catch (err) {
    console.error(err);
    showToast('No se pudo importar el archivo ❌');
  }
}

// ---------------------------------------------------------------------------
// Navegación entre vistas
// ---------------------------------------------------------------------------

const VIEW_TITLES = { review: 'Repasar', stats: 'Estadísticas', settings: 'Ajustes' };

function switchView(view) {
  document.querySelectorAll('.view').forEach((v) => v.classList.add('hidden'));
  el(`view-${view}`).classList.remove('hidden');
  document.querySelectorAll('.tab-btn').forEach((b) => {
    b.classList.toggle('active', b.dataset.view === view);
  });
  els.viewTitle.textContent = VIEW_TITLES[view] || '';
  els.dueCount.classList.toggle('hidden', view !== 'review');

  if (view === 'stats') renderStats();
  if (view === 'settings') renderLevelsSettings();
}

// ---------------------------------------------------------------------------
// Toast
// ---------------------------------------------------------------------------

let toastTimer = null;
function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => els.toast.classList.add('hidden'), 2500);
}

// ---------------------------------------------------------------------------
// Wiring de eventos estáticos (una sola vez)
// ---------------------------------------------------------------------------

function wireStaticUI() {
  els.tabbar.addEventListener('click', (e) => {
    const btn = e.target.closest('.tab-btn');
    if (btn) switchView(btn.dataset.view);
  });

  els.btnReveal.addEventListener('click', revealCard);

  els.gradeButtons.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-grade');
    if (btn) gradeCard(Number(btn.dataset.grade));
  });

  els.writeForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleWriteCheck();
  });

  els.writeGradeButtons.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-grade');
    if (btn) gradeCard(Number(btn.dataset.grade));
  });

  els.btnReviewMore.addEventListener('click', async () => {
    await loadQueue();
    renderCurrent();
  });

  els.onboardingOk.addEventListener('click', async () => {
    els.onboarding.classList.add('hidden');
    await storage.setMeta('onboardingSeen', true);
  });

  els.toggleDark.addEventListener('change', (e) => toggleTheme(e.target.checked));

  els.toggleAudioOnly.addEventListener('change', async (e) => {
    audioOnlyMode = e.target.checked;
    await storage.setMeta('audioOnlyMode', audioOnlyMode);
    if (reviewMode === 'flashcards') renderCurrent();
  });

  els.btnDrillArticles.addEventListener('click', openArticlesDrill);
  els.btnDrillConjugation.addEventListener('click', openConjugationDrill);

  els.drillOptions.addEventListener('click', (e) => {
    const btn = e.target.closest('.quiz-option');
    if (!btn || btn.disabled) return;
    handleDrillAnswer(btn);
  });
  els.drillCloseBtn.addEventListener('click', () => {
    els.drillModal.classList.add('hidden');
    drillState = null;
  });

  els.btnExport.addEventListener('click', exportProgress);
  els.importFile.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) importProgress(file);
    e.target.value = '';
  });

  // Mode switch (Flashcards / Quiz)
  els.modeSwitch.addEventListener('click', (e) => {
    const btn = e.target.closest('.mode-btn');
    if (!btn || btn.classList.contains('active')) return;
    reviewMode = btn.dataset.mode;
    els.modeSwitch.querySelectorAll('.mode-btn').forEach((b) => b.classList.toggle('active', b === btn));
    renderCurrent();
  });

  // Banner de sugerencia de nivel
  els.levelBannerTest.addEventListener('click', () => {
    const level = els.levelBanner.dataset.nextLevel;
    if (level) openDiagnosticModal(level);
  });
  els.levelBannerDismiss.addEventListener('click', async () => {
    await storage.setMeta('levelBannerDismissedUntil', levels.snoozeBannerUntil());
    els.levelBanner.classList.add('hidden');
  });

  // Lista de niveles en Ajustes (delegación)
  els.levelsList.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;
    const level = btn.dataset.level;
    if (btn.dataset.action === 'unlock') unlockLevel(level);
    else if (btn.dataset.action === 'test') openDiagnosticModal(level);
  });

  // Test de diagnóstico
  els.diagnosticOptions.addEventListener('click', (e) => {
    const btn = e.target.closest('.quiz-option');
    if (!btn || btn.disabled) return;
    handleDiagnosticAnswer(btn);
  });
  els.diagnosticCloseBtn.addEventListener('click', () => {
    els.diagnosticModal.classList.add('hidden');
  });

  // Import de Anki
  els.ankiFile.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) handleAnkiFileSelected(file);
    e.target.value = '';
  });
  els.ankiConfirmBtn.addEventListener('click', confirmAnkiImport);
  els.ankiCancelBtn.addEventListener('click', () => {
    els.ankiModal.classList.add('hidden');
    ankiParsedDeck = null;
  });
}

// ---------------------------------------------------------------------------

boot();
