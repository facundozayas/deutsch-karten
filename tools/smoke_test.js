// Smoke test end-to-end de la app usando Chromium headless.
// Verifica: carga sin errores, IndexedDB se inicializa con las 384 tarjetas,
// el loop de review funciona (mostrar respuesta -> calificar -> avanza),
// las stats se actualizan, y el export de backup genera un archivo.
const { chromium } = require('playwright');

const BASE_URL = 'http://127.0.0.1:8811';

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } }); // iPhone-ish
  const page = await context.newPage();

  const consoleErrors = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('pageerror', (err) => consoleErrors.push('pageerror: ' + err.message));

  console.log('1. Cargando index.html...');
  await page.goto(BASE_URL + '/index.html', { waitUntil: 'networkidle' });

  // Cerrar onboarding
  const onboardingOk = page.locator('#onboarding-ok');
  if (await onboardingOk.isVisible()) {
    await onboardingOk.click();
    console.log('   Onboarding cerrado.');
  }

  await page.waitForTimeout(500);

  console.log('2. Chequeando IndexedDB...');
  const cardCount = await page.evaluate(async () => {
    const dbReq = indexedDB.open('german-app-db');
    const db = await new Promise((res, rej) => {
      dbReq.onsuccess = () => res(dbReq.result);
      dbReq.onerror = () => rej(dbReq.error);
    });
    const tx = db.transaction('cardStates', 'readonly');
    const store = tx.objectStore('cardStates');
    const countReq = store.count();
    return new Promise((res, rej) => {
      countReq.onsuccess = () => res(countReq.result);
      countReq.onerror = () => rej(countReq.error);
    });
  });
  console.log(`   Tarjetas en IndexedDB: ${cardCount}`);
  if (cardCount !== 384) throw new Error(`Se esperaban 384 tarjetas, hay ${cardCount}`);

  console.log('3. Verificando due-count y primera tarjeta...');
  const dueCountText = await page.locator('#due-count').textContent();
  console.log('   due-count:', dueCountText);

  const cardVisible = await page.locator('#review-card-wrap').isVisible();
  if (!cardVisible) throw new Error('La tarjeta de repaso no está visible');

  const term1 = await page.locator('#card-term').textContent();
  console.log('   Primer término mostrado:', term1);

  console.log('4. Revelando respuesta y calificando 5 tarjetas...');
  for (let i = 0; i < 5; i++) {
    await page.locator('#btn-reveal').click();
    await page.waitForTimeout(150);
    const answer = await page.locator('#card-answer').textContent();
    const grade = [1, 2, 3, 4][i % 4];
    // Escopado a #review-card-wrap: desde v3 el modo Escribir tiene sus
    // propios botones .btn-grade (ocultos) en #write-grade-buttons, y sin
    // esto el locator sería ambiguo (matchea los dos aunque uno esté hidden).
    await page.locator(`#review-card-wrap .btn-grade[data-grade="${grade}"]`).click();
    await page.waitForTimeout(150);
    console.log(`   Tarjeta ${i + 1}: respuesta="${answer}", grade=${grade}`);
  }

  console.log('5. Verificando reviewLog en IndexedDB...');
  const logCount = await page.evaluate(async () => {
    const dbReq = indexedDB.open('german-app-db');
    const db = await new Promise((res, rej) => {
      dbReq.onsuccess = () => res(dbReq.result);
      dbReq.onerror = () => rej(dbReq.error);
    });
    const tx = db.transaction('reviewLog', 'readonly');
    const countReq = tx.objectStore('reviewLog').count();
    return new Promise((res, rej) => {
      countReq.onsuccess = () => res(countReq.result);
      countReq.onerror = () => rej(countReq.error);
    });
  });
  console.log(`   Entradas en reviewLog: ${logCount}`);
  if (logCount !== 5) throw new Error(`Se esperaban 5 entradas de log, hay ${logCount}`);

  console.log('6. Yendo a Estadísticas...');
  await page.locator('.tab-btn[data-view="stats"]').click();
  await page.waitForTimeout(300);
  const statToday = await page.locator('#stat-today').textContent();
  const statTotal = await page.locator('#stat-total').textContent();
  console.log(`   Repasadas hoy: ${statToday}, Total: ${statTotal}`);
  if (statToday !== '5') throw new Error(`Se esperaba 5 repasadas hoy, salió ${statToday}`);
  if (statTotal !== '384') throw new Error(`Se esperaba 384 total, salió ${statTotal}`);

  console.log('7. Probando toggle de modo oscuro/claro...');
  await page.locator('.tab-btn[data-view="settings"]').click();
  await page.waitForTimeout(200);
  const themeBefore = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  // El checkbox real está visualmente oculto (opacity:0, 0x0) por el estilo
  // custom del switch; clickeamos el .slider visible, que al estar dentro
  // del <label> dispara el toggle del input igual que un click nativo.
  // Escopado al switch de #toggle-dark: desde v3 también existe el switch
  // de "Modo solo audio" con la misma estructura .switch .slider.
  await page.locator('#toggle-dark').locator('xpath=following-sibling::span[contains(@class,"slider")]').click();
  await page.waitForTimeout(100);
  const themeAfter = await page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  console.log(`   Tema: ${themeBefore} -> ${themeAfter}`);
  if (themeBefore === themeAfter) throw new Error('El toggle de tema no cambió el atributo data-theme');

  console.log('8. Probando exportar progreso (backup)...');
  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.locator('#btn-export').click(),
  ]);
  const suggestedName = download.suggestedFilename();
  console.log('   Archivo exportado:', suggestedName);
  if (!suggestedName.endsWith('.json')) throw new Error('El export no generó un .json');

  console.log('9. Verificando registro del service worker...');
  const swState = await page.evaluate(async () => {
    if (!('serviceWorker' in navigator)) return 'unsupported';
    await new Promise((r) => setTimeout(r, 500));
    const reg = await navigator.serviceWorker.getRegistration();
    return reg ? (reg.active ? 'active' : 'registered-not-active') : 'not-registered';
  });
  console.log('   Service worker:', swState);

  console.log('\n--- Errores de consola capturados ---');
  if (consoleErrors.length > 0) {
    consoleErrors.forEach((e) => console.log('  ERROR:', e));
  } else {
    console.log('  (ninguno)');
  }

  await browser.close();

  if (consoleErrors.length > 0) {
    console.error('\nFALLÓ: hubo errores de consola.');
    process.exit(1);
  }
  console.log('\nTODO OK ✅');
})().catch((err) => {
  console.error('FALLÓ:', err);
  process.exit(1);
});
