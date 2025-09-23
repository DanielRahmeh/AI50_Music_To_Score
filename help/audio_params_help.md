# Paramètres audio et spectrogramme (explication)

Ce fichier décrit les paramètres utilisés pour transformer l'audio en spectrogrammes Mel.

## 1. sr = 22050
- **Sample rate (fréquence d'échantillonnage)**
- Chaque seconde d'audio est compressé en 22 050 points.
- Permet d'alléger les fichiers tout en restant fidèle à la musique.

---

## 2. n_fft = 2048
- **Taille de la fenêtre FFT**
- L'audio est découpé en morceaux de 2048 points.
- Plus cette valeur est grande, plus on distingue bien les fréquences, mais on perd en précision temporelle.

---

## 3. hop_length = 512
- **Pas de décalage entre les fenêtres**
- On avance de 512 points à chaque fois.
- Les fenêtres se chevauchent pour mieux suivre le temps et ne rien rater.

---

## 4. n_mels = 128
- **Nombre de bandes Mel**
- Les fréquences sont regroupées en 128 "bandes", suivant la perception de l'oreille humaine.
- Résultat : chaque fenêtre devient une colonne de 128 valeurs.

---

## Résultat final
En appliquant ces paramètres :
- On obtient une **image** appelée log-Mel spectrogramme.
- Taille : `128 (fréquences)` × `N (fenêtres dans le temps)`
