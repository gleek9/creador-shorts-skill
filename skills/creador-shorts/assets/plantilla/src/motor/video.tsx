// Un short = una lista de planos (cada uno empieza en una palabra de la voz) + sonidos anclados a palabras + música.
// Esto monta las secuencias, los subtítulos de 1-2 palabras y el audio. Cada idea solo describe sus planos.
import React, { useEffect, useState } from "react";
import { AbsoluteFill, Audio, Sequence, cancelRender, continueRender, delayRender, interpolate, staticFile, useCurrentFrame } from "remotion";
import { cargarTextura, clamp, useRecursos } from "./cine";
import { Fondos, FondosProvider, SOLAPE, Transicion, Transiciones } from "./escena";
import { FPS, Tiempos, VozProvider, segundoDe } from "./voz";
import { VarianteProvider, elige, versionFondo } from "./variante";
import niveles from "../../public/comun/niveles.json";

export type PlanoDef = {
  C: React.FC<{ dur: number }>;
  empieza: string | null; // palabra(s) de la voz donde empieza el plano (null = el primero)
  vez?: number; // si la palabra se repite: 0 = la primera vez, 1 = la segunda…
  entrada: Transicion;
};
export type SonidoDef = { archivo: string; en: string; vez?: number; retraso?: number; vol?: number; corta?: number };
export type IdeaDef = {
  id: string;
  fondos: string[]; // public/ideas/<id>/<nombre>.jpg y <nombre>_prof.png
  planos: PlanoDef[];
  sonidos: SonidoDef[];
  musica: string; // public/comun/musica/<archivo>
};

const NIVEL = niveles as Record<string, number>;
const vol = (ruta: string) => NIVEL[ruta] ?? 0.3;

// ---------------------------------------------------------------- letras (embebidas: no hace falta internet)
let letras: Promise<void> | null = null;
const cargarLetras = () => {
  if (!letras) {
    letras = Promise.all([
      new FontFace("Montserrat", `url(${staticFile("comun/fuentes/Montserrat-Variable.ttf")})`, { weight: "100 900" }).load(),
      new FontFace("Caveat", `url(${staticFile("comun/fuentes/Caveat-Variable.ttf")})`, { weight: "400 700" }).load(),
    ]).then((fs) => fs.forEach((f) => document.fonts.add(f)));
  }
  return letras;
};
const useLetras = () => {
  const [lista, setLista] = useState(false);
  useEffect(() => {
    if (lista) return;
    const h = delayRender("Letras");
    cargarLetras()
      .then(() => {
        setLista(true);
        continueRender(h);
      })
      .catch((e) => cancelRender(e));
  }, [lista]);
  return lista;
};

// ---------------------------------------------------------------- subtítulos (frases cortas de 1-3 palabras con ritmo fluido, sin parpadeos de 2 fotogramas)
const grupos = (t: Tiempos) => {
  const ps = t.palabras;
  const out: { texto: string; ini: number }[] = [];
  let i = 0;
  while (i < ps.length) {
    let texto = ps[i].p;
    const ini = ps[i].ini;
    let fin = ps[i].fin;
    let j = i + 1;
    // Junta palabras cortas o muy rápidas (<= 3 letras o duración < 0.24s) hasta 3 palabras o ~16 caracteres
    while (j < ps.length && j - i < 3) {
      const prevTermina = /[.,?!:;]$/.test(ps[j - 1].p);
      const cortaPrev = ps[j - 1].p.replace(/[¿?¡!.,:;]/g, "").length <= 3 || fin - ini < 0.24;
      const cortaSig = ps[j].p.replace(/[¿?¡!.,:;]/g, "").length <= 3 || ps[j].fin - ps[j].ini < 0.18;
      const cabe = texto.length + 1 + ps[j].p.length <= 16;
      if (prevTermina || !cabe || (!cortaPrev && !cortaSig)) break;
      texto = `${texto} ${ps[j].p}`;
      fin = ps[j].fin;
      j++;
    }
    out.push({ texto, ini });
    i = j;
  }
  return out;
};

