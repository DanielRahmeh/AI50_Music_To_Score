import argparse
import pandas as pd
import xml.etree.ElementTree as ET
from music21 import stream, note, chord, duration, meter, tempo, clef, instrument as m21instr

# Permet de mettre les valeurs de temps/durée dans les temps d’une grille rythmique régulière
def quantize(x, q):
    return round(x / q) * q

# Lit le tempo et la signature rythmique depuis un fichier MIDI si possible
def extract_tempo_and_timesig_from_midi(mid_path: str):
    try:
        import mido
    except ImportError:
        return None, None
    try:
        mid = mido.MidiFile(mid_path)
    except Exception:
        return None, None
    bpm = None; ts = None
    for tr in mid.tracks:
        for msg in tr:
            if msg.type == 'set_tempo' and bpm is None:
                bpm = mido.tempo2bpm(msg.tempo)
            elif msg.type == 'time_signature' and ts is None:
                ts = f"{msg.numerator}/{msg.denominator}"
            if bpm is not None and ts is not None:
                break
        if bpm is not None and ts is not None:
            break
    return bpm, ts

# Supprime les liaisons (tie/tied/slur) dans un fichier MusicXML (temporaire)
def strip_liaisons_from_musicxml(xml_path: str, out_path: str = None) -> int:
    tree = ET.parse(xml_path); root = tree.getroot()
    def ln(x): return x.rsplit('}',1)[-1] if '}' in x else x
    removed = 0
    for n in root.iter():
        if ln(n.tag) != "note": continue
        for child in list(n):
            if ln(child.tag) == "tie":
                n.remove(child); removed += 1
            elif ln(child.tag) == "notations":
                for nn in list(child):
                    if ln(nn.tag) in ("tied","slur"):
                        child.remove(nn); removed += 1
    tree.write(out_path or xml_path, encoding="utf-8", xml_declaration=True)
    return removed

# Utilise Verovio pour rendre un fichier MusicXML en SVG
def render_svg_with_verovio(xml_path: str, out_base: str):
    import verovio
    tk = verovio.toolkit()
    tk.setOptions({"pageHeight":2970,"pageWidth":2100,"scale":40,"adjustPageHeight":1})
    if not tk.loadFile(xml_path):
        raise RuntimeError(f"Verovio n'a pas pu charger: {xml_path}")
    pages = tk.getPageCount() or 1
    outs = []
    for p in range(1, pages+1):
        try: svg = tk.renderToSVG(p)
        except TypeError:
            tk.setPage(p); svg = tk.renderToSVG()
        target = f"{out_base}.svg" if pages==1 else f"{out_base}_p{p}.svg"
        with open(target, "w", encoding="utf-8") as f: f.write(svg)
        outs.append(target)
    return outs

def main():
    # Arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--mid", default=None)
    ap.add_argument("--bpm", type=float, default=120.0)
    ap.add_argument("--timesig", default="4/4")
    ap.add_argument("--quantum", type=float, default=0.25)
    ap.add_argument("--max_notes", type=int, default=None)
    ap.add_argument("--out", default="partition")
    args = ap.parse_args()

    # Lecture du CSV
    df = pd.read_csv(args.csv).sort_values("start_time")
    
    if args.max_notes: df = df.head(args.max_notes)

    # Détection des colonnes
    has_beats = all(c in df.columns for c in ["start_beat","end_beat"])
    if has_beats:
        print("[USE] Colonnes 'start_beat' (début en battements) et 'end_beat' (durée en battements) détectées.")
        bpm, ts = None, None  # ignorés
    else:
        bpm, ts = (None, None)
        if args.mid:
            bpm, ts = extract_tempo_and_timesig_from_midi(args.mid)
        bpm = bpm if bpm is not None else args.bpm
        ts  = ts  if ts  is not None else args.timesig
        print(f"[USE] BPM={bpm:.2f} | TS={ts} | quantum={args.quantum}")

    # Construction de la partition Music21
    sc = stream.Score() 
    parts = []

    # On sépare par 'instrument' si présent, sinon une seule piste
    inst_ids = df["instrument"].unique().tolist() if "instrument" in df.columns else [None]
    for inst_id in inst_ids:
        part_df = df if inst_id is None else df[df["instrument"] == inst_id]
        prt = stream.Part()
        if inst_id is not None:
            prt.id = f"Inst{inst_id}"
            prt.partName = f"Instrument {inst_id}"
        prt.insert(0, m21instr.Piano())
        prt.insert(0, clef.TrebleClef())

        # Indication de mesure et tempo
        ts_use = args.timesig
        if not has_beats and ts is not None:
            ts_use = ts
        prt.insert(0, meter.TimeSignature(ts_use))

        if not has_beats:
            prt.insert(0, tempo.MetronomeMark(number=bpm))
        q = args.quantum

        # Récupération de chaque note et de leur placement
        events = []
        for _, row in part_df.iterrows():
            midi = int(row["note"])
            if has_beats:
                start_ql = float(row["start_beat"])
                dur_ql   = float(row["end_beat"])  # DUREE en battements
            else:
                start_s = float(row["start_time"]) / 1000.0
                end_s   = float(row["end_time"])   / 1000.0
                start_ql = start_s * (args.bpm/60.0 if bpm is None else bpm/60.0)
                dur_ql   = max(0.01, (end_s - start_s) * (args.bpm/60.0 if bpm is None else bpm/60.0))
                start_ql = quantize(start_ql, q)
                dur_ql   = max(q, quantize(dur_ql, q))

            events.append((start_ql, dur_ql, midi))

        # Tri et regroupement des notes simultanées par instrumet pour faire des accords
        events.sort(key=lambda x: (x[0], x[2]))
        grouped = {}
        for s, d, m in events:
            grouped.setdefault((s, d), []).append(m)

        # Insertion des notes dans la partition et mets des silences si besoin
        current = 0.0
        for (s, d) in sorted(grouped.keys()):
            if s > current + 1e-6:
                r = note.Rest(); r.duration = duration.Duration(s - current)
                prt.insert(current, r); current = s
            midis = grouped[(s, d)]
            if len(midis) == 1:
                n = note.Note(midis[0]); n.duration = duration.Duration(d)
                prt.insert(s, n)
            else:
                ch = chord.Chord(midis); ch.duration = duration.Duration(d)
                prt.insert(s, ch)
            current = max(current, s + d)

        # Finalisation de la partition
        prt.makeMeasures(inPlace=True)
        # Pas de ties “music21” (temporaire)
        for n in prt.recurse().notes: n.tie = None
        parts.append(prt)

    # Ajout des pistes au score
    for p in parts: sc.insert(0, p)

    # Export du fichier .musicxml
    out_xml = f"{args.out}.musicxml"
    sc.write("musicxml", out_xml)
    removed = strip_liaisons_from_musicxml(out_xml)
    if removed: print(f"[CLEAN] Liaisons (tie/tied/slur) supprimées : {removed}")

    # Rendu SVG avec Verovio
    outs = render_svg_with_verovio(out_xml, args.out)
    for o in outs: print("[OK] SVG:", o)

if __name__ == "__main__":
    main()
