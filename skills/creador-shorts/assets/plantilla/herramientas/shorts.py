#!/usr/bin/env python3
"""Shorts Animados — órdenes para preparar voz, comprobar código y montar un short.

    shorts comprobar                 ¿está todo instalado?
    shorts ideas                     las ideas disponibles, con su guion
    shorts tsc                       comprueba el código TypeScript del proyecto
    shorts voz N                     coge el audio de «Audios», lo nivela y alinea cada palabra
    shorts montar N [--variante S]   renderiza el short N y lo deja en «Vídeos listos»
"""
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8")
    except Exception:
        pass

RAIZ = Path(__file__).resolve().parents[1]
GUIONES = RAIZ / "Guiones"
TU_VOZ = RAIZ / "Audios"
LISTOS = RAIZ / "Vídeos listos"
RITMO_VOZ = 1.1
VOCES = RAIZ / "public" / "voces"
SALIDA = RAIZ / "salida"
WINDOWS = os.name == "nt"
AUDIOS = (".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac")

# Registro de vídeos del proyecto: { N: {"titulo": ..., "subir": ..., "tags": ..., "musica": ..., "sin_voz": False} }
IDEAS = {}


def fallo(msg):
    print("\n✗ " + msg)
    sys.exit(1)


def ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        fallo("No encuentro ffmpeg. Ejecuta primero el instalador del proyecto.")


def node_bin():
    """Node portátil de la carpeta o el del sistema."""
    local = RAIZ / "node" / ("npx.cmd" if WINDOWS else "bin/npx")
    if local.exists():
        return str(local)
    exe = shutil.which("npx.cmd" if WINDOWS else "npx") or shutil.which("npx")
    if not exe:
        fallo("No encuentro Node. Ejecuta primero el instalador del proyecto.")
    return exe


def entorno():
    env = dict(os.environ)
    nodo = RAIZ / "node" / ("" if WINDOWS else "bin")
    if nodo.exists():
        env["PATH"] = str(nodo) + os.pathsep + env.get("PATH", "")
    return env


def duracion(audio):
    import av

    with av.open(str(audio)) as c:
        return float(c.duration / 1_000_000) if c.duration else 0.0


