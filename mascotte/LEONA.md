# Léona, la mascotte de NéoSoluce

Léona est l'animatrice virtuelle de NéoSoluce. C'est un personnage 100 % original, créé pour NéoSoluce
(aucun élément appartenant à Rockstar Games). Son nom est un clin d'œil à Leonida, mais ce n'est pas Leonida :
ne l'appelle jamais « Leonida ».

## Fiche personnage (à garder IDENTIQUE dans chaque prompt)
Partie fixe, à copier telle quelle au début de chaque prompt vidéo ou image :

```
Original anthropomorphic female crocodile character with a sexy, confident glamour look: pastel pink crocodile head with glossy realistic scales, long snout, almond eyes with glamorous makeup, long lashes and glossy lips, athletic feminine figure.
```

Toujours présents : tête de crocodile rose pastel, maquillage glamour, créoles dorées, bijoux dorés.
La tenue change à chaque vidéo selon le sujet (toujours sexy mais habillée : pas de nudité, pas de pose suggestive appuyée).
Exemples déjà utilisés : maillot une pièce échancré turquoise/rose (plage), blazer blanc ouvert sur haut de bikini rose
(police, clin d'œil Miami Vice), chemise safari nouée + short en jean (carte), crop top à sequins + short métallisé +
casque de DJ (radios), chemise rose nouée + short en jean + chapeau de paille (marais).

## Personnalité
Confiante, séduisante, joueuse, un brin provocatrice, street-smart. Elle tutoie les joueurs, les appelle
« les criminels de Vice City », « chéri », « mon cœur ». Elle parle de « ses cousins » les alligators des marais de Leonida.
Ton d'experte : elle donne toujours une vraie info vérifiée.

## Format des vidéos (OpenArt)
- 9:16, haute résolution, 8 secondes, plan à la taille, face caméra, bouche bien visible.
- Elle parle en français, voix féminine confiante et joueuse, synchronisée.
- Script de 18 à 24 mots maximum : une accroche, une vraie info, une chute (question, clin d'œil, ou « NéoSoluce a le guide »).
- Dans la phrase dite, écrire les mots comme ils se prononcent : « GTA six », « GTA cinq », « Néo Soluce », nombres en lettres.
- Toujours terminer le prompt par : « No subtitles, no text, no letters anywhere. » (l'enseigne et les sous-titres sont ajoutés au montage).

## Règles
- Uniquement des infos vérifiées (Rockstar, presse reconnue). Une rumeur est toujours dite comme une rumeur.
- Jamais d'image officielle de Rockstar, de logo GTA, ni de personnage du jeu dans la scène.
- Vidéos signalées comme contenu IA sur Instagram (isAiGenerated true) et TikTok (isAigc true).
- Montage : python3 tools/make_leona_reel.py video.mp4 "sous-titre exact" reels/AAAA-MM-JJ-leona.mp4
  (garde la voix d'origine, ajoute la pastille NÉOSOLUCE, le nom « Léona », les sous-titres et la mention IA).
