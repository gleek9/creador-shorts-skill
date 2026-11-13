---
name: creador-shorts
description: Crea shorts y vídeos animados verticales u horizontales adaptados al nicho, estilo visual y voz (o formato sin voz) de cualquier creador usando Remotion, React, TypeScript, Three.js (parallax 3D), faster-whisper y FFmpeg. Antes de generar nada, realiza una entrevista obligatoria de 10 preguntas más 1 pregunta extra para analizar una URL de referencia.
---

# Creador de Shorts Animados Adaptables

Esta skill convierte cualquier tema en un vídeo animado con escenas 3D en movimiento, gráficos vectoriales sincronizados, música, efectos de sonido y subtítulos dinámicos — **totalmente adaptado al estilo, audiencia y formato de cada creador**.

## Regla de comunicación con el usuario

- Habla siempre en el idioma del usuario, con lenguaje claro, frases cortas y pasos numerados.
- Si el usuario no es técnico, no le pidas ejecutar comandos ni editar código: encarga tú la instalación, alineación de voz, generación de escenas y renderizado.

---

## Fase 1 (OBLIGATORIA): Entrevista de adaptación (10 preguntas + 1 URL de referencia)

**NUNCA escribas el guion, generes imágenes ni programes escenas sin haber hecho primero estas 11 preguntas y recibido respuesta del usuario** (si el usuario ya respondió algunas en su primer mensaje, confírmalas y pide solo las que falten).

Presenta las preguntas de forma ordenada y fácil de responder:

1. **Nicho y tema del vídeo:** ¿De qué trata tu canal y cuál es la idea exacta que quieres explicar en este vídeo?
2. **Público y objetivo:** ¿A quién va dirigido (principiantes, entusiastas, clientes, niños, profesionales) y qué quieres que aprenda o sienta al verlo?
3. **Plataforma y duración:** ¿Es para YouTube Shorts, Reels, TikTok u otro formato, y cuánto quieres que dure (30 s rápido, 45 s equilibrado o 60 s detallado)?
4. **Estilo visual general:** ¿Qué estética prefieres para las escenas? (Ej. boceto blanco y negro con colores resaltantes, oscuro/neón futurista, minimalista pastel, estilo cómic, editorial/revista, etc.)
5. **Paleta de colores y tipografía:** ¿Qué 2 o 3 colores definen tu marca y qué vibra de letras prefieres (gruesa moderna, manuscrita, elegante, gamer)?
6. **Personaje o presentador:** ¿Quieres un personaje animado en pantalla (indica edad aproximada, ropa, gafas, accesorios o estilo) o prefieres explicar solo con objetos, iconos y gráficas animadas?
7. **Escenarios clave:** ¿En qué 2 a 4 lugares o ambientes debería ocurrir la historia? (Ej. escritorio, taller, cocina, oficina, espacio, tienda, laboratorio, ciudad)
8. **Narración y audio:** ¿Usarás tu voz real grabada, una locución externa que subirás en audio, o prefieres un **vídeo sin voz** (solo música, efectos y subtítulos/textos en pantalla)?
9. **Subtítulos, textos y música:** ¿Quieres subtítulos grandes de 1–3 palabras, carteles fijos con datos clave, y qué estilo de música va mejor (neutra explicativa, energética, humorística, lo-fi, épica)?
10. **Tono y cierre:** ¿Qué tono debe tener el texto (cercano, serio, humorístico, sarcástico; tú/vos/usted) y cómo quieres cerrar (frase memorable, pregunta para comentarios o llamado a la acción)?

**Pregunta extra (11) — Referencia por URL:**
11. **URL de referencia:** ¿Tienes algún enlace (URL) de un vídeo, canal, imagen o página web cuyo estilo visual, ritmo o diseño quieras tomar como inspiración? *(Pega la URL aquí; si no tienes una ahora, responde «ninguna»).*

