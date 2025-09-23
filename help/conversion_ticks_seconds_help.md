# Conversion Ticks → Secondes (Explication)

## 1. Les **ticks**
Dans les CSV, `start_time` et `end_time` sont en **ticks**.  
Ce sont des “unités internes MIDI” (pas des secondes).  
Un tick = une petite division de la pulsation rythmique.

---

## 2. Le **PPQ** (Pulses Per Quarter note)
* PPQ = combien de **ticks correspondent à une noire (quarter note)**.  
* Dans un exemple, on trouve ≈ **6144 ticks = 1 noire**.  
* Donc : 6144 ticks → une **noire**, 3072 ticks → une **croche**, etc.

---

## 3. Le **BPM** (Battements par minute)
* BPM = vitesse de la musique.  
* Exemple : 120 BPM = 120 noires/minute = 2 noires/seconde.  
* Donc une noire dure **0,5 seconde**.

---

## 4. Conversion **ticks → secondes**
On combine les deux infos :

```text
seconds = (ticks / PPQ) * (60 / BPM)
```

### Décomposition
* `(ticks / PPQ)` = nombre de noires.  
* `(60 / BPM)` = durée d’une noire en secondes.  
* Multiplication = durée en secondes.

---

## 5. Exemple concret
* Suppose que tu as **12288 ticks**.  
* PPQ = 6144 → 12288 / 6144 = **2 noires**.  
* BPM = 120 → une noire = 0,5 s.  
* Donc 2 × 0,5 = **1 seconde**.  

Vérification :  
```text
(12288 / 6144) * (60 / 120) = 2 * 0.5 = 1 s
```
