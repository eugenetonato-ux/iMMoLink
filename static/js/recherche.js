/* ==========================================================================
   iMMoLink — recherche.js
   Petite amélioration progressive de la page de recherche : soumission
   automatique du formulaire de filtres quand un select change, pour éviter
   un clic supplémentaire sur mobile.
   ========================================================================== */

(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".filters-bar");
    if (!form) return;

    form.querySelectorAll("select").forEach(function (select) {
      select.addEventListener("change", function () {
        form.requestSubmit();
      });
    });
  });
})();
