# Stack Tecnológico y Arquitectura del Motor

## 1. Tecnologías utilizadas

- **Remotion (`@remotion/cli`, `remotion`) + React 18 + TypeScript:** motor de composición por fotogramas (`1080×1920`, `30 FPS`).
- **Three.js + `@react-three/fiber` + `@remotion/three`:** proyección de escenarios 2D sobre malla 3D con desplazamiento por mapa de profundidad (`_prof.png`) y movimiento de cámara (`EncuadreCuadro`).
- **Python + `faster-whisper`:** alineación automática palabra por palabra entre el audio de `Audios/` y el texto de `Guiones/<N> - <Título>.txt`, generando `public/voces/<N>/voz.tiempos.json`.
- **FFmpeg (`imageio-ffmpeg`, `av`, `numpy`):** normalización de audio a `-14 LUFS`, mezcla de pista musical + voz + efectos (`sfx/`), y preparación de imágenes `1536×2752` con sus mapas de profundidad.

## 2. Estructura de carpetas de un proyecto

- `Guiones/<N> - <Título>.txt`: texto exacto del vídeo.
- `Audios/`: archivo de audio grabado o locutado por el creador (si usa voz).
- `public/ideas/<N>/`: escenarios `<nombre>.jpg`, variantes (`-b.jpg`, `-c.jpg`) y mapas de profundidad (`_prof.png`).
- `public/voces/<N>/voz.tiempos.json`: tiempos por palabra (`{ duracion, palabras: [{ p, ini, fin }] }`).
- `src/motor/`: núcleo reutilizable (`video.tsx`, `escena.tsx`, `parallax.tsx`, `muneco.tsx`, `cine.tsx`, `voz.tsx`, `variante.tsx`).
- `src/ideas/<N>.tsx` y `src/ideas/lista.ts`: definición de planos, efectos de sonido y registro de cada vídeo.
- `herramientas/shorts.py`: orquestador CLI (`comprobar`, `ideas`, `tsc`, `voz N`, `montar N`).
- `Vídeos listos/`: salida final con `.mp4` y `.txt` de publicación.

## 3. Soporte para modo con voz y modo sin voz

- **Con voz:** se ejecuta `shorts voz N` sobre el audio más reciente en `Audios/`.
- **Sin voz (`sin_voz: True`):** se genera `public/voces/<N>/voz.tiempos.json` con `scripts/generar_tiempos_sin_voz.py` para mantener subtítulos, cortes y efectos sincronizados, y `VideoShort` recibe `sinVoz: true` mientras FFmpeg normaliza música + SFX a `-14 LUFS`.
