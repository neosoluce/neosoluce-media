/*
 * Moteur de calcul des frais d'achat (Wallonie, Bruxelles) — paramètres 2026.
 * Aucune dépendance. Utilisable dans le navigateur (window.FraisAchat) et dans Node (require).
 * Chaque paramètre renvoie à une source listée dans SOURCES.md (clé "src").
 */
(function (root) {
  "use strict";

  // Tranches successives (largeurs en EUR) du tarif des honoraires des notaires,
  // annexe de l'AR du 16/12/1950, version consolidée Fednot du 9/02/2026.
  var TRANCHES = [7500, 10000, 12500, 15495, 18595, 186005, 249905, Infinity];

  var BAREMES = {
    // Vente de gré à gré (art. 17, point 81)
    J:    { pct: [2.5, 2.5, 1.75, 1.71, 1.14, 0.57, 0.2, 0.2] },
    Jbis: { pct: [2.5, 2.5, 2.0, 1.5, 0.5, 0.485, 0.3, 0.2] },
    // Ouverture de crédit / prêt (art. 17, point 53)
    G:    { pct: [0.75, 0.65, 0.5, 0.4, 0.4, 0.228, 0.046, 0.046] },
    Gbis: { pct: [1.368, 1.094, 0.73, 0.547, 0.365, 0.182, 0.036, 0.036] }
  };

  // Paramètres en vigueur en 2026 (indexation du 1/1/2026).
  var PARAMS_2026 = {
    id: "2026",
    partieFixe: { J: 285, Jbis: 257, G: 285, Gbis: 0 },
    forfaitAdminPremierActe: 855,   // frais administratifs forfaitaires (HTVA), acte de vente ou de financement
    forfaitAdminActeLie: 627,       // à partir du 2e acte lié du même dossier (ex. crédit signé avec l'achat)
    deboursAchat: 304,              // ESTIMATION : montant de l'exemple Fednot (recherches, certificats, urbanisme)
    transcription: 285,             // rétribution de transcription hypothécaire
    droitEcritureEtAnnexes: 200,    // ESTIMATION : exemple Fednot (droit d'écriture 100 € + annexes)
    partieTvaDroitEcritureAnnexes: 100, // reconstitution de la base TVA de l'exemple Fednot
    tva: 0.21,
    // Crédit hypothécaire
    accessoiresCredit: 0.10,        // accessoires usuels : 10 % du capital
    tauxEnregHypotheque: 0.01,      // droit d'enregistrement 1 %
    tauxInscriptionHypotheque: 0.003, // droit d'hypothèque 0,30 %
    retributionInscription: [{ jusqua: 300000, montant: 270 }, { jusqua: Infinity, montant: 1160 }],
    droitEcritureCredit: 100,
    // Droits d'enregistrement régionaux
    wallonie: { tauxNormal: 0.125, tauxReduit: 0.03 },
    bruxelles: {
      taux: 0.125,
      habitation: { abattement: 200000, plafond: 600000 },
      terrain: { abattement: 100000, plafond: 300000 }
    }
  };

  // Paramètres de l'indexation précédente (2024-2025) : servent UNIQUEMENT à rejouer
  // les exemples publiés par Fednot (brochures « Acheter une habitation en Wallonie / à Bruxelles »).
  var PARAMS_2024 = clone(PARAMS_2026);
  PARAMS_2024.id = "2024";
  PARAMS_2024.partieFixe = { J: 271, Jbis: 244, G: 271, Gbis: 0 };
  PARAMS_2024.forfaitAdminPremierActe = 813;
  PARAMS_2024.forfaitAdminActeLie = 596;

  function clone(o) { return JSON.parse(JSON.stringify(o, function (k, v) { return v === Infinity ? "Infinity" : v; }), function (k, v) { return v === "Infinity" ? Infinity : v; }); }

  function r2(x) { return Math.round(x * 100) / 100; }

  /** Honoraires proportionnels + partie fixe (HTVA). Base arrondie à l'euro supérieur (art. 4 du tarif). */
  function honoraires(bareme, montant, params) {
    var b = BAREMES[bareme];
    if (!b) throw new Error("Barème inconnu : " + bareme);
    var reste = Math.ceil(Math.max(0, montant));
    var prop = 0;
    for (var i = 0; i < TRANCHES.length && reste > 0; i++) {
      var part = Math.min(reste, TRANCHES[i]);
      prop += part * b.pct[i] / 100;
      reste -= part;
    }
    var fixe = params.partieFixe[bareme] || 0;
    // Réduction de la partie fixe pour petits montants (art. 6) : non gérée -> le calculateur exige un prix >= 20 000 €.
    return r2(prop + fixe);
  }

  /** Droits d'enregistrement sur l'acte d'achat. */
  function droitsEnregistrement(opts, params) {
    var prix = opts.prix;
    var terrain = opts.typeBien === "terrain";
    if (opts.region === "wallonie") {
      var reduit = !!opts.habitationPropreUnique;
      var taux = reduit ? params.wallonie.tauxReduit : params.wallonie.tauxNormal;
      return {
        montant: r2(prix * taux), base: prix, taux: taux, abattement: 0,
        libelle: reduit ? "taux réduit de 3 % (habitation propre et unique)" : "taux normal de 12,5 %",
        avantagePerdu: false
      };
    }
    if (opts.region === "bruxelles") {
      var regle = terrain ? params.bruxelles.terrain : params.bruxelles.habitation;
      var demande = !!opts.habitationPropreUnique;
      var eligible = demande && prix <= regle.plafond;
      var abatt = eligible ? Math.min(prix, regle.abattement) : 0;
      var base = prix - abatt;
      return {
        montant: r2(base * params.bruxelles.taux), base: base, taux: params.bruxelles.taux, abattement: abatt,
        libelle: eligible ? "12,5 % après abattement de " + abatt.toLocaleString("fr-BE") + " €" : "12,5 % sans abattement",
        avantagePerdu: demande && !eligible
      };
    }
    throw new Error("Région inconnue");
  }

  /**
   * Calcul complet.
   * opts = { region: "wallonie"|"bruxelles", prix, typeBien: "habitation"|"terrain",
   *          habitationPropreUnique: bool (avantage régional),
   *          aucunAutreBien: bool (barèmes réduits Jbis/Gbis — conditions fédérales),
   *          credit: montant du crédit (0 = sans crédit) }
   */
  function calculer(opts, params) {
    params = params || PARAMS_2026;
    var p = params;
    var lignesAchat = [];
    var de = droitsEnregistrement(opts, p);
    var baremeAchat = (opts.aucunAutreBien && opts.typeBien !== "terrain") ? "Jbis" : "J";
    var hon = honoraires(baremeAchat, opts.prix, p);
    var admin = p.forfaitAdminPremierActe;
    var baseTvaAchat = hon + admin + p.deboursAchat + p.partieTvaDroitEcritureAnnexes;
    var tvaAchat = r2(baseTvaAchat * p.tva);

    lignesAchat.push({ id: "droits", label: "Droits d'enregistrement", detail: de.libelle, montant: de.montant });
    lignesAchat.push({ id: "honoraires", label: "Honoraires du notaire (barème légal " + baremeAchat + ")", detail: "HTVA", montant: hon });
    lignesAchat.push({ id: "admin", label: "Frais administratifs (forfait légal)", detail: "HTVA", montant: admin });
    lignesAchat.push({ id: "debours", label: "Débours (recherches, certificats)", detail: "montant de l'exemple Fednot", montant: p.deboursAchat, estimation: true });
    lignesAchat.push({ id: "transcription", label: "Transcription hypothécaire", detail: "rétribution", montant: p.transcription });
    lignesAchat.push({ id: "ecriture", label: "Droit d'écriture et annexes", detail: "droit d'écriture 100 € + annexes", montant: p.droitEcritureEtAnnexes, estimation: true });
    lignesAchat.push({ id: "tva", label: "TVA 21 %", detail: "sur honoraires, frais et débours", montant: tvaAchat });

    var totalAchat = r2(sum(lignesAchat));

    var res = {
      params: p.id, region: opts.region, prix: opts.prix,
      droits: de, baremeAchat: baremeAchat,
      lignesAchat: lignesAchat, totalAchat: totalAchat,
      lignesCredit: [], totalCredit: 0, baremeCredit: null
    };

    var credit = Math.max(0, opts.credit || 0);
    if (credit > 0) {
      var baseHyp = r2(credit * (1 + p.accessoiresCredit));
      var baremeCredit = (opts.aucunAutreBien && opts.typeBien !== "terrain") ? "Gbis" : "G";
      var honC = honoraires(baremeCredit, credit, p);
      var adminC = p.forfaitAdminActeLie;
      var retrib = 0;
      for (var i = 0; i < p.retributionInscription.length; i++) {
        if (baseHyp <= p.retributionInscription[i].jusqua) { retrib = p.retributionInscription[i].montant; break; }
      }
      var lc = [];
      lc.push({ id: "c_enreg", label: "Droit d'enregistrement sur l'hypothèque (1 %)", detail: "sur " + fmt(baseHyp) + " (capital + 10 % d'accessoires)", montant: r2(baseHyp * p.tauxEnregHypotheque) });
      lc.push({ id: "c_inscr", label: "Droit d'inscription hypothécaire (0,30 %)", detail: "même base", montant: r2(baseHyp * p.tauxInscriptionHypotheque) });
      lc.push({ id: "c_retrib", label: "Rétribution d'inscription", detail: baseHyp <= 300000 ? "inscription ≤ 300 000 €" : "inscription > 300 000 €", montant: retrib });
      lc.push({ id: "c_ecriture", label: "Droit d'écriture", detail: "", montant: p.droitEcritureCredit });
      lc.push({ id: "c_hon", label: "Honoraires du notaire (barème légal " + baremeCredit + ")", detail: "HTVA", montant: honC });
      lc.push({ id: "c_admin", label: "Frais administratifs (forfait acte lié)", detail: "HTVA", montant: adminC });
      lc.push({ id: "c_tva", label: "TVA 21 %", detail: "sur honoraires et frais", montant: r2((honC + adminC) * p.tva) });
      res.lignesCredit = lc;
      res.totalCredit = r2(sum(lc));
      res.baremeCredit = baremeCredit;
      res.baseHypotheque = baseHyp;
    }
    res.total = r2(res.totalAchat + res.totalCredit);
    return res;
  }

  function sum(lignes) { return lignes.reduce(function (s, l) { return s + l.montant; }, 0); }
  function fmt(x) { return Math.round(x).toLocaleString("fr-BE") + " €"; }

  var api = {
    calculer: calculer, honoraires: honoraires, droitsEnregistrement: droitsEnregistrement,
    PARAMS_2026: PARAMS_2026, PARAMS_2024: PARAMS_2024, BAREMES: BAREMES, TRANCHES: TRANCHES,
    PRIX_MIN: 20000
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.FraisAchat = api;
})(typeof window !== "undefined" ? window : this);