const Subtitulos: React.FC<{ tiempos: Tiempos }> = ({ tiempos }) => {
  const f = useCurrentFrame();
  const t = f / FPS;
  const gs = grupos(tiempos);
  let actual: { texto: string; ini: number } | null = null;
  for (const g of gs) if (t >= g.ini - 0.03) actual = g;
  const ultima = tiempos.palabras[tiempos.palabras.length - 1];
  if (!actual || t > ultima.fin + 0.5) return null;
  const edad = Math.max(0, (t - (actual.ini - 0.03)) * FPS);
  const escala = interpolate(edad, [0, 3], [0.92, 1], clamp);
  return (
    <AbsoluteFill style={{ alignItems: "center", pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          top: 1410,
          padding: "4px 22px 6px",
          background: "linear-gradient(177deg, rgba(253,224,71,0.94) 0%, rgba(250,204,21,0.9) 100%)",
          borderRadius: 12,
          transform: `rotate(-1deg) scale(${escala})`,
          boxShadow: "0 6px 0 rgba(24,24,27,0.22)",
          fontFamily: "Montserrat",
          fontWeight: 900,
          fontSize: 68,
          color: "#fcfaf2",
          letterSpacing: -1,
          WebkitTextStroke: "10px #18181b",
          paintOrder: "stroke fill",
          textShadow: "0 5px 0 rgba(24,24,27,0.5)",
          whiteSpace: "nowrap",
        }}
      >
        {actual.texto}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- el vídeo
export const duracionDe = (t: Tiempos) => Math.ceil((t.duracion + 0.6) * FPS);

const MUSICAS = ["local-forecast-elevator.mp3", "lobby-time.mp3"];

export const VideoShort: React.FC<{ idea: IdeaDef; tiempos: Tiempos; sinVoz?: boolean; variante?: number }> = ({ idea, tiempos, sinVoz, variante = 0 }) => {
  const letrasListas = useLetras();
  const fondos = useRecursos<Fondos>(`fondos-${idea.id}-${variante}`, async () => {
    const pares = await Promise.all(
      idea.fondos.map(async (n) => {
        const v = versionFondo(variante, idea.id, n);
        const [mapa, prof] = await Promise.all([cargarTextura(staticFile(`ideas/${idea.id}/${n}${v}.jpg`), true, true), cargarTextura(staticFile(`ideas/${idea.id}/${n}${v}_prof.png`), false, true)]);
        return [n, { mapa, prof }] as const;
      }),
    );
    return Object.fromEntries(pares);
  });
  if (!fondos || !letrasListas) return null;
  const total = duracionDe(tiempos);
  // cortes: el plano nuevo entra 2 fotogramas antes de la palabra
  const cortes = idea.planos.map((p) => (p.empieza === null ? 0 : Math.round(segundoDe(tiempos, p.empieza, 0, p.vez ?? 0) * FPS) - 2));
  cortes.push(total);
  const O = SOLAPE;
  const pista = variante ? elige(MUSICAS, variante, "musica", idea.id) : idea.musica;
  const musica = `comun/musica/${pista}`;
  const volMusica = vol(`musica/${pista}`);
  const fin = Math.round(tiempos.palabras[tiempos.palabras.length - 1].fin * FPS);
  return (
    <FondosProvider value={fondos}>
      <AbsoluteFill style={{ backgroundColor: "#faf6ec" }}>
        {idea.planos.map((p, i) => {
          const desde = cortes[i] - (i > 0 ? O : 0);
          const hasta = cortes[i + 1] + (i < idea.planos.length - 1 ? O : 0);
          const salida = i < idea.planos.length - 1 ? idea.planos[i + 1].entrada : "nada";
          // en los planos largos, un acercón de golpe en la palabra que cae más cerca de la mitad
          const medio = (cortes[i] + cortes[i + 1]) / 2;
          const enPalabra = tiempos.palabras.map((w) => Math.round(w.ini * FPS)).filter((g) => g > cortes[i] + 0.9 * FPS && g < cortes[i + 1] - 0.9 * FPS);
          const golpe = cortes[i + 1] - cortes[i] >= 2.2 * FPS && enPalabra.length ? enPalabra.reduce((a, b) => (Math.abs(b - medio) < Math.abs(a - medio) ? b : a)) - desde : undefined;
          return (
            <Sequence key={i} from={desde} durationInFrames={hasta - desde}>
              <VozProvider tiempos={tiempos} desde={desde}>
                <VarianteProvider value={{ semilla: variante, plano: i }}>
                  <Transiciones id={`t${i}`} dur={hasta - desde} entrada={i === 0 ? "nada" : p.entrada} salida={salida} golpe={golpe}>
                    <p.C dur={hasta - desde} />
                  </Transiciones>
                </VarianteProvider>
              </VozProvider>
            </Sequence>
          );
        })}
        <Subtitulos tiempos={tiempos} />
        {!sinVoz && <Audio src={staticFile(`voces/${idea.id}/voz.mp3`)} />}
        <Audio
          src={staticFile(musica)}
          loop
          volume={(g) => interpolate(g, [0, 10, fin, fin + 10, total - 6, total], [0, volMusica, volMusica, volMusica * 4, volMusica * 4, 0], clamp)}
        />
        {/* un whoosh en cada barrido */}
        {idea.planos.map((p, i) =>
          i > 0 && p.entrada === "barrido" ? (
            <Sequence key={`w${i}`} from={Math.max(0, cortes[i] - 9)}>
              <Audio src={staticFile("comun/sfx/whoosh.wav")} volume={vol("sfx/whoosh.wav")} />
            </Sequence>
          ) : null,
        )}
        {idea.sonidos.map((s, i) => {
          const ruta = `comun/sfx/${s.archivo}`;
          const f0 = Math.round((segundoDe(tiempos, s.en, 0, s.vez ?? 0) + (s.retraso ?? 0)) * FPS);
          return (
            <Sequence key={`s${i}`} from={Math.max(0, f0)} durationInFrames={s.corta}>
              <Audio src={staticFile(ruta)} volume={vol(`sfx/${s.archivo}`) * (s.vol ?? 1)} />
            </Sequence>
          );
        })}
      </AbsoluteFill>
    </FondosProvider>
  );
};
