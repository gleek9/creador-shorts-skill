#!/usr/bin/env python3
"""Genera voz.tiempos.json para vídeos sin locución, calculando pausas cómodas de lectura."""
import argparse
import json
from pathlib import Path


def generar(guion_path: Path, salida_json: Path, ritmo: float = 1.0) -> None:
    texto = guion_path.read_text(encoding="utf-8").strip()
    palabras = []
    t = 0.25
    for w in texto.split():
        limpia = w.strip("¿?¡!.,:;")
        dur = max(0.24, min(0.55, 0.14 + len(limpia) * 0.032)) / ritmo
        palabras.append({"p": w, "ini": round(t, 2), "fin": round(t + dur, 2)})
        pausa = (0.28 if w[-1] in ".?!" else (0.14 if w[-1] in ",:" else 0.04)) / ritmo
        t += dur + pausa

    salida_json.parent.mkdir(parents=True, exist_ok=True)
    data = {"duracion": round(t + 0.4, 2), "palabras": palabras}
    salida_json.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Tiempos generados: {len(palabras)} palabras en {data['duracion']} s -> {salida_json}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--guion", required=True, help="Archivo .txt del guion")
    ap.add_argument("--salida", required=True, help="Ruta de salida voz.tiempos.json")
    ap.add_argument("--ritmo", type=float, default=1.0, help="Multiplicador de velocidad (ej. 1.1 más rápido)")
    args = ap.parse_args()
    generar(Path(args.guion), Path(args.salida), args.ritmo)
