// Variaciones: cada short sale distinto aunque dos personas hagan la misma idea. Una «semilla» (número) decide, siempre
// igual para el mismo número: qué versión de cada escenario se usa, los colores de la ropa, el encuadre de cada plano y
// la música. Semilla 0 = la versión original (la del ejemplo).
import { createContext, useContext } from "react";

/** Número entre 0 y 1 que depende solo de la semilla y de las claves (determinista: no usa Math.random). */
export const azar = (semilla: number, ...claves: (string | number)[]) => {
  let h = 2166136261 ^ semilla;
  for (const c of claves.join("|")) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
  h = Math.imul(h ^ (h >>> 15), 2246822507);
  h = Math.imul(h ^ (h >>> 13), 3266489909);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
};
export const elige = <T,>(lista: T[], semilla: number, ...claves: (string | number)[]) => lista[Math.floor(azar(semilla, ...claves) * lista.length)];

type Ctx = { semilla: number; plano: number };
const VarianteCtx = createContext<Ctx>({ semilla: 0, plano: 0 });
export const VarianteProvider = VarianteCtx.Provider;
export const useVariante = () => useContext(VarianteCtx);

/** Versión del escenario: «» (original), «-b» o «-c». */
export const versionFondo = (semilla: number, idea: string, fondo: string) => (semilla ? elige(["", "-b", "-c"], semilla, "fondo", idea, fondo) : "");

// Paletas minimalistas blanco y negro (papel y tinta) + colores de lapicera (plumones, resaltadores y bolígrafos)
const ROPAS_PAPEL: [string, string][] = [
  ["#f5f2eb", "#dcd7cc"], ["#27272a", "#18181b"], ["#e7e5e4", "#c7c3bc"], ["#3f3f46", "#27272a"], ["#faf8f2", "#e2ddd2"],
  ["#52525b", "#3f3f46"], ["#d6d3d1", "#a8a29e"], ["#1f2937", "#111827"],
];
const SOMBREROS = ["#27272a", "#3f3f46", "#d6d3d1", "#ef4444", "#2563eb", "#18181b"];
const BUFANDAS = ["#ef4444", "#facc15", "#2563eb", "#22c55e", "#f97316", "#ec4899"];
const PELOS = ["#18181b", "#3f3f46", "#71717a", "#a16207", "#52525b", "#27272a"];

/** Convierte un color cualquiera en tono papel/tinta (claro u oscuro) para mantener el estilo blanco y negro minimalista. */
const aPapelOTinta = (hex: string): [string, string] => {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex);
  if (!m) return ["#f5f2eb", "#dcd7cc"];
  const n = parseInt(m[1], 16);
  const lum = (0.299 * ((n >> 16) & 255) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) / 255;
  return lum > 0.55 ? ["#f5f2eb", "#dcd7cc"] : ["#27272a", "#18181b"];
};

/** Misma persona → mismos colores en todo el vídeo (la clave es su color original). */
export const variarColores = <P extends { ropa: string; ropaOscura?: string; colorSombrero?: string; bufanda?: string | null; pelo?: string | null; vestido?: string | null; fijo?: boolean }>(p: P, semilla: number): P => {
  if (p.fijo) return p;
  if (!semilla) {
    const [ropa, ropaOscura] = aPapelOTinta(p.ropa);
    return {
      ...p,
      ropa,
      ropaOscura,
      vestido: p.vestido ? aPapelOTinta(p.vestido)[1] : p.vestido,
    };
  }
  const [ropa, ropaOscura] = elige(ROPAS_PAPEL, semilla, "ropa", p.ropa);
  return {
    ...p,
    ropa,
    ropaOscura,
    colorSombrero: p.colorSombrero ? elige(SOMBREROS, semilla, "sombrero", p.ropa, p.colorSombrero) : p.colorSombrero,
    bufanda: p.bufanda ? elige(BUFANDAS, semilla, "bufanda", p.ropa, p.bufanda) : p.bufanda,
    pelo: p.pelo ? elige(PELOS, semilla, "pelo", p.ropa, p.pelo) : p.pelo,
    vestido: p.vestido ? elige(ROPAS_PAPEL, semilla, "vestido", p.ropa, p.vestido)[1] : p.vestido,
  };
};
