# Audit « prêt à gagner de l'argent » : NéoSoluce, 10/11/2026

Sortie de GTA VI : jeudi 19/11/2026. Semaine décisive : 19 au 26/11.
Méthode : Search Console (outils console gratuits, aucune dépense), API WordPress.com, journaux du dépôt (08 au 10/11), règles des agents. neosoluce.com n'est pas lisible directement depuis cette session (proxy 403) : ads.txt, sitemap et rendu des pubs n'ont pas pu être lus en direct.

## Verdict
**Le site n'est pas prêt à gagner de l'argent : le contenu et les liens d'affiliation sont en place, mais Google n'indexe que la page d'accueil et les réseaux n'envoient aucun visiteur. Sans trafic, ni WordAds ni Amazon ne peuvent rapporter. À ce jour, le seuil de 20 €/mois n'est pas atteignable avant décembre, sauf si l'indexation repart avant le 19/11.**

## 1. Indexation Google (priorité absolue)

### Constats (vérifiés le 10/11)
| URL | État Google | Dernier passage |
|---|---|---|
| / (accueil) | Indexée | 09/11 |
| article 5 date-heure-sortie | Explorée, non indexée | 14/10 |
| article 6 standard-ou-ultimate | Explorée, non indexée | 13/10 |
| article 28 Online | Explorée, non indexée | 14/10 |
| article 33 carte | Explorée, non indexée | 24/10 |
| article 78 francophonie (brouillon depuis le 26/10) | Explorée, non indexée | 24/10 |
| article 165 taille | Inconnue de Google | jamais |
| article 413 Lucia | Inconnue de Google | jamais |
| article 529 ordre des GTA | Inconnue de Google | jamais |
| article 539 préchargement | Inconnue de Google | jamais |
| page 29 (pilier) | Inconnue de Google | jamais |
| page 225 Précommander | Inconnue de Google | jamais |

- Sitemap : https://neosoluce.com/sitemap.xml, 143 URL, lu une seule fois par Google le 27/10, 0 erreur.
- Aucun noindex : indexation autorisée, robots.txt OK, canonicals corrects (Google retient la même URL que le site).
- Search Console : 17 clics et environ 540 impressions du 12 au 22/10 (article 5 en position 6, article 78 en position 7 sur les requêtes Belgique/Suisse), puis **zéro impression depuis le 23/10**.
- Journal d'activité WordPress du 20 au 24/10 : aucun changement de réglage (pas de passage en privé, pas de noindex). La chute vient donc de Google, pas d'une erreur de réglage.
- L'animation d'intro (nsx-splash) ne se lance pas pour les robots (filtre « bot ») : elle n'est pas en cause.

### Cause probable (diagnostic)
1. **Site neuf sans autorité** : domaine lancé le 12/10, aucun lien externe connu. Google a testé les pages quelques jours (« prime de nouveauté »), puis les a retirées de l'index le 23/10. C'est le schéma classique d'un site neuf sur un sujet ultra concurrentiel (GTA 6 est couvert par tous les grands médias).
2. **Contenu jugé peu différenciant** : beaucoup d'articles « ce qu'on sait » proches de ceux des grands sites, plusieurs intentions qui se recoupent (78 et 5, 252 et 165, 137 et 132, 33 et 247), et des pages mises à jour presque tous les jours.
3. **Exploration minimale** : Google ne repasse presque plus (aucune nouvelle URL découverte depuis fin octobre, sitemap lu une fois), donc même les bons nouveaux articles ne sont pas vus.
4. **Une URL qui marchait a été tuée** : l'article 78 (153 impressions, position 7) a été mis en brouillon le 26/10 ; sur ce forfait il n'y a pas de redirection, l'URL renvoie une erreur.

### Ce qui relève seulement du temps ou de liens externes
Le point 1 ne se corrige pas par un réglage. Il faut : des liens externes (forums, Reddit francophones, sites de jeux, Discord, annuaires de fans), des signaux de marque (recherches « neosoluce »), et du temps (souvent plusieurs semaines). Honnêtement : il est probable que Google n'indexe pas massivement le site avant le 19/11.

### Corrigé aujourd'hui
- Sitemap principal resoumis + news-sitemap.xml soumis (articles des 2 derniers jours).
- Nouvelle page /liens (id 572) qui relie les 5 guides clés, Précommander et les 22 articles publiés : plus aucun article sans lien entrant, et une page de destination unique pour les réseaux.

