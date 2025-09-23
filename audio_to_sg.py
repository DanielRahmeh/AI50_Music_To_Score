import argparse
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from pathlib import Path
import json

def main():
    # Definition des arguments
    p = argparse.ArgumentParser()
    p.add_argument("--wav", required=True, help="Data/audio/1727.wav")
    p.add_argument("--sr", type=int, default=22050)
    p.add_argument("--n_fft", type=int, default=2048)
    p.add_argument("--hop_length", type=int, default=512)
    p.add_argument("--n_mels", type=int, default=128)
    p.add_argument("--save", type=str, default=None, help="Data/image")
    p.add_argument("--show", action="store_true", help="Afficher la figure à l'écran")
    args = p.parse_args()

    # Charement du fichier audio
    y, sr = librosa.load(args.wav, sr=args.sr, mono=True)

    # Calcul du spectrogramme Mel
    mel = librosa.feature.melspectrogram(
        y=y, sr=sr, n_fft=args.n_fft, hop_length=args.hop_length, n_mels=args.n_mels, power=2.0
    )
    mel_db = librosa.power_to_db(mel, ref=np.max)

    # Sauvegarde en .npy
    out_npy = Path(args.save).with_suffix(".npy") if args.save else Path("mel.npy")
    np.save(out_npy, mel_db.astype(np.float32))
    print(f"[OK] Mel dB sauvegardé : {out_npy.resolve()}")

    # Sauvegarde du meta.json
    meta = {
        "sr": sr,
        "n_fft": args.n_fft,
        "hop_length": args.hop_length,
        "n_mels": args.n_mels,
        "n_frames": int(mel_db.shape[1]),
        "duration_s": float(len(y)/sr),
        "frame_step_s": args.hop_length/ sr
    }
    meta_path = Path(args.save).with_suffix(".meta.json") if args.save else Path("mel.meta.json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[OK] Meta écrit : {meta_path.resolve()}")

    # Affichage
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(
        mel_db, sr=sr, hop_length=args.hop_length, x_axis="time", y_axis="mel"
    )
    plt.title("Log-Mel spectrogram")
    plt.colorbar(format="%+2.0f dB")
    plt.tight_layout()

    # Sauvegarde
    if args.save:
        out = Path(args.save)
        out.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out, dpi=150)
        print(f"[OK] Image sauvegardée : {out.resolve()}")

    # Affichage à l'écran (optionnel)
    if args.show:
        plt.show()

    # Infos utiles
    print(f"[INFO] mel_db shape = {mel_db.shape}  (n_mels, frames)")

if __name__ == "__main__":
    main()
