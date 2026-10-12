# Règles des Reels NéoSoluce (à lire par l'agent avant chaque Reel)

## Musique : différente à chaque Reel, toujours dans le thème (néon, Miami, nuit, années 80)

### 1. Musique intégrée à la vidéo (Facebook + secours)
- `tools/make_reel.py N fichier.mp4` génère automatiquement une musique originale différente selon N
  (style qui tourne chaque jour : synthwave, outrun, darkwave, phonk, chillwave, funk rétro ; tempo et tonalité variables).
- Pour un autre Reel le même jour, passe une autre graine : `python3 tools/make_reel.py N fichier.mp4 <graine>`.
- Cette musique est 100 % originale : aucun droit à payer, aucun risque.

### 2. Musique Instagram sous licence (Instagram uniquement)
Instagram permet d'ajouter un titre de sa bibliothèque musicale sous licence via Metricool :
dans `instagramData`, ajoute `"audioConfiguration": {"audioId": "<id>", "audioVolume": 100, "videoVolume": 0}`
(videoVolume 0 coupe la musique intégrée pour éviter deux musiques en même temps).
- Trouver un titre : mets un mot-clé d'ambiance comme `audioId` (ex. « synthwave », « retrowave », « outrun »,
  « phonk », « night drive », « miami », « 80s », « chillwave », « neon », « drift »). L'outil refuse en listant
  les titres correspondants : choisis-en un qui colle au thème, puis réessaie avec son identifiant numérique exact.
- Change de mot-clé d'un jour à l'autre pour varier les ambiances.
- Ne réutilise jamais un titre déjà présent dans `musiques-instagram.txt` (sauf s'il n'y a vraiment plus de choix).
- Après chaque Reel publié avec un titre Instagram, ajoute une ligne à `musiques-instagram.txt`
  (date | reel | audioId | titre | artiste), puis commit + push avec le Reel.
- Si l'audio Instagram est refusé pour une autre raison (compte, droits, erreur), publie sans `audioConfiguration` :
  la musique originale intégrée suffit. Signale-le dans le récap.
- Interdit : toute musique hors bibliothèque Instagram ou hors générateur (pas de Spotify, pas de musique du jeu,
  pas de morceau téléchargé).

### 3. Facebook
Facebook n'a pas de bibliothèque via Metricool : il publie la vidéo avec sa musique originale intégrée.
Comme Instagram et Facebook partagent la même publication Metricool, mets les deux réseaux dans le même post :
`audioConfiguration` ne s'applique qu'à Instagram.