## 2. Publicités WordAds
- Non vérifiable depuis cette session : ads.txt et rendu des pubs illisibles (proxy), et l'API ne donne pas le statut WordAds. Les mentions légales et la page Confidentialité annoncent WordAds et un bandeau de consentement.
- **À vérifier par Noah (2 min)** : WordPress.com > Monétiser > Publicités : activées ? approuvées ? ; ouvrir neosoluce.com/ads.txt sur l'iPhone (doit lister des lignes « wordpress.com » ou équivalent).
- Risque de refus : faible. Contenu sur un jeu PEGI 18, sans images choquantes repérées dans les titres et images listées ; sujets « police », « armes », « braquages » restent descriptifs. Images officielles Rockstar : voir section 6.
- **Estimation des revenus** (RPM = revenu pour 1 000 pages vues ; WordAds ne publie pas ses RPM ; pour un petit site jeux vidéo francophone, hypothèse 1 à 4 €, retenue 2 €) :
  | Objectif mensuel | Pages vues nécessaires (RPM 2 €) | Fourchette (RPM 4 € à 1 €) |
  |---|---|---|
  | 20 € | 10 000 | 5 000 à 20 000 |
  | 200 € | 100 000 | 50 000 à 200 000 |
  | 500 € | 250 000 | 125 000 à 500 000 |
  Trafic actuel : environ 50 pages vues par mois. Sources générales sur le RPM display : MonetizeMore (https://www.monetizemore.com/blog/website-ad-revenue), Clickio (https://blog.clickio.com/what-is-rpm/), Aditude (https://www.aditude.com/blog/rpm-for-publishers). Ce sont des ordres de grandeur, pas des chiffres WordAds.

## 3. Affiliation Amazon
### Liens vérifiés (contenu brut des pages)
| Page | Liens | Tag | Mention légale |
|---|---|---|---|
| 225 Précommander | 4 boutons : amazon.fr PS5 B0GZW5D8YF, Xbox B0GZW3TCF7 ; amazon.com.be PS5 B0GZH9BJYD, Xbox B0GZVXB4DX | neosoluce-21 (.fr), neosoluce00-21 (.be) : corrects | oui (haut et bas) + rel sponsored |
| 5 date et heure | même encart 4 boutons + liens texte PS5/Xbox + SSD | idem | oui |
| 6 Standard ou Ultimate | même encart + liens texte | idem | oui |
| Pied de page | - | - | mention Partenaire Amazon présente |
| 78 | brouillon (hors ligne) | - | - |
Non vérifié : que chaque fiche est en stock et que le lien répond (amazon non lisible depuis cette session). À faire par Noah : toucher chaque bouton de la page 225 sur l'iPhone.

### Règles qui menacent le compte
- **3 ventes qualifiées dans les 180 jours** suivant l'inscription, sinon le compte est clôturé (il faut alors se réinscrire). Sources : https://techtactician.com/amazon-affiliate-3-sales-in-180-days , https://www.leptidigital.fr/logiciels/amazon-partenaires/ . Date d'inscription des deux comptes : à vérifier par Noah dans le tableau de bord Partenaires.
- **Interdit : afficher un prix Amazon écrit en dur** (prix figé non mis à jour). Corrigé : la ligne « Amazon 60 € » du tableau de la page 225 est retirée. À corriger plus tard : article 6 (« Amazon » cité dans une liste d'enseignes à 60 €) et article 5 (même mention), sans urgence car ce n'est pas un prix affiché à côté du lien.
- Interdit : liens dans les e-mails, newsletters, PDF ou messages privés ; liens raccourcis masqués ; inciter à cliquer (« clique pour nous soutenir ») ; acheter soi-même via ses liens.
- Obligatoire : mention « En tant que Partenaire Amazon… » visible (présente) et lien vers la fiche réelle.

### Page Précommander (id 225) : état et version jour J
- Corrigé aujourd'hui : préchargement « dès le 12 novembre » → « ouvert depuis le 10 novembre, jusqu'à 212 Go » (liste + FAQ), avec lien vers l'article 539 ; ligne « Amazon 60 € » retirée.
- **Version jour J (à appliquer le 19/11 au matin, même URL /precommander-gta-6/)** :
  - Titre : « Acheter GTA 6 : prix, éditions et où le trouver » ; titre SEO : « Acheter GTA 6 (PS5, Xbox) : prix et où le trouver ».
  - Menu (navigation id 7) : « 🎮 Précommander » → « 🎮 Acheter GTA 6 » ; bouton de l'accueil idem.
  - 1er paragraphe : « Mis à jour le 19/11/2026 : GTA 6 est sorti aujourd'hui sur PS5 et Xbox Series X|S. » + « le Pack Vintage Vice City reste offert pour tout achat jusqu'au 20/11 (dernier jour). »
  - Encart : titre « 🎮 Acheter GTA 6 » ; mêmes 4 boutons et mêmes tags (vérifier chaque fiche le matin même).
  - Retirer : FAQ « Précommander donne-t-il accès plus tôt ? », phrases sur la livraison du 12/11 et le préchargement.
  - Ajouter : « Boîte ou numérique le jour J ? » (la boîte reste un code, il faut télécharger jusqu'à 212 Go) ; lien vers le guide débutant (N12) et la page /liens.
  - Après le 20/11 : retirer le Pack Vintage.
  - Méta : « Acheter GTA 6 sur PS5 ou Xbox : prix officiels, éditions Standard et Ultimate, boîte ou numérique et liens Amazon.fr et Amazon.be. »

### Contenus à forte intention d'achat
1. « SSD, manette, casque : les accessoires pour GTA 6 » (N9) : était prévu le 16/11, **avancé au 12/11** dans agents/1-redaction.md (les 212 Go rendent le SSD urgent maintenant).
2. « Quel SSD pour GTA 6 sur PS5 ? » : à intégrer comme section forte de N9 (pas d'article séparé, pour éviter le doublon).
3. « Carte PSN / Xbox : acheter GTA 6 moins cher en numérique » : proposé, non ajouté à la file (à valider : produit Amazon disponible selon le pays, commission faible).

## 4. Parcours réseaux → site
- Pourquoi 0 clic : (1) les carrousels donnent toute la réponse, rien ne pousse à cliquer ; (2) TikTok et Instagram n'ont pas de lien cliquable dans les légendes ; la légende renvoie vers « neosoluce.com (lien en bio) », mais le lien réellement en bio n'est pas connu des agents (non vérifiable via Metricool) ; (3) aucun commentaire épinglé ; (4) public TikTok jeune et mobile, qui reste dans l'appli.
- Règle de bio : rien dans le dépôt ne fixe le lien de bio. Désormais : **https://neosoluce.com/liens** partout.
- Dispositif retenu pour un compte de moins de 1 000 abonnés : lien en bio vers /liens + dernière page « question dont la réponse est sur le site » + commentaire épinglé (fait à la main par Noah) + story Instagram avec sticker lien (disponible pour tous les comptes). TikTok : le lien en bio demande en général un compte professionnel ou 1 000 abonnés selon le type de compte (à vérifier dans l'appli).
- agents/3-reseaux.md mis à jour (section « Règle trafic et quota »).

## 5. Machine de publication
- Les agents tournent : un article NEUF publié chaque jour (529 le 08/11, 531 le 09/11, 537 le 10/11). Le passage court de Rédaction du 10/11 a bien publié l'article 537 et ajouté un lien retour depuis 456.
- Erreurs récurrentes : add_repo indisponible (sans conséquence, dépôt déjà cloné) ; lecture de rockstargames.com et de certains médias refusée (faits officiels recoupés via la presse) ; boîte Gmail connectée = boîte personnelle (Business ne traite pas neosoluce.contact) ; Contrôle du soir, Vidéo, Pinterest, Monétisation en pause (sections absentes chaque jour, signalées en boucle par Business).
- Contradictions trouvées : (a) 4 posts par jour sur 4 réseaux contre un forfait Metricool gratuit de 20 posts par mois et par réseau : le quota Facebook est épuisé le 10/11 ; corrigé dans 3-reseaux.md ; (b) 3-reseaux.md dit à la fois « carrousel en brouillon pour Noah » et la mission du 04/11 qui programme les carrousels automatiquement (la règle prioritaire du 07/11 l'emporte : à nettoyer) ; (c) plusieurs pages disent encore « préchargement le 12 novembre » : priorité ajoutée dans 1-redaction.md.
- Semaine de lancement : file datée N12 à N23 prête (débuter, argent, bugs, soluce, tests…), mais **aucun brouillon jour J n'existe encore** (les seuls brouillons sont 78, 137 et 252, anciens). Ajouté en priorité dans 1-redaction.md.

## 6. Conformité et confiance
- Présents : Mentions légales (21), Confidentialité (22, RGPD, cookies, WordAds), Contact (20), À propos (1), Partenariats (48), mention « site de fans non affilié à Rockstar Games ni à Take-Two » dans le pied de page et sur les pages d'achat, mention Partenaire Amazon dans le pied de page.
- Bandeau cookies : annoncé dans la page Confidentialité (bannière WordPress.com) ; non vérifié visuellement.
- Images officielles : leur usage sur un site monétisé reste toléré mais non autorisé par Rockstar, qui peut demander un retrait à tout moment ; d'où la règle « jamais à côté d'un lien Amazon ».

## 7. Rentabilité
- Coûts : environ 20 €/mois (WordPress.com Premium payé au mois + domaine ; tarif exact non revérifié aujourd'hui). Metricool gratuit, agents compris dans l'abonnement Claude existant.
- Hypothèses : RPM WordAds 2 € ; Amazon ≈ 1,5 à 3 € de commission par jeu ou accessoire vendu (taux variable selon la catégorie, à vérifier sur la grille Partenaires) ; taux de clic vers Amazon 2 à 5 % des visiteurs des pages d'achat, conversion 5 à 10 %.

| Scénario | Semaine 19 au 26/11 | Décembre |
|---|---|---|
| Prudent (Google n'indexe toujours pas, réseaux = seule source) | 100 à 300 pages vues → 0 à 1 € | 300 à 1 000 pages vues → 0 à 3 € |
| Moyen (quelques pages indexées + clics réseaux grâce à /liens) | 2 000 à 5 000 pages vues + 2 à 5 ventes → 5 à 20 € | 5 000 à 15 000 pages vues → 10 à 40 € |
| Optimiste (pages jour J indexées tôt, Discover, une vidéo virale) | 20 000 à 50 000 pages vues + 15 à 30 ventes → 70 à 150 € | 50 000 à 100 000 pages vues → 100 à 250 € |

- Seuil de rentabilité (20 €/mois) : environ 10 000 pages vues par mois, ou 3 000 à 5 000 pages vues avec quelques ventes Amazon.
- Plus d'effet par minute investie : (1) lien de bio vers /liens + commentaire épinglé (5 min, effet immédiat sur le seul canal qui a de l'audience) ; (2) demander l'indexation des 10 URL clés dans Search Console (10 min) ; (3) poster les guides utiles dans 2 ou 3 communautés francophones (Reddit, Discord, forums) en respectant leurs règles (30 min, premiers liens externes) ; (4) vérifier WordAds (2 min). Plus d'effet par euro : ne rien acheter avant d'avoir du trafic ; un boost TikTok de 5 € vers /liens est le seul test payant raisonnable.

## Modifications appliquées le 10/11 (avant → après)
| # | Élément | Avant | Après |
|---|---|---|---|
| 1 | Search Console | sitemap lu une fois le 27/10 | sitemap.xml resoumis + news-sitemap.xml soumis |
| 2 | Page 225, liste « Ce qu'il faut savoir » | « Préchargement dès le 12 novembre 2026 » | « Préchargement ouvert depuis le 10 novembre 2026… jusqu'à 212 Go » + lien vers 539 et vers l'article taille |
| 3 | Page 225, tableau des enseignes | ligne « Amazon 60 € » (prix Amazon figé) | ligne retirée + phrase « pour Amazon, seul le prix affiché sur la fiche compte » |
| 4 | Page 225, FAQ « accès plus tôt » | « précharger dès le 12 novembre » | « précharger dès maintenant (ouvert depuis le 10 novembre) » |
| 5 | Article 5, section #precharge | « ouvre le jeudi 12 novembre » | « ouvert depuis le mardi 10 novembre », horaires PS5/Xbox, lien vers 539 |
| 6 | Article 5, paragraphe taille | « taille non annoncée, 120 à 130 Go » | « jusqu'à 212 Go (officiel) », conseils de téléchargement |
| 7 | Nouvelle page /liens (id 572) | absente | publiée : 5 guides clés, Précommander, 22 dossiers, mention fan site |
| 8 | agents/3-reseaux.md | aucune règle de bio, de boucle ouverte ni de quota | section « Règle trafic et quota » |
| 9 | agents/1-redaction.md | - | section « Priorités du 11 au 18/11 » (préchargement, N9 avancé au 12/11, brouillons jour J, maillage /liens, ne plus dépublier) |

## Non vérifié dans cette session
ads.txt, affichage et statut WordAds ; disponibilité et fonctionnement réel des 4 fiches Amazon ; lien actuel des bios TikTok/Instagram ; statistiques Metricool ; bandeau cookies à l'écran ; pages 29 et 6 en détail ; tarif exact du forfait WordPress.
