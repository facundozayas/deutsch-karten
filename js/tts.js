// Wrapper sobre Web Speech API (speechSynthesis) para pronunciación en alemán.
// La lista de voces carga de forma asíncrona en varios navegadores (incluido
// Safari/iOS), y puede no haber ninguna voz alemana instalada — en ese caso
// degradamos con gracia (el botón se deshabilita) en vez de tirar error.

let voicesCache = [];
let voicesReady = false;
let voicesPromise = null;

function loadVoices() {
  if (voicesPromise) return voicesPromise;

  voicesPromise = new Promise((resolve) => {
    if (!('speechSynthesis' in window)) {
      resolve([]);
      return;
    }

    const tryLoad = () => {
      const list = window.speechSynthesis.getVoices();
      if (list && list.length > 0) {
        voicesCache = list;
        voicesReady = true;
        resolve(list);
        return true;
      }
      return false;
    };

    if (tryLoad()) return;

    window.speechSynthesis.addEventListener('voiceschanged', () => {
      if (!voicesReady) tryLoad();
    });

    // fallback: algunos navegadores nunca disparan voiceschanged
    setTimeout(() => {
      if (!voicesReady) tryLoad();
      if (!voicesReady) resolve([]); // no hay voces, nos rendimos con gracia
    }, 1500);
  });

  return voicesPromise;
}

export function isSupported() {
  return 'speechSynthesis' in window;
}

export async function hasGermanVoice() {
  if (!isSupported()) return false;
  const voices = await loadVoices();
  return voices.some((v) => v.lang && v.lang.toLowerCase().startsWith('de'));
}

export async function speak(text) {
  if (!isSupported() || !text) return false;

  const voices = await loadVoices();
  const germanVoice = voices.find((v) => v.lang && v.lang.toLowerCase().startsWith('de'));

  // Si no hay voz alemana, igual intentamos con lang="de-DE": algunos
  // navegadores sintetizan de forma aproximada aunque no listen la voz.
  window.speechSynthesis.cancel(); // corta cualquier lectura anterior en curso

  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = germanVoice ? germanVoice.lang : 'de-DE';
  if (germanVoice) utter.voice = germanVoice;
  utter.rate = 0.9;

  window.speechSynthesis.speak(utter);
  return true;
}
