

(function () {
  "use strict";

  function debounce(fn, delay) {
    let timer = null;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  function buildQuartiersUrl(endpointTemplate, villeId) {
    // endpointTemplate ressemble à "/locations/quartiers/0/"
    return endpointTemplate.replace(/(\/)0(\/?)$/, `$1${villeId}$2`);
  }

  function findVilleId(villeInput) {
    if (villeInput.tagName === "SELECT") {
      const option = villeInput.options[villeInput.selectedIndex];
      return option ? option.dataset.id || null : null;
    }

    const datalist = villeInput.list;
    const valeur = villeInput.value.trim();
    if (!datalist || !valeur) return null;

    const option = Array.from(datalist.querySelectorAll("option")).find(
      (opt) => opt.value.trim().toLowerCase() === valeur.toLowerCase()
    );
    return option ? option.dataset.id || null : null;
  }

  function resetQuartierField(quartierInput, quartierDatalist, placeholder, lock) {
    if (lock) {
      quartierInput.value = "";
      quartierInput.disabled = true;
    }
    quartierInput.placeholder = placeholder;
    if (quartierDatalist) quartierDatalist.innerHTML = "";
  }

  function populateQuartiers(quartierInput, quartierDatalist, quartiers, lock) {
    quartierDatalist.innerHTML = "";
    quartiers.forEach((quartier) => {
      const option = document.createElement("option");
      option.value = quartier.nom;
      option.dataset.id = quartier.id;
      quartierDatalist.appendChild(option);
    });
    if (lock) quartierInput.disabled = false;
    quartierInput.placeholder = quartiers.length
      ? "Choisis un quartier"
      : "Aucun quartier référencé pour cette ville — saisis-le librement";
  }

  function initCascade(container) {
    const villeInput = container.querySelector('[data-role="ville"]');
    const quartierInput = container.querySelector('[data-role="quartier"]');
    const endpointTemplate = container.dataset.quartiersEndpoint;
    const lock = container.dataset.cascadeLock !== "false";

    if (!villeInput || !quartierInput || !endpointTemplate) return;

    const quartierDatalist = quartierInput.list;
    if (!quartierDatalist) return;

    const placeholderInitial = quartierInput.placeholder || "Choisis d'abord une ville";
    let currentVilleId = null;

    const handleVilleChange = debounce(function () {
      const villeId = findVilleId(villeInput);

      if (!villeId) {
        currentVilleId = null;
        resetQuartierField(quartierInput, quartierDatalist, placeholderInitial, lock);
        return;
      }

      if (villeId === currentVilleId) return; // déjà chargé, rien à refaire
      currentVilleId = villeId;

      if (lock) quartierInput.disabled = true;
      quartierInput.placeholder = "Chargement des quartiers…";

      fetch(buildQuartiersUrl(endpointTemplate, villeId), {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      })
        .then((response) => {
          if (!response.ok) throw new Error("Requête quartiers échouée");
          return response.json();
        })
        .then((data) => {
          // Le champ ville a pu changer pendant l'attente de la réponse.
          if (currentVilleId !== villeId) return;
          populateQuartiers(quartierInput, quartierDatalist, data.quartiers || [], lock);
        })
        .catch(() => {
          resetQuartierField(quartierInput, quartierDatalist, "Impossible de charger les quartiers", false);
        });
    }, 250);

    villeInput.addEventListener("input", handleVilleChange);
    villeInput.addEventListener("change", handleVilleChange);

    // Si la ville est déjà pré-remplie au chargement (ex: filtres conservés
    // après soumission, ou formulaire d'édition d'annonce), on déclenche la
    // cascade immédiatement pour peupler les suggestions de quartier.
    if (villeInput.value.trim()) {
      handleVilleChange();
    } else if (lock && !quartierInput.value.trim()) {
      resetQuartierField(quartierInput, quartierDatalist, placeholderInitial, true);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('[data-cascade="ville-quartier"]').forEach(initCascade);
  });
})();