# AI50_Music_To_Score


1. **audio_to_spectrogram.py**  
    Convertit un fichier audio `.wav` en spectrogramme et sauvegarde les résultats (image, `.npy`, `.json`).
    py .\audio_to_sg.py --wav .\data\audio\1727.wav --save .\Data\image\1727.png    

2. **csv_to_musicscore.py**  
   Transforme un fichier CSV de notes (timestamps, pitch) en partition musicale au format MusicXML.
    py csv_to_musicscore.py --csv Data\labels\1729.csv --mid Data\midi\1729.mid --out Data\musicscore\1729 --max_notes 300