def normal(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", s)


def numero(args):
    try:
        n = int(args[0])
    except (IndexError, ValueError):
        fallo("Dime el número de la idea. Ejemplo:  shorts montar 1")
    if n not in IDEAS:
        disp = ", ".join(str(k) for k in IDEAS) or "(ninguna registrada todavía)"
        fallo(f"Esa idea no existe. Ideas disponibles: {disp}.")
    return n


def guion(n):
    f = next(GUIONES.glob(f"{n} - *.txt"), None)
    if not f:
        fallo(f"No encuentro el guion de la idea {n} en la carpeta «Guiones».")
    return f.read_text(encoding="utf-8").strip()


def cmd_comprobar(_):
    bien = True

    def linea(ok, texto):
        nonlocal bien
        bien = bien and ok
        print(("  ✓ " if ok else "  ✗ ") + texto)

    print("Shorts Animados — comprobación")
    linea((RAIZ / "node").exists() or shutil.which("node") is not None, "Node (motor de vídeo)")
    linea((RAIZ / "node_modules" / "remotion").exists(), "Remotion instalado (node_modules)")
    for mod, nombre in (("faster_whisper", "faster-whisper (escucha la voz)"), ("av", "PyAV (lee el audio)"), ("imageio_ffmpeg", "ffmpeg")):
        try:
            __import__(mod)
            linea(True, nombre)
        except Exception:
            linea(False, nombre)
    for n, d in IDEAS.items():
        tiene = (VOCES / str(n) / "voz.tiempos.json").exists()
        print(f"  · Idea {n} «{d['titulo']}»: " + ("tiempos listos" if tiene else "sin tiempos todavía"))
    print("\nTodo listo." if bien else "\nFalta algo: ejecuta instalar/instalar.ps1 (Windows) o instalar/instalar.sh (Mac).")
    sys.exit(0 if bien else 1)


def cmd_ideas(_):
    if not IDEAS:
        print("No hay ideas registradas todavía en IDEAS.")
        return
    for n, d in IDEAS.items():
        print(f"\n{n}. {d['titulo']}\n   {guion(n)}")


def cmd_voz(args):
    n = numero(args)
    audios = sorted([p for p in TU_VOZ.iterdir() if p.suffix.lower() in AUDIOS], key=lambda p: p.stat().st_mtime, reverse=True) if TU_VOZ.exists() else []
    if not audios:
        fallo("No hay ningún audio en la carpeta «Audios». Graba tu voz leyendo el guion y déjala ahí (mp3, wav o m4a).")
    original = audios[0]
    print(f"Uso la voz «{original.name}» para la idea {n}.")
    destino = VOCES / str(n)
    destino.mkdir(parents=True, exist_ok=True)
    voz = destino / "voz.mp3"
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", str(original), "-af", f"atempo={RITMO_VOZ},loudnorm=I=-20:TP=-2:LRA=11", "-ar", "44100", "-ac", "1", "-b:a", "192k", str(voz)], check=True)
    texto = guion(n)
    palabras_guion = texto.split()
    print("Escuchando la voz palabra a palabra (la primera vez descarga el modelo, ~500 MB)…", flush=True)
    from faster_whisper import WhisperModel

    modelo = WhisperModel(os.environ.get("SHORTS_WHISPER", "small"), device="cpu", compute_type="int8")
    segs, _ = modelo.transcribe(str(voz), language="es", word_timestamps=True, vad_filter=False, condition_on_previous_text=False, initial_prompt=texto)
    oidas = [(w.word.strip(), float(w.start), float(w.end)) for s in segs for w in (s.words or []) if w.word.strip()]
    if not oidas:
        fallo("No se oye ninguna palabra en ese audio. Vuelve a grabar el audio leyendo el guion.")
    a = [normal(w) for w in palabras_guion]
    b = [normal(w) for w, _, _ in oidas]
    tiempos = [None] * len(a)
    for blq in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blq.size):
            tiempos[blq.a + k] = (oidas[blq.b + k][1], oidas[blq.b + k][2])
    total = duracion(voz)
    claras = sum(1 for t in tiempos if t is not None)
    i = 0
    while i < len(a):
        if tiempos[i] is None:
            j = i
            while j < len(a) and tiempos[j] is None:
                j += 1
            t0 = tiempos[i - 1][1] if i > 0 else 0.0
            t1 = tiempos[j][0] if j < len(a) else total
            paso = max(t1 - t0, 0.05) / (j - i)
            for k in range(i, j):
                tiempos[k] = (t0 + paso * (k - i), t0 + paso * (k - i + 1))
            i = j
        else:
            i += 1
    palabras = [{"p": w, "ini": round(t[0], 2), "fin": round(t[1], 2)} for w, t in zip(palabras_guion, tiempos)]
    (destino / "voz.tiempos.json").write_text(json.dumps({"duracion": round(total, 2), "palabras": palabras}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ Voz preparada: {len(palabras)} palabras en {total:.1f} s ({claras} oídas con claridad).")
    if claras < 0.7 * len(a):
        print("  ⚠ Parece que la voz no dice el guion tal cual. Vuelve a grabar leyendo el guion exacto.")
    if total > 65:
        print("  ⚠ La voz dura más de 65 s: comprueba que solo grabaste el guion de esta idea.")
    print(f"  Siguiente:  shorts montar {n}")


def cmd_montar(args):
    n = numero(args)
    import random

    variante = int(args[args.index("--variante") + 1]) if "--variante" in args else random.randint(1, 9999)
    tiempos = VOCES / str(n) / "voz.tiempos.json"
    if not tiempos.exists():
        fallo(f"Antes hay que preparar los tiempos:  shorts voz {n}")
    dur = json.loads(tiempos.read_text(encoding="utf-8"))["duracion"]
    d = IDEAS[n]
    SALIDA.mkdir(exist_ok=True)
    bruto = SALIDA / f"short-{n}.mp4"
    registro = SALIDA / f"short-{n}.log"
    estimado = int(dur * (45 if WINDOWS else 4))
    print(f"Haciendo el short {n} «{d['titulo']}» (puede tardar ~{max(1, estimado // 60)} min)…", flush=True)
    inicio = time.time()
    fondo3d = float(os.environ.get("SHORTS_FONDO3D", "0.6" if WINDOWS else "1"))
    with open(registro, "w", encoding="utf-8") as reg:
        r = subprocess.run(
            [node_bin(), "remotion", "render", "src/index.ts", f"short-{n}", str(bruto), "--props", json.dumps({"n": n, "sinVoz": True, "variante": variante, "fondo3d": fondo3d}), "--concurrency=50%", "--crf=20", "--timeout=180000", "--log=error"],
            cwd=RAIZ, stdout=reg, stderr=subprocess.STDOUT, env=entorno(),
        )
    if r.returncode != 0 or not bruto.exists():
        fallo(f"El motor no ha podido hacer el vídeo. Mira salida/short-{n}.log\n" + registro.read_text(encoding="utf-8")[-1500:])
    LISTOS.mkdir(exist_ok=True)
    final = LISTOS / f"{n} - {d['titulo']} ({variante}).mp4"
    voz_mp3 = VOCES / str(n) / "voz.mp3"
    if d.get("sin_voz") or not voz_mp3.exists():
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", str(bruto), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", str(final)], check=True)
    else:
        filtro = "[1:a]aresample=48000,aformat=channel_layouts=stereo[voz];[0:a][voz]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]"
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", str(bruto), "-i", str(voz_mp3), "-filter_complex", filtro, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", str(final)], check=True)
    creditos = {}
    for linea in (RAIZ / "public" / "comun" / "musica" / "CREDITOS.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        if "\t" in linea:
            k, v = linea.split("\t", 1)
            creditos[k] = v
    pista = musica_de(variante, n)
    desc = f"{d['descripcion']}\n\n" if d.get("descripcion") else ""
    final.with_suffix(".txt").write_text(f"{d['subir']}\n\n{desc}{d['tags']}\n\nMúsica: {creditos.get(pista, '')}\n", encoding="utf-8")
    print(f"✓ Short listo en {time.time() - inicio:.0f} s: «{LISTOS.name}/{final.name}» (con su .txt)")


def _azar(semilla, *claves):
    """Mismo algoritmo que src/motor/variante.tsx (FNV-1a)."""
    m = 0xFFFFFFFF
    h = (2166136261 ^ semilla) & m
    for c in "|".join(str(k) for k in claves):
        h = ((h ^ ord(c)) * 16777619) & m
    h = ((h ^ (h >> 15)) * 2246822507) & m
    h = ((h ^ (h >> 13)) * 3266489909) & m
    return ((h ^ (h >> 16)) & m) / 4294967296


def musica_de(variante, n):
    lista = ["local-forecast-elevator.mp3", "lobby-time.mp3"]
    return lista[int(_azar(variante, "musica", str(n)) * len(lista))] if variante else IDEAS[n]["musica"]


def cmd_tsc(_):
    r = subprocess.run([node_bin(), "tsc", "--noEmit", "-p", "."], cwd=RAIZ, env=entorno())
    print("✓ El código está bien." if r.returncode == 0 else "✗ Hay errores en el código (arriba).")
    sys.exit(r.returncode)


ORDENES = {"comprobar": cmd_comprobar, "ideas": cmd_ideas, "voz": cmd_voz, "montar": cmd_montar, "tsc": cmd_tsc}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ORDENES:
        print(__doc__)
        sys.exit(1)
    ORDENES[sys.argv[1]](sys.argv[2:])
