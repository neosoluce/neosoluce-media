# Agent Contrôle du soir (21h26) : rien ne doit rater

Ta mission : vérifier que tout ce qui était prévu aujourd'hui a bien été publié et que le site fonctionne, réparer ce qui peut l'être ce soir, et préparer le lendemain.

## Vérifications
0. Visuels officiels : getScheduledPosts sur aujourd'hui et les jours suivants déjà programmés (brouillons compris). Toute publication non publiée avec un visuel officiel Rockstar/Take-Two (fichiers de officiel/, Reels « -officiel » ou « -personnages », visuels make_official.py, crédit « © Rockstar Games ») → passe-la en brouillon avec updateScheduledPost (draft true, autoPublish false ; Metricool gratuit : pas de révision ; ne supprime jamais) et liste-la dans ta section du journal du lendemain pour le récap (COMMUN.md « Visuels : règle unique »). Ne la reprogramme jamais en réparation.
1. getScheduledPosts sur la journée (00h00 à 23h59, Europe/Berlin) : pour chaque publication passée, statut « PUBLISHED ». Toute publication en erreur ou restée « PENDING » plus d'une heure après son heure : note-la.
2. Le Reel du compte à rebours du jour existe-t-il (J-N) ? Le Reel du jour ? Les stories ? Compare avec le journal de l'agent Vidéo et de l'agent Réseaux.
3. Réparation : si une publication importante a échoué (compte à rebours, Reel du jour, post de l'article), reprogramme-la une seule fois ce soir (au plus tôt 15 minutes plus tard, avant 23h30) avec le même média et le même texte, sans dépasser les limites de COMMUN.md ; si le Reel du compte à rebours du jour n'existe pas du tout et que le fichier reels/AAAA-MM-JJ-jN.mp4 n'existe pas, génère-le selon agents/2-video.md et REELS.md, puis programme-le avant 23h00. Ne crée rien d'autre.
4. Site : WebFetch sur https://neosoluce.com et sur l'article du jour : la page répond, le titre de l'accueil, la recherche et les derniers guides apparaissent. Signale toute anomalie.
5. Demain : getScheduledPosts sur le lendemain ; note s'il y a des doublons ou un dépassement de limite.
6. Écris dans le journal du LENDEMAIN (journal/AAAA-MM-JJ.md de demain) une section « ## Contrôle du soir (veille) » : ce qui a été publié, ce qui a échoué, ce que tu as réparé, ce qui reste à faire et pour quel agent. L'agent Business l'intègre au récap.
7. Si un problème grave touche le site (site inaccessible, page d'accueil cassée) ou une demande de retrait de Rockstar/Take-Two non traitée : envoie tout de suite un court e-mail à Noah (adresse dans ton message de lancement), sujet « NéoSoluce – alerte ».
