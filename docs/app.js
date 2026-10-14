(function () {
  "use strict";
  var F = window.FraisAchat;
  var $ = function (id) { return document.getElementById(id); };
  var eur = new Intl.NumberFormat("fr-BE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
  var eur2 = new Intl.NumberFormat("fr-BE", { style: "currency", currency: "EUR", minimumFractionDigits: 2, maximumFractionDigits: 2 });
  var nbr = new Intl.NumberFormat("fr-BE", { maximumFractionDigits: 0 });

  var COND = {
    wallonie: {
      label: "J'achète mon habitation propre et unique (taux réduit de 3\u00a0%)",
      html: "<ul><li>Acheter le bien en pleine propriété (100 % du bien avec les co-acquéreurs).</li>" +
        "<li>Ne pas être déjà plein propriétaire de la totalité d'un autre logement, en Belgique ou à l'étranger, sauf engagement de le vendre dans les 3 ans.</li>" +
        "<li>Se domicilier dans le bien dans les 3 ans (5 ans pour un terrain à bâtir ou un bien sur plan) et y rester au moins 3 ans.</li>" +
        "<li>Sans plafond de prix. À défaut : complément de 9,5 % (différence entre 12,5 % et 3 %).</li></ul>"
    },
    bruxelles: {
      label: "J'achète mon habitation propre et unique (abattement de 200\u00a0000\u00a0€)",
      html: "<ul><li>Personne physique qui achète la totalité du bien en pleine propriété.</li>" +
        "<li>Prix maximum 600 000 € (300 000 € pour un terrain à bâtir, abattement de 100 000 €).</li>" +
        "<li>Ne pas être plein propriétaire d'un autre logement à la date du compromis (sinon restitution possible si revente dans les 2 ans).</li>" +
        "<li>Se domicilier dans le bien dans les 3 ans et y rester 5 ans sans interruption.</li></ul>"
    }
  };

  function parse(v) {
    var s = String(v || "").replace(/[\s  .]/g, "").replace(",", ".");
    if (!/^\d+(\.\d+)?$/.test(s)) return NaN;
    return Number(s);
  }
  function region() { return document.querySelector("input[name=region]:checked").value; }
  function typeBien() { return document.querySelector("input[name=type]:checked").value; }

  function setError(id, msg) { var el = $(id); el.textContent = msg || ""; el.hidden = !msg; }

  function row(l) {
    var est = l.estimation ? ' <span class="est">estimation</span>' : "";
    var d = l.detail ? '<span class="d">' + l.detail + "</span>" : "";
    return "<tr><th scope=\"row\">" + l.label + est + d + "</th><td>" + eur2.format(l.montant) + "</td></tr>";
  }

  function render() {
    var reg = region();
    $("hpu-label").textContent = COND[reg].label;
    $("hpu-cond").innerHTML = COND[reg].html;
    var terrain = typeBien() === "terrain";
    $("unique").disabled = terrain;
    $("unique").parentNode.style.opacity = terrain ? "0.55" : "";

    var prix = parse($("prix").value);
    if (!(prix >= F.PRIX_MIN) || prix > 50000000) {
      setError("prix-err", isNaN(prix) ? "Indiquez un prix en euros (chiffres uniquement)." : "Indiquez un prix entre 20 000 € et 50 000 000 €.");
      $("total").textContent = "—"; $("total-sub").textContent = "";
      return;
    }
    setError("prix-err", "");

    var avecCredit = $("avec-credit").checked;
    $("credit-zone").hidden = !avecCredit;
    var credit = 0;
    if (avecCredit) {
      credit = parse($("credit").value);
      if (!(credit > 0) || credit > 50000000) { setError("credit-err", "Indiquez le montant emprunté en euros."); credit = 0; }
      else setError("credit-err", "");
    }

    var res = F.calculer({
      region: reg, prix: prix, typeBien: typeBien(),
      habitationPropreUnique: $("hpu").checked,
      aucunAutreBien: $("unique").checked && !terrain,
      credit: credit
    });

    $("total").textContent = eur.format(res.total);
    $("total-sub").textContent = (credit ? "Achat " + eur.format(res.totalAchat) + " + crédit " + eur.format(res.totalCredit) + " · " : "") +
      "soit " + (res.total / prix * 100).toLocaleString("fr-BE", { maximumFractionDigits: 1 }) + " % du prix";

    var alerte = "";
    if (res.droits.avantagePerdu) alerte = "Le prix dépasse " + nbr.format(terrain ? 300000 : 600000) + " € : l'abattement bruxellois ne s'applique pas du tout (pas de réduction partielle).";
    $("alerte").textContent = alerte; $("alerte").hidden = !alerte;

    var ta = $("t-achat").tBodies[0];
    ta.innerHTML = res.lignesAchat.map(row).join("") +
      '<tr class="sub"><th scope="row">Total acte d\'achat</th><td>' + eur2.format(res.totalAchat) + "</td></tr>";
    var tc = $("t-credit");
    tc.hidden = !credit;
    tc.tBodies[0].innerHTML = credit ? res.lignesCredit.map(row).join("") +
      '<tr class="sub"><th scope="row">Total acte de crédit</th><td>' + eur2.format(res.totalCredit) + "</td></tr>" : "";
  }

  function reformat(e) {
    var v = parse(e.target.value);
    if (!isNaN(v)) e.target.value = nbr.format(Math.round(v));
  }

  var form = $("form");
  form.addEventListener("input", render);
  form.addEventListener("change", render);
  form.addEventListener("submit", function (e) { e.preventDefault(); render(); });
  $("prix").addEventListener("blur", reformat);
  $("credit").addEventListener("blur", reformat);
  render();
})();
