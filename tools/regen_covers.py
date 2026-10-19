"""Régénère toutes les couvertures d'articles avec leur scène thématique.
Usage : python3 tools/regen_covers.py [slug ...]  (sans argument : toutes)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_cover import make

# slug : (badge, titre, sous-titre, scène, accent)
COVERS = {
    "gta-6-date-sortie": ("SORTIE", "Heure de|sortie", "19 novembre 2026 : heure exacte en Belgique et en France, préchargement et astuces.", "calendrier", "cyan"),
    "gta-6-editions": ("ÉDITIONS", "Standard ou|Ultimate ?", "Prix, bonus de précommande et contenu de chaque édition : laquelle choisir ?", "editions", "soleil"),
    "gta-6-online": ("ONLINE", "GTA 6|Online ?", "Ce que Rockstar a dit, ce qui est rapporté et ce qui reste à confirmer.", "globe", "cyan"),
    "gta-6-gameplay": ("GAMEPLAY", "Gameplay|de GTA 6", "Police, vols de voitures, combats, relation et corps : tout ce qu'on sait.", "etoiles", "rose"),
    "gta-6-carte-leonida": ("CARTE", "La carte|de Leonida", "Vice City, Keys, Grassrivers : les régions, la taille et les lieux inspirés de la Floride.", "peninsule", "soleil"),
    "gta-6-vehicules": ("VÉHICULES", "Tous les|véhicules", "Voitures, motos, bateaux, hélicos et avions déjà confirmés pour GTA 6.", "voiture", "rose"),
    "gta-6-missions": ("MISSIONS", "Missions et|braquages", "Petits coups, gros braquages et choix : tout ce qui a été montré, sans spoiler.", "coffre", "rose"),
    "gta-6-francophonie": ("FRANCOPHONIE", "GTA 6 en|francophonie", "Belgique, France, Suisse, Québec : heure de sortie, prix et version française.", "globe", "soleil"),
    "gta-6-pc": ("PC", "GTA 6|sur PC ?", "Date, rumeurs et historique de Rockstar : ce qu'on sait vraiment de la version PC.", "ecran", "rose"),
    "gta-6-trailers": ("TRAILERS", "Trailers|décortiqués", "Détails, références et ce que Rockstar a vraiment montré dans ses vidéos.", "play", "rose"),
    "gta-6-trailer-lancement": ("TRAILER", "Trailer de|lancement", "Tout ce qu'on a appris du dernier trailer de GTA 6, plan par plan.", "play", "cyan"),
    "gta-6-armes": ("ARMES", "Les armes|de GTA 6", "Pistolets, fusils et lance-grenades repérés dans les trailers officiels.", "arme", "cyan"),
    "gta-6-taille-go-place-disque": ("TAILLE", "Combien|de Go ?", "Taille estimée, préchargement et astuces pour libérer de la place sur ta console.", "disque", "cyan"),
    "gta-6-codes-de-triche": ("CODES", "Codes de|triche ?", "Rockstar n'a rien annoncé : ce qu'on sait et les faux codes à éviter.", "manette", "rose"),
    "gta-6-activites-faune": ("ACTIVITÉS", "Activités|et faune", "Jet-ski, golf, plongée, 170 espèces animales : tout ce que Rockstar a détaillé.", "palmiers", "soleil"),
    "gta-6-radios": ("RADIOS", "Les radios|de GTA 6", "Les 6 stations officielles, leurs animateurs et les premiers titres confirmés.", "radio", "cyan"),
    "gta-6-personnages": ("PERSONNAGES", "Les personnages|de GTA 6", "Lucia, Jason et les rôles officiels : tout ce que Rockstar a présenté.", "cartes", "soleil"),
    "gta-6-tout-savoir": ("GUIDE", "Toutes les|infos GTA VI", "La page de référence : sortie, prix, carte, personnages, gameplay et FAQ.", "boussole", "rose"),
}
if __name__ == "__main__":
    for slug in (sys.argv[1:] or COVERS):
        b, t, sub, kind, acc = COVERS[slug]
        make(f"covers/{slug}.jpg", b, t, sub, kind, acc)
        print("ok", slug)
