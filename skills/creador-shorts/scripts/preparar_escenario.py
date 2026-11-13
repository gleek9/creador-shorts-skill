#!/usr/bin/env python3
"""Convierte imágenes base en escenarios 1536x2752 con variantes (-b, -c) y mapas de profundidad (_prof.png)."""
import argparse
import subprocess
from pathlib import Path

import av
import imageio_ffmpeg
import numpy as np

W, H = 1536, 2752


def crear_profundidad(jpg_path: Path, prof_path: Path) -> None:
    with av.open(str(jpg_path)) as cont:
        frame = next(cont.decode(video=0))
        gray = frame.to_ndarray(format="gray").astype(np.float32) / 255.0
    grad = np.repeat(np.linspace(0.25, 0.92, H, dtype=np.float32)[:, None], W, axis=1)
    depth = np.clip(grad * 0.85 + (1.0 - gray) * 0.15, 0.05, 1.0)
    arr = (depth * 255).astype(np.uint8)
    with av.open(str(prof_path), mode="w") as oc:
        stream = oc.add_stream("png", rate=1)
        stream.width, stream.height, stream.pix_fmt = W, H, "gray"
        vf = av.VideoFrame.from_ndarray(arr, format="gray")
        for pkt in stream.encode(vf):
            oc.mux(pkt)
        for pkt in stream.encode(None):
            oc.mux(pkt)


def procesar(entrada: Path, salida_dir: Path, nombre: str) -> None:
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    salida_dir.mkdir(parents=True, exist_ok=True)
    p_a = salida_dir / f"{nombre}.jpg"
    p_b = salida_dir / f"{nombre}-b.jpg"
    p_c = salida_dir / f"{nombre}-c.jpg"

    subprocess.run([ff, "-y", "-i", str(entrada), "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", "-q:v", "3", str(p_a)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([ff, "-y", "-i", str(p_a), "-vf", "hflip", "-q:v", "3", str(p_b)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([ff, "-y", "-i", str(p_a), "-vf", f"crop=iw*0.92:ih*0.92,scale={W}:{H}", "-q:v", "3", str(p_c)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for img, suf in [(p_a, ""), (p_b, "-b"), (p_c, "-c")]:
        crear_profundidad(img, salida_dir / f"{nombre}{suf}_prof.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", required=True, help="Ruta de la imagen original")
    ap.add_argument("--salida", required=True, help="Carpeta destino (ej. public/ideas/5)")
    ap.add_argument("--nombre", required=True, help="Nombre base del escenario (ej. estudio)")
    args = ap.parse_args()
    procesar(Path(args.entrada), Path(args.salida), args.nombre)
    print(f"Escenario '{args.nombre}' preparado en {args.salida}")
