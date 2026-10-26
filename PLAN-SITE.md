# Plan site NéoSoluce : objectif « référence GTA VI n°1 FR/BE » (audit du 26/10/2026)

Classement par impact sur le trafic et les revenus. Effort : S (moins d'1 h), M (quelques heures), L (plusieurs jours). « Claude seul » = faisable par les agents sans action de Noah.

## État des lieux (26/10/2026)
- Note globale : 7/10. Contenu solide et sourcé (21 articles, page pilier id 29 très complète, statuts Officiel/Rapporté/Rumeur respectés, aucune date de sortie erronée trouvée), SEO de base propre (titres, méta, catégorie unique, maillage correct vers et depuis le hub).
- Points faibles : trafic encore très faible (environ 205 vues du 12 au 19/10) ; plus aucun article publié depuis le 23/10 (agent Rédaction à l'arrêt) ; monétisation fragile (WordAds non vérifiable par les outils, pas de mention Amazon dans le pied de page) ; animation d'intro plein écran à la première visite (jusqu'à 3,6 s, pénalisante sur mobile) ; aucune page « jour J » prête (soluce, argent, codes, 100 %, trophées).
- Réalité des revenus : avec WordAds seul, 200 € nets en novembre demandent de l'ordre de plusieurs dizaines de milliers de pages vues (estimation, dépend du RPM). Le levier réaliste est le pic de recherche du 12 au 30/11 : il faut que les pages qui captent ces requêtes existent et soient indexées AVANT le 19/11.

## Chantiers classés par impact

### 1. Relancer la production et préparer les pages piliers de lancement (impact : très fort ; effort L ; Claude seul)
- Vérifier pourquoi l'agent Rédaction ne publie plus depuis le 23/10 (tâche planifiée, quotas). Action Noah : regarder l'état des tâches planifiées.
- Suivre la file d'articles datée du 27/10 au 30/11 (agents/1-redaction.md, section « File d'articles datée », issue de ETUDE-AUDIENCE.md) : un article par jour, 3 brouillons jour J préparés avant le 19/11.
- Les URL « jour J » doivent exister et être indexées avant le 19/11 (même avec un contenu d'attente honnête : « ce qu'on sait, mis à jour en continu ») pour capter le trafic des premiers jours.

### 2. Pages « jour J » mises à jour en continu du 19 au 30/11 (impact : très fort ; effort L ; Claude seul)
- Soluce complète, argent rapide, codes de triche, 100 % et collectibles, trophées et succès, carte complète, meilleurs véhicules, ce que disent les tests.
- Méthode : recoupement de 2 sources fiables minimum (règles de 1-redaction.md), mise à jour plusieurs fois par jour la première semaine, « Mis à jour le » visible.
- Mettre ces pages en avant sur l'accueil (bloc « Jour J ») et dans le hub id 29.

### 3. Monétisation (impact : fort ; effort S à M)
- Action Noah : vérifier dans wp-admin (Outils > Monétisation / WordAds) que les publicités sont activées et approuvées ; aucune pub n'apparaît dans la lecture texte du site.
- Mention « En tant que Partenaire Amazon… » dans le pied de page (texte seul) : la modification automatique a été refusée par la protection des actions partagées ; Noah peut l'autoriser ou l'ajouter lui-même dans l'éditeur du site (Pied de page, dernière ligne).
- Agent Monétisation : guide d'achat « SSD, manette, casque pour GTA 6 » (liens neosoluce-21 et neosoluce00-21, aucune image officielle à côté des liens), encart d'achat dans la checklist (id 252) et l'article taille (id 165), page Précommander (id 225) à tenir à jour (prix relevés, date).
- Après le 19/11 : remplacer « Précommander » par « Acheter GTA 6 » dans le menu et sur la page 225 (même URL, texte mis à jour).

### 4. Mobile et parcours accueil vers guides (impact : moyen à fort ; effort M ; validation Noah)
- Animation d'intro (template part nsx-splash) : la limiter (déjà une fois par visiteur) ou la supprimer ; elle masque l'écran à la première visite, retarde la lecture et peut gêner l'affichage des pubs et les signaux Core Web Vitals. Le bloc de débogage caché « NSX: le script ne tourne pas » est lu par les robots : à retirer. Décision de Noah (design).
- Accueil : remplacer progressivement les 6 « derniers guides » par un bloc « Jour J » (checklist, heure de sortie, taille, codes, argent) puis, après le 19/11, par les guides de lancement.
- Menu : « Guides GTA 6 » vers une vraie page index des guides classés par thème (Commencer, Carte, Argent, Véhicules, Armes, Online) plutôt que l'archive de catégorie.
- Commentaires : la zone « Chargement des commentaires… » apparaît sur l'accueil ; vérifier son utilité.

### 5. Visibilité Google et distribution (impact : fort ; effort S récurrent ; Noah + Claude)
- Action Noah : Search Console, demander l'indexation des nouvelles pages piliers (10 URL par jour max), vérifier la couverture.
- Images : illustrer chaque pilier avec 1 à 3 images officielles « gtavi- » (les 40 ont désormais texte alternatif et légende © Rockstar Games), jamais à côté d'un lien Amazon ; images larges (≥ 1200 px) favorables à Google Discover.
- Pinterest et réseaux : une épingle et un post par pilier publié ; lien de la page pilier en bio.

### 6. Qualité continue (impact : moyen ; effort S ; Claude seul)
- Étiquettes : chaque article a maintenant 1 à 4 étiquettes cohérentes ; ne pas en créer de nouvelles sans vérifier tags.list.
- Méta : toutes les pages et articles ont une méta-description ; garder 130 à 155 caractères.
- Harmoniser progressivement le tutoiement dans les anciens articles (5, 6, 32) lors de leurs mises à jour normales.

## Journal des corrections appliquées le 26/10/2026 (audit)
| Élément | Avant | Après |
|---|---|---|
| Médias 259 à 298 (40 images gtavi-) | texte alternatif vide, aucune légende | texte alternatif descriptif + légende « Image officielle © Rockstar Games » |
| Page 225 Précommander | page courte (boutons + 1 ligne), sans méta, sans mention Amazon officielle | contenu enrichi (prix officiels, Pack Vintage, préchargement, boîte sans disque, GTA+, FAQ, liens internes, sources), méta-description, titre SEO, extrait, mention Partenaire Amazon |
| Article 78 Francophonie | pas de mention Partenaire Amazon malgré 4 liens Amazon ; titre SEO vide ; méta 167 caractères ; schéma vide ; aucune étiquette | mention ajoutée ; bloc « À lire aussi » (checklist, taille, PC) ; titre SEO ; méta 140 caractères ; schéma « article » ; 2 étiquettes |
| Articles 5, 6, 28, 32, 33, 34, 35, 68, 137 | aucune étiquette | 1 à 4 étiquettes |
| Étiquettes créées | - | GTA 6 Online, Date de sortie GTA 6, Prix et éditions GTA 6, Carte GTA 6, Véhicules GTA 6, Missions GTA 6, Radios GTA 6, Gameplay GTA 6 |
| Articles 85 et 127 | titre SEO vide | titre SEO renseigné |
| Pages 1, 20, 21, 22 | méta-description vide | méta-description renseignée |
| Article 32 | - | lien interne ajouté puis retiré (doublon d'un lien existant) : aucun changement net |
| Pied de page (assembler//footer) | sans mention Amazon | NON modifié : action refusée par la protection, à valider par Noah |
| NeoSoluce-images-site.zip | absent de la médiathèque | rien à supprimer |
