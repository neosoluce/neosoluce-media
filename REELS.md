# Règles des Reels NéoSoluce (à lire par l'agent avant chaque Reel)

**Lis aussi FRANCOPHONIE.md (même dépôt) et applique-le à tout le passage : site, articles et réseaux.**

**Avant de programmer quoi que ce soit** : appelle getScheduledPosts pour le jour visé. Des publications ont pu être
programmées à l'avance (par Noah ou une session précédente) : compte-les dans la limite de 3 publications par réseau
et par jour (stories à part). S'il y a déjà un Reel programmé ce jour-là, n'en crée pas un deuxième.

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
Les captures que Noah filme sur sa propre console sont déposées dans le dossier `captures/` de ce dépôt
(voir captures/README.md). Jamais de vidéo d'un autre créateur ni de vidéo qui a fuité.
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

## Images et vidéos OFFICIELLES de Rockstar : INTERDITES (règle en vigueur, voir agents/COMMUN.md « Visuels : règle unique »)
Aucun visuel officiel Rockstar/Take-Two (captures, artworks, jaquette, portraits et clips de personnages, trailers,
extraits de trailer, logos, fichiers du dossier `officiel/` et `officiel/videos/`) dans un Reel, un post, une story ou
une épingle, tant que Noah n'a pas confirmé explicitement par écrit une licence Take-Two (demande en cours, seules des
réponses automatiques reçues). Le crédit « © Rockstar Games » ne rend pas l'usage autorisé. `tools/make_official.py`
n'est plus utilisé ; `officiel/` et `officiel-utilisees.txt` sont conservés sans modification.
Autorisés : visuels générés par IA (néon Vice City, sans logo, sans texte, sans personnage existant), créations maison
(Reels `make_reel.py` / `make_info_reel.py`, Canva maison, Léona et les vidéos OpenArt de Noah), images libres de droits
à licence vérifiée. Un simple lien vers une vidéo YouTube officielle de Rockstar reste permis (partage ou intégration,
jamais de téléversement). Le Reel du jour de 16h00 est donc : Léona, sinon capture de Noah (après la sortie), sinon Reel
info néon.
Avant toute programmation, vérifie dans getScheduledPosts qu'aucune publication non publiée ne contient un visuel
officiel ; si c'est le cas, passe-la en brouillon (updateScheduledPost, draft true ; jamais de suppression) et signale-la
dans le journal « Pour Noah ».

## Léona, la mascotte (vidéos générées par Noah avec OpenArt)
Lis mascotte/LEONA.md (fiche personnage, ton, règles). Léona n'est jamais appelée « Leonida ».
- Chaque jour, dans le journal (section « Pour Noah », reprise dans le récap), propose à Noah UN script de Léona (18 à 24 mots, vraie info vérifiée avec source, chute
  joueuse) et le prompt OpenArt complet prêt à copier-coller : fiche fixe + tenue sexy mais habillée liée au sujet +
  décor + « She speaks in French with a confident, playful female voice, perfectly lip-synced: "<phrase écrite comme
  elle se prononce>" » + « No subtitles, no text, no letters anywhere. ». Note le script dans mascotte/scripts.txt
  (date | sujet | texte exact | texte prononcé).
- Si mascotte/videos/ contient une vidéo pas encore listée dans mascotte/utilisees.txt : retrouve son texte dans
  mascotte/scripts.txt (même sujet que le nom du fichier ; si tu ne le trouves pas, ne la publie pas et demande à Noah
  ce qu'elle dit), puis python3 tools/make_leona_reel.py mascotte/videos/<fichier> "<texte exact>" reels/AAAA-MM-JJ-leona.mp4,
  regarde l'aperçu avec Read (sous-titres lisibles, enseigne qui ne cache pas le visage), supprime l'aperçu, commit,
  ajoute la ligne « date | fichier | reel » à mascotte/utilisees.txt.
- Programmation : c'est le Reel du jour, Instagram + Facebook à 16h00 (garde la voix de Léona : PAS d'audioConfiguration Instagram,
  la voix est le son), instagramData isAiGenerated true, TikTok à 16h30 avec tiktokData isAigc true, story à 17h00. Compte-le
  dans la limite de 3 publications par réseau et par jour. Légende : l'info d'abord, une question, « Léona t'en dit
  plus sur neosoluce.com (lien en bio) », hashtags, puis « Vidéo générée par IA ». Jamais boostée ni sponsorisée.
