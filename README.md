# Creador de Shorts Animados (`creador-shorts`)

Skill lista para subir a GitHub (`main`) e instalar en **Gemini / Antigravity**, **Claude Code** o **Codex**, diseñada para que cualquier creador genere shorts animados con escenarios 3D, personajes o gráficos vectoriales, subtítulos sincronizados, música y voz real (o modo sin voz).

## Qué hace antes de empezar

Antes de escribir el guion o crear gráficos, la IA realiza **10 preguntas obligatorias** (nicho, audiencia, duración, estilo visual, paleta, personaje, escenarios, voz/sin voz, subtítulos/música, tono/cierre) **+ 1 pregunta extra para analizar una URL de referencia**, adaptando toda la producción al creador.

## Tecnologías incluidas en la plantilla

- **Remotion + React + TypeScript:** animación por fotogramas (`1080×1920`, 30 FPS) y subtítulos dinámicos.
- **Three.js + React Three Fiber:** movimiento de cámara 3D con mapas de profundidad (`_prof.png`).
- **Python + faster-whisper:** alineación automática palabra por palabra con voz real.
- **FFmpeg:** mezcla de audio, efectos de sonido y normalización a `-14 LUFS`.

## Cómo instalarla desde GitHub

Una vez subas el contenido de esta carpeta a la rama `main` de tu repositorio en GitHub:

- **Instalación universal (`skills` CLI):**
  ```bash
  npx skills add https://github.com/<tu-usuario>/<tu-repo> --skill creador-shorts
  ```
- **Manual en Gemini / Antigravity (global):**
  Copia `skills/creador-shorts` en `~/.gemini/config/skills/creador-shorts/`
- **Manual por proyecto:**
  Copia `skills/creador-shorts` en `.agents/skills/creador-shorts/`
