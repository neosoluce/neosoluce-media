# Sources des taux et barèmes (consultées le 14/10/2026)

| Paramètre (calc.js) | Valeur 2026 | Source | Statut |
|---|---|---|---|
| Wallonie, taux normal | 12,5 % | notaire.be, « Droits d'enregistrement en Région wallonne » : https://www.notaire.be/immobilier/acheter-et-vendre-un-bien-immobilier/les-frais-lies-lachat/droits-denregistrement-en-region-wallonne | Officiel (Fednot) |
| Wallonie, taux réduit habitation propre et unique | 3 % (actes depuis le 1/1/2025, sans plafond) | Wallonie, FAQ réforme : https://www.wallonie.be/sites/default/files/2024-12/Réforme_droits_enregistrement-FAQ.pdf ; https://wallonie.be/fr/vivre-en-wallonie/habitat-et-energie/fiscalite-immobiliere | Officiel |
| Wallonie, conditions | pleine propriété ; pas d'autre logement en pleine propriété (ou vente dans les 3 ans) ; domicile dans les 3 ans (5 ans terrain/sur plan) ; 3 ans minimum ; sinon +9,5 % | idem | Officiel |
| Bruxelles, taux | 12,5 % | be.brussels : https://be.brussels/fr/impots-financement/impots-et-taxes/fiscalite-immobiliere/droits-denregistrement/abattement-sur-les-droits-de-vente | Officiel |
| Bruxelles, abattement habitation | 200 000 €, prix ≤ 600 000 € (tout ou rien) | idem + notaire.be : https://www.notaire.be/immobilier/les-droits-denregistrement-abattements-et-taux-reduits/droits-denregistrement-en-region-de-bruxelles-capitale | Officiel |
| Bruxelles, abattement terrain | 100 000 €, prix ≤ 300 000 € | idem | Officiel |
| Honoraires : tranches successives | 7 500 / 10 000 / 12 500 / 15 495 / 18 595 / 186 005 / 249 905 / surplus | Tarif consolidé Fednot 9/02/2026 : https://www.notaire.be/sites/default/files/files/2026-02/20260209%20-%20Tariefbesluit%20geconsolideerde%20versie%20FR.pdf ; AR 22/11/2022 : https://etaamb.openjustice.be/fr/arrete-royal-du-22-novembre-2022_n2022042846.html | Officiel |
| Barème J (vente) | fixe 285 € ; 2,5 / 2,5 / 1,75 / 1,71 / 1,14 / 0,57 / 0,2 / 0,2 % | idem | Officiel |
| Barème Jbis (habitation propre et unique, aucun autre droit immobilier) | fixe 257 € ; 2,5 / 2,5 / 2 / 1,5 / 0,5 / 0,485 / 0,3 / 0,2 % | idem | Officiel |
| Barème G (crédit) | fixe 285 € ; 0,75 / 0,65 / 0,5 / 0,4 / 0,4 / 0,228 / 0,046 / 0,046 % | idem | Officiel |
| Barème Gbis (crédit, mêmes conditions que Jbis) | pas de partie fixe ; 1,368 / 1,094 / 0,73 / 0,547 / 0,365 / 0,182 / 0,036 / 0,036 % | idem | Officiel |
| Frais administratifs forfaitaires | 855 € HTVA (1er acte) ; 627 € (acte lié) | idem (art. 2 §2) ; confirmé par https://www.clnotaires.be/indexation-au-1-1-2026/ (813 → 855 ; 596 → 627) | Officiel |
| TVA | 21 % | notaire.be : https://www.notaire.be/actualites/frais-dactes-notaries | Officiel |
| Transcription hypothécaire | 285 € | infofiches Fednot (ci-dessous) ; indexation SPF Finances 1/1/2024 | Officiel |
| Débours achat | 304 € | infofiche Fednot Wallonie, exemple à 250 000 € : https://www.notaire.be/immobilier/brochures/downloads/259 | ESTIMATION (varie selon dossier) |
| Droit d'écriture et annexes (achat) | 200 € (dont 100 € inclus dans la base TVA, reconstitué depuis l'exemple Fednot) | idem ; droit d'écriture 100 € : https://www.dekamer.be/FLWB/pdf/55/2624/55K2624001.pdf | ESTIMATION partielle |
| Crédit : droit d'enregistrement | 1 % de (capital + 10 % d'accessoires) | notaire.be : https://www.notaire.be/immobilier/acheter-et-vendre-un-bien-immobilier/les-frais-lies-lachat/les-frais-lies-au-credit-hypothecaire | Officiel (10 % = valeur « habituelle ») |
| Crédit : droit d'inscription | 0,30 % même base | idem | Officiel |
| Crédit : rétribution d'inscription | 270 € si inscription ≤ 300 000 € ; 1 160 € au-delà | https://www.clnotaires.be/indexation-au-1-1-2026/ | NON OFFICIEL (étude notariale) — notaire.be indique encore « 230 € ou 985 € » (montants anciens) |
| Crédit : droit d'écriture | 100 € | Chambre, doc 55K2624/001 | Officiel |

## Exemples de vérification (tests/test.js — 32/32 OK)
1. Infofiche Fednot « Acheter une habitation en Wallonie » : 250 000 €, 12,5 %, barème J → 36 089 € (reproduit à l'euro, avec les forfaits 2024 : J fixe 271 €, frais 813 €).
2. Infofiche Fednot « Acheter une habitation à Bruxelles » : https://notaire.be/immobilier/brochures/downloads/260 — 250 000 €, barème Jbis → 35 719 € (reproduit à l'euro).
3. Tableaux notaire.be Wallonie (200 k à 500 k, 12,5 % / 3 %) et Bruxelles (250 k à 650 k avec abattement).

## Points non confirmés
- Relèvement du plafond bruxellois à 800 000 € : annoncé (La Libre, 13/02/2026), non en vigueur selon be.brussels et notaire.be au 14/10/2026. Non appliqué.
- Débours et annexes : montants de l'exemple Fednot (2024-2025), non publiés pour 2026.
- Débours propres à l'acte de crédit (certificats) : non inclus.
- Base des honoraires de crédit : capital emprunté (hypothèse de lecture du tarif, non confirmée par un exemple officiel).
- Calculateur officiel notaire.be (calculator.notaris.be) : inaccessible depuis l'environnement de travail ; pas de comparaison directe.

## Maintenance
Vérifier chaque 1er janvier (indexation des forfaits tous les 2 ans : prochaine au 1/1/2028) et à chaque réforme régionale.