### Si el usuario entrega una URL en la pregunta 11
- Analiza la URL con tus herramientas web o de navegador antes de diseñar el guion y los escenarios.
- Extrae: estructura del gancho, ritmo de cortes, paleta de colores, estilo gráfico y tipo de texto en pantalla.
- Si la URL está bloqueada o no carga, infórmalo claramente al usuario y pídele una breve descripción o captura de pantalla de esa referencia antes de continuar.

---

## Fase 2: Preparación del entorno y tecnologías

Este flujo combina cinco tecnologías incluidas en `assets/plantilla/` (consulta `references/stack-y-motor.md` para detalles técnicos):
1. **Remotion + React + TypeScript:** renderizado cuadro por cuadro (`1080×1920`, 30 FPS), animaciones SVG, carteles HTML fijos y subtítulos sincronizados.
2. **Three.js + React Three Fiber (`@remotion/three`):** cámara en movimiento con efecto parallax 3D real usando cada fondo (`1536×2752`) y su mapa de profundidad (`_prof.png`).
3. **Python + `faster-whisper`:** escucha el audio de la voz y detecta el segundo exacto de cada palabra para disparar planos, gestos y efectos. (En modo **sin voz**, usa `scripts/generar_tiempos_sin_voz.py`).
4. **FFmpeg (`imageio-ffmpeg` / `av`):** recorta/escala fondos, genera variantes y mapas de profundidad (`scripts/preparar_escenario.py`), mezcla música + voz + SFX y normaliza el audio final a `-14 LUFS`.
5. **Generación de imágenes:** crea fondos coherentes con el estilo elegido en las preguntas 4, 5, 7 y 11.

### Comprobación inicial del proyecto
- Si el workspace actual todavía no tiene el motor (`src/motor/`, `package.json`, `herramientas/`), copia la base desde `assets/plantilla/` al workspace del proyecto.
- Comprueba la instalación ejecutando el comprobador del proyecto (`./shorts.cmd comprobar` en Windows o `./shorts comprobar` en Mac/Linux) o instala dependencias con `instalar/instalar.ps1` / `instalar/instalar.sh`.

---

## Fase 3: Producción del vídeo adaptado

1. **Diseña y redacta el guion (`Guiones/<N> - <Título>.txt`):**
   - Sigue `references/guia-guion-y-estilo.md`, ajustado al tono, duración y cierre de las preguntas 1–3 y 10.
   - El `.txt` debe contener únicamente el texto limpio para locución o subtítulos (sin corchetes ni notas).
   - Muéstralo completo al usuario para su visto bueno antes de grabar o montar.
2. **Prepara los escenarios (`public/ideas/<N>/`):**
   - Genera las imágenes base en el estilo visual y colores elegidos (preguntas 4, 5, 7 y 11), dejando zona inferior-central despejada para el personaje o gráficos.
   - Ejecuta `scripts/preparar_escenario.py` para obtener los tamaños `1536×2752`, sus variantes (`-b`, `-c`) y los mapas de profundidad (`_prof.png`).
3. **Programa los planos (`src/ideas/<N>.tsx`):**
   - Adapta la paleta, tipografía, personaje (`Muneco` u objetos/gráficos puros según la pregunta 6) y música.
   - Usa carteles HTML fijos (no `<text>` SVG animado sobre fondos complejos) para evitar saltos visuales entre fotogramas.
   - Registra la idea en `src/ideas/lista.ts` y en `herramientas/shorts.py`, y valida con TypeScript (`tsc --noEmit`).
4. **Audio o modo sin voz (según la pregunta 8):**
   - **Con voz:** pide al usuario guardar su audio en `Audios/` y ejecuta `voz <N>` para alinear cada palabra.
   - **Sin voz:** ejecuta `scripts/generar_tiempos_sin_voz.py` para generar `public/voces/<N>/voz.tiempos.json` con ritmo cómodo de lectura y marca `"sin_voz": True` en la idea.
5. **Renderizado y entrega:**
   - Monta el vídeo final con el motor y FFmpeg, entregando el `.mp4` y el `.txt` (título, descripción, hashtags y créditos musicales) en `Vídeos listos/`.
