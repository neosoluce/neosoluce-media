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

## Reels « gameplay » à partir des captures de Noah (à partir du 19 novembre 2026)
Les seules images de GTA VI autorisées dans nos vidéos sont les captures que Noah filme sur sa propre console
et dépose dans le dossier `captures/` de ce dépôt (voir captures/README.md). Jamais de trailer, d'image Rockstar,
de vidéo d'un autre créateur ni de vidéo qui a fuité.
- À chaque passage, regarde s'il y a dans `captures/` une vidéo pas encore utilisée (liste dans `captures-utilisees.txt`).
- S'il y en a une : écris 2 à 5 encarts utiles (astuce, soluce express, détail, emplacement…) en lien avec ce qu'on voit
  (lis le .txt de même nom s'il existe ; vérifie chaque fait dans au moins deux sources fiables), puis :
  `python3 tools/make_gameplay_reel.py captures/<fichier> cartes.json reels/AAAA-MM-JJ-gameplay.mp4 <graine> <début_s> <durée_s>`
  (durée 15 à 30 s). Regarde l'aperçu `-apercu.jpg` avec Read (pas de scène qui spoile l'histoire, texte lisible),
  supprime-le et le JSON, commit le Reel et ajoute la ligne « date | fichier capture | reel » à `captures-utilisees.txt`.
- Ce Reel remplace le Reel info de 16h00 ce jour-là (même programmation : Instagram + Facebook avec un titre de la
  bibliothèque Instagram selon les règles ci-dessus, TikTok à 16h30, story à 17h00). Légende : l'astuce d'abord,
  question en fin, et « Capture NéoSoluce » ; ne jamais monétiser la vidéo elle-même (pas de partenariat sur ces Reels).
- Une capture peut servir 2 fois maximum (deux passages différents, encarts différents).
- Si `captures/` est vide après le 19 novembre, rappelle à Noah dans le récap comment déposer ses captures (captures/README.md).
