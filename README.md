# Deutsch Karten

App de repaso de vocabulario alemán (niveles A1 y A2, con mecanismo listo para B1/B2), con repetición espaciada real (FSRS), pensada para usarse desde el celular como PWA instalada, sin cuentas ni servidor: todo tu progreso vive en el navegador de tu dispositivo.

## Qué incluye esta versión (v3)

- 384 palabras/frases A1 + 265 de A2 (649 en total), organizadas por categorías temáticas. B1/B2 se generan cuando llegues ahí — el mecanismo de niveles ya los soporta sin tocar código.
- Flashcards con el algoritmo FSRS real (no un timer fijo): las tarjetas se repiten justo cuando es más probable que las estés por olvidar.
- Modo Quiz (opción múltiple) y modo **Escribir** (producción activa: escribís la palabra en alemán de memoria, incluido el artículo) — ambos alimentan el mismo sistema de repetición espaciada que las flashcards.
- **Modo solo audio** (toggle en Ajustes): en Flashcards, escuchás la palabra en alemán en vez de leerla — pensado para usar en el tren sin mirar la pantalla.
- **Práctica extra** (Ajustes): drills cortos de artículos (der/die/das) y de conjugación de 29 verbos de alta frecuencia en presente — no cuentan para las estadísticas ni la racha, son un complemento del repaso diario, no un reemplazo.
- Sistema de niveles: desbloqueás A2/B1/B2 a mano desde Ajustes, o hacés un test de diagnóstico (15 preguntas, 85% para aprobar) que te lo sugiere. La app también te avisa sola cuando ya dominás la mayoría del nivel actual.
- Importar mazos `.apkg` de AnkiWeb (necesita conexión la primera vez que la usás, después funciona offline).
- Dirección de la tarjeta mezclada al azar (alemán→español y español→alemán), con inglés como dato extra.
- Botón de pronunciación (lee la palabra en alemán con la voz del navegador).
- Estadísticas: repasadas hoy, racha de días, % de retención, cantidad por estado.
- Funciona instalada como app (PWA) y offline después de la primera carga (salvo el import de Anki la primera vez).
- Exportar/importar tu progreso como backup en JSON (incluye tarjetas importadas de Anki y vocabulario propio).

## Cómo probarla en tu compu antes de publicarla

No hace falta build ni instalar nada raro, es HTML/CSS/JS plano. Solo necesitás levantar un servidor estático local (los navegadores no dejan que los `fetch()` y el service worker funcionen bien si abrís el `index.html` directo con `file://`).

En Windows, con Python instalado:
```
cd deutsch-karten
python -m http.server 8080
```
Si no tenés Python, con Node instalado también sirve `npx serve .` desde la misma carpeta.

Y abrís `http://localhost:8080` en el navegador.

## Cómo publicarla gratis en GitHub Pages (paso a paso)

1. **Crear el repositorio.** Entrá a github.com, tocá el `+` de arriba a la derecha → "New repository". Nombre sugerido: `deutsch-karten`. Dejalo en **Public** (GitHub Pages gratis requiere que sea público, salvo que tengas plan pago). No tildes "Add a README" porque ya tenemos uno.

2. **Subir el código.** Desde una terminal (PowerShell o Git Bash) parada en la carpeta del proyecto:
   ```
   cd deutsch-karten
   git init
   git add .
   git commit -m "Primera version de Deutsch Karten"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/deutsch-karten.git
   git push -u origin main
   ```
   (Reemplazá `TU_USUARIO` por tu usuario de GitHub. Te va a pedir que te loguees — GitHub ya no acepta contraseña por git, te va a pedir un "personal access token" o va a abrir el navegador para loguearte. Si te trabás ahí, avisame.)

3. **Activar GitHub Pages.** En la página del repo en GitHub: `Settings` → menú de la izquierda `Pages` → en "Build and deployment" → "Source" elegís **Deploy from a branch** → branch: **main**, carpeta: **/ (root)** → `Save`.

4. **Esperar el link.** GitHub tarda 1-2 minutos en publicarlo. Refrescando esa misma página de Settings → Pages te va a aparecer el link, algo como:
   ```
   https://TU_USUARIO.github.io/deutsch-karten/
   ```

5. **Instalarla en tu iPhone.** Abrí ese link en Safari (tiene que ser Safari, no Chrome, para que funcione "Agregar a inicio" como PWA) → tocá el ícono de compartir (el cuadradito con la flecha hacia arriba) → **"Agregar a inicio"** → confirmá. Te va a quedar un ícono en la pantalla de inicio que abre la app en modo standalone (sin la barra de Safari), y va a seguir funcionando sin internet después de la primera vez que la abras (salvo el import de Anki, que necesita red la primera vez que la usás).

### Actualizar la app después de cambios

Cada vez que quieras subir una mejora (por ejemplo cuando generemos B1), es:
```
git add .
git commit -m "Descripcion del cambio"
git push
```
GitHub Pages se actualiza solo en 1-2 minutos. Ojo: si cambia algún archivo cacheado por el service worker, hay que bumpear `CACHE_NAME` en `service-worker.js` (ya está comentado ahí mismo) para que no quede la versión vieja pegada en el celular — esto ya está hecho para esta versión (`deutsch-karten-v3`).

## Importante: dónde vive tu progreso

Todo tu progreso de repaso (qué tarjetas viste, cuándo toca repasarlas de nuevo, tu racha, tarjetas importadas de Anki, etc.) se guarda **solo en el navegador de tu dispositivo** (IndexedDB), no en ningún servidor. Si cambiás de celular, desinstalás la app, o borrás datos de navegación de Safari, lo perdés — salvo que antes hayas hecho un backup desde **Ajustes → Exportar progreso**, que te descarga un `.json` que después podés reimportar.

## Estructura del proyecto

```
/
├── index.html
├── manifest.json
├── service-worker.js
├── css/styles.css
├── js/
│   ├── app.js             # boot, cola de repaso, UI, stats, niveles, import, drills
│   ├── fsrs.js             # wrapper sobre ts-fsrs
│   ├── storage.js          # IndexedDB (cardStates, reviewLog, customVocab, meta)
│   ├── levels.js           # lógica de niveles y test de diagnóstico
│   ├── quiz.js              # lógica del modo Quiz
│   ├── write.js              # normalización/chequeo de respuestas del modo Escribir
│   ├── articles.js            # lógica del drill de artículos (der/die/das)
│   ├── conjugation.js          # lógica del drill de conjugación
│   ├── anki-import.js           # parser de mazos .apkg (JSZip + sql.js)
│   ├── tts.js                    # Web Speech API
│   └── vendor/                    # ts-fsrs, jszip, sql.js — vendorizados, sin CDN externo
├── data/
│   ├── vocab-a1.json         # 384 palabras/frases A1
│   ├── vocab-a2.json          # 265 palabras/frases A2
│   └── conjugaciones.json      # 29 verbos de alta frecuencia, presente
├── icons/
└── tools/                     # scripts usados para generar contenido/íconos (no se usan en runtime)
```

## Qué viene después

- Generar `vocab-b1.json` / `vocab-b2.json` cuando llegues a esos niveles.
- Fase 2 (a pedido): heatmap de actividad, exportar progreso propio como `.apkg`, más tiempos verbales (Perfekt/Präteritum) en los drills de conjugación.
