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

## Publications avec les images OFFICIELLES de Rockstar (dossier `officiel/`, dès maintenant)
Noah dépose dans `officiel/` les images téléchargées sur https://www.rockstargames.com/VI/media (voir officiel/README.md).
Rockstar/Take-Two tolère l'usage de ses contenus par les fans SANS BUT COMMERCIAL : on les utilise donc uniquement
sur Instagram, Facebook et TikTok, en publication de fan, avec ces règles strictes :
- jamais sur une publication sponsorisée, en partenariat, boostée, ni avec un lien Amazon ou un code promo ;
  la légende apporte une info et pose une question ; elle peut citer « Plus d'infos : neosoluce.com » une fois, sans « achetez » ;
- crédit « Image officielle © Rockstar Games » toujours visible (le script l'ajoute) et rappelé en fin de légende ;
- image non déformée, pas de spoiler, jamais une image qui ne vient pas du site officiel de Rockstar ;
- jamais sur le site neosoluce.com tant que Take-Two n'a pas accordé de licence écrite (demande envoyée à copyright@take2games.com) ;
- en cas de demande de retrait de Rockstar/Take-Two : retirer immédiatement et le signaler en tête du récap.
Vidéos officielles : `officiel/videos/` contient les clips officiels publiés par Rockstar sur la même page
(portraits animés des personnages de 1 à 1,5 s, jaquette animée). Mêmes règles que les images, crédit
« Vidéo officielle © Rockstar Games » (ajouté par le script), son d'origine toujours coupé. Dans cartes.json, une entrée
`{"video": "officiel/videos/<fichier>.mp4", "x": 0.5, ...}` remplace `"image"` ; `x` (0 = gauche, 1 = droite) règle le
recadrage : vérifie dans l'aperçu que le visage est dans le cadre. Jaquette : `"cadre": "entier", "largeur": 0.45,
"debut": 16.5` (jamais la fin de la vidéo avec « Pre-order now »). Les personnages déjà présentés par Rockstar
(Jason Duval, Lucia Caminos, Cal Hampton, Boobie Ike, Dre'Quan Priest, Real Dimez, Raul Bautista, Brian Heder) :
décris-les uniquement avec ce que dit leur fiche officielle. Jamais de trailer, ni d'extrait de trailer.
Formats (python3 tools/make_official.py) :
- `post`  : post Instagram/Facebook 1080x1350 avec encart néon (badge, titre ≤ 40 car., texte ≤ 90 car.) ;
- `story` : story 1080x1920 (même encart) ;
- `reel`  : Reel de 3 à 6 images officielles avec zoom lent, encarts et musique originale :
  `python3 tools/make_official.py reel cartes.json reels/AAAA-MM-JJ-officiel.mp4 <graine>` avec
  cartes.json = [{"image": "officiel/<fichier>", "badge": "...", "titre": "...", "texte": "..."}, ...].
Rythme : quand `officiel/` contient des images, le Reel info de 16h00 utilise de préférence `make_official.py reel`
(un jour sur deux au moins), et la story « question du jour » de 12h30 peut utiliser `make_official.py story`
au lieu de Canva. Varie les images (liste dans `officiel-utilisees.txt` : date | image | publication ; une image
au maximum une fois par semaine). Chaque fait écrit sur l'image doit être vérifié dans une source fiable et
correspondre à ce qu'on voit, sans inventer de détail sur l'image.
Si `officiel/` est vide, rappelle une fois par semaine à Noah, dans le récap, comment le remplir (officiel/README.md).

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
