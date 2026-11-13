# 🎬 Creador de Shorts Animados (`creador-shorts`)

> Skill para **Gemini / Antigravity**, **Claude Code**, **Codex** y otros agentes compatibles que convierte cualquier idea en un short o vídeo animado (`1080×1920`, 30 FPS) con **escenarios 3D en parallax**, gráficos vectoriales, subtítulos dinámicos, música, efectos de sonido y voz real (o modo sin voz), **100 % adaptado a tu estilo**.

[![Repositorio](https://img.shields.io/badge/GitHub-gleek9%2Fcreador--shorts--skill-181717?style=flat&logo=github)](https://github.com/gleek9/creador-shorts-skill)
[![Remotion](https://img.shields.io/badge/Remotion-4.0-0B84F3?style=flat)](https://www.remotion.dev/)
[![Three.js](https://img.shields.io/badge/Three.js-Parallax%203D-000000?style=flat)](https://threejs.org/)
[![Python](https://img.shields.io/badge/Python-3%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)

---

## 📦 Instalación

Elige la forma más cómoda según cómo trabajes:

### Opción 1: Instalación por prompt (sin usar la terminal manualmente)

Abre tu agente de IA (**Gemini / Antigravity**, **Claude Code** o **Codex**) y envíale directamente este mensaje:

```text
Instala la skill creador-shorts desde https://github.com/gleek9/creador-shorts-skill para poder usarla en mis proyectos.
```

> [!TIP]
> Si prefieres que quede instalada solo en el proyecto actual en lugar de de forma global, añade al final: *"instálala solo en este proyecto (`.agents/skills/creador-shorts/`)"*.

### Opción 2: CLI universal (`skills`)

```bash
npx skills add https://github.com/gleek9/creador-shorts-skill --skill creador-shorts
```

### Opción 3: Instalación manual

Clona o descarga [gleek9/creador-shorts-skill](https://github.com/gleek9/creador-shorts-skill) y copia la carpeta `skills/creador-shorts` en la ruta correspondiente:

| Alcance | Ruta de destino |
| :--- | :--- |
| **Global (Gemini / Antigravity)** | `~/.gemini/config/skills/creador-shorts/` |
| **Por proyecto (universal)** | `.agents/skills/creador-shorts/` |

---

## ⚙️ Requisitos previos (para renderizar vídeos)

La skill copia e inicializa la plantilla en tu proyecto automáticamente, pero tu equipo necesita tener instalado:

- **Node.js** (para Remotion, React 18 y TypeScript)
- **Python 3** (para `faster-whisper`, FFmpeg mediante `imageio-ffmpeg`, `av` y `numpy`)

La plantilla incluye instaladores listos en `instalar/` (`instalar.ps1` para Windows e `instalar.sh` para macOS/Linux) y `instalar/requirements.txt`.

---

## 🚀 Cómo usarla paso a paso

No necesitas saber programar ni editar código: la skill se encarga de preparar el proyecto, alinear el audio, programar las escenas y renderizar el vídeo.

### 1. Inicia la conversación con un tema o idea

Abre una carpeta vacía (o tu proyecto de vídeos) en tu agente de IA y pídele el short. Algunos ejemplos de cómo empezar:

- **Con tu propia voz:**
  > *"Usa creador-shorts para hacer un short de 45 segundos explicando qué es una API para principiantes. Voy a grabar mi voz."*
- **Sin voz (solo música, SFX y subtítulos):**
  > *"Crea un short animado de 30 segundos sin voz sobre 3 atajos de teclado que ahorran tiempo, con estética oscura neón."*
- **Inspirado en un vídeo o web de referencia:**
  > *"Quiero un short usando creador-shorts sobre cómo funciona el Wi-Fi. Toma como referencia visual el ritmo de esta URL: https://..."*

### 2. Responde la entrevista de adaptación (10 preguntas + 1 URL)

Antes de escribir el guion o generar gráficos, la IA te hará **11 preguntas rápidas** para adaptar toda la producción a tu canal:

| Aspecto | Qué defines en la entrevista |
| :--- | :--- |
| **1–3. Contenido y formato** | Nicho y tema exacto, público objetivo, plataforma (Shorts, Reels, TikTok) y duración (`30s`, `45s` o `60s`). |
| **4–7. Identidad visual** | Estilo artístico general, paleta de 2–3 colores, tipografía, si quieres personaje animado o solo objetos/gráficas, y 2–4 escenarios clave. |
| **8–10. Audio y narrativa** | Si usarás **tu voz grabada**, **locución externa** o **modo sin voz**; tipo de subtítulos/carteles, estilo de música, tono y cierre. |
| **11. Referencia (opcional)** | Una **URL** de vídeo, canal o web para analizar su gancho, ritmo de cortes, paleta y estilo visual (puedes responder *«ninguna»*). |

### 3. Aprueba el guion

Con tus respuestas, la IA creará el guion limpio (listo para leer o subtitular, sin notas técnicas) en `Guiones/<N> - <Título>.txt` y te lo mostrará completo para que des el visto bueno o pidas ajustes antes de producir las escenas.

### 4. Audio o modo sin voz

- **Si elegiste usar voz:** la IA te pedirá guardar tu grabación en la carpeta `Audios/`. Luego ejecutará `faster-whisper` para detectar el segundo exacto de cada palabra y sincronizar cortes, gestos, subtítulos y efectos de sonido.
- **Si elegiste modo sin voz:** la IA calculará automáticamente un ritmo cómodo de lectura (`scripts/generar_tiempos_sin_voz.py`) para sincronizar subtítulos, transiciones y SFX con la música.

### 5. Recibe tu vídeo listo

La IA preparará los escenarios 3D (`1536×2752` + mapas de profundidad `_prof.png`), programará los planos en Remotion y renderizará el resultado final en `Vídeos listos/`:

- **`<Título>.mp4`**: vídeo vertical `1080×1920` a `30 FPS` con audio normalizado a `-14 LUFS`.
- **`<Título>.txt`**: título sugerido, descripción, hashtags y créditos musicales listos para copiar y publicar.

<details>
<summary>🛠️ Comandos útiles del proyecto (opcional para usuarios técnicos)</summary>

Si quieres inspeccionar o ejecutar pasos manualmente dentro del proyecto generado:

- **Comprobar entorno:** `./shorts.cmd comprobar` (Windows) o `./shorts comprobar` (macOS/Linux)
- **Vista previa interactiva (Remotion Studio):** `npm run estudio`
- **Alinear voz manualmente:** `python herramientas/shorts.py voz <N>`
- **Renderizar vídeo manualmente:** `python herramientas/shorts.py montar <N>`

</details>

---

## 🧩 Tecnologías y arquitectura

| Tecnología | Función en el flujo |
| :--- | :--- |
| **Remotion + React 18 + TypeScript** | Renderizado cuadro por cuadro (`1080×1920`, `30 FPS`), animaciones SVG, carteles HTML fijos y subtítulos sincronizados. |
| **Three.js + React Three Fiber (`@remotion/three`)** | Proyección de escenarios sobre malla 3D con mapas de profundidad (`_prof.png`) y movimiento de cámara parallax. |
| **Python + `faster-whisper`** | Alineación automática palabra por palabra entre tu audio y el guion. |
| **FFmpeg (`imageio-ffmpeg`, `av`, `numpy`)** | Recorte/escalado de fondos, mezcla de voz + música + SFX y normalización a `-14 LUFS`. |

---

## 📁 Estructura del repositorio

```text
creador-shorts-skill/
├── README.md
└── skills/
    └── creador-shorts/
        ├── SKILL.md                  # Flujo completo y reglas de la skill
        ├── references/               # Guías de guion, estilo y arquitectura del motor
        ├── scripts/                  # Scripts Python (escenarios 3D y tiempos sin voz)
        └── assets/
            └── plantilla/            # Plantilla base (Remotion, Three.js, audios, SFX y fuentes)
```

---

## 📄 Licencias y créditos

Consulta [skills/creador-shorts/assets/plantilla/LICENCIAS.txt](skills/creador-shorts/assets/plantilla/LICENCIAS.txt) para el detalle completo:

- **Uso de la plantilla:** puedes crear y monetizar tus propios shorts; no está permitido revender ni redistribuir la plantilla como producto independiente.
- **Música incluida:** *Sneaky Snitch* y *Mischief Maker* de Kevin MacLeod (`incompetech.com`), bajo licencia Creative Commons BY 4.0 (la plantilla añade el crédito automáticamente en el `.txt` final).
- **Efectos de sonido y tipografías:** SFX sintetizados o CC0; fuentes *Montserrat* y *Caveat* bajo SIL Open Font License 1.1.
- **Motor y librerías:** Three.js, React Three Fiber y `faster-whisper` (MIT); Remotion sujeto a [remotion.dev/license](https://www.remotion.dev/license).
