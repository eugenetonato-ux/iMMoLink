document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("geo-search-form");
  if (!form) return;

  const departmentSelect = document.getElementById("department-select");
  const communeSelect = document.getElementById("commune-select");
  const arrondissementSelect = document.getElementById("arrondissement-select");
  const localitySelect = document.getElementById("locality-select");
  const communeHidden = document.getElementById("commune-hidden");
  const quartierHidden = document.getElementById("quartier-hidden");

  const communesUrl = form.dataset.communesUrl;
  const arrondissementsUrl = form.dataset.arrondissementsUrl;
  const localitiesUrl = form.dataset.localitiesUrl;

  function resetSelect(select, placeholder) {
    select.innerHTML = "";
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = placeholder;
    select.appendChild(opt);
    select.disabled = true;
  }

  function fillSelect(select, items, placeholder) {
    select.innerHTML = "";
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = placeholder;
    select.appendChild(opt);
    items.forEach(function (item) {
      const o = document.createElement("option");
      o.value = item.id;
      o.textContent = item.nom;
      select.appendChild(o);
    });
    select.disabled = false;
  }

  function fetchResults(url, paramName, paramValue) {
    return fetch(url + "?" + paramName + "=" + encodeURIComponent(paramValue)).then(function (res) {
      if (!res.ok) throw new Error("Erreur réseau");
      return res.json();
    });
  }

  departmentSelect.addEventListener("change", function () {
    resetSelect(communeSelect, "Choisir d'abord un département");
    resetSelect(arrondissementSelect, "Choisir d'abord une commune");
    resetSelect(localitySelect, "Choisir d'abord un arrondissement");
    communeHidden.value = "";
    quartierHidden.value = "";

    if (!departmentSelect.value) return;

    fetchResults(communesUrl, "department_id", departmentSelect.value)
      .then(function (data) {
        fillSelect(communeSelect, data.results, "Choisir une commune");
      })
      .catch(function () {
        resetSelect(communeSelect, "Erreur de chargement");
      });
  });

  communeSelect.addEventListener("change", function () {
    resetSelect(arrondissementSelect, "Choisir d'abord une commune");
    resetSelect(localitySelect, "Choisir d'abord un arrondissement");
    quartierHidden.value = "";

    communeHidden.value = communeSelect.value || "";

    if (!communeSelect.value) return;

    fetchResults(arrondissementsUrl, "commune_id", communeSelect.value)
      .then(function (data) {
        fillSelect(arrondissementSelect, data.results, "Choisir un arrondissement");
      })
      .catch(function () {
        resetSelect(arrondissementSelect, "Erreur de chargement");
      });
  });

  arrondissementSelect.addEventListener("change", function () {
    resetSelect(localitySelect, "Choisir d'abord un arrondissement");
    quartierHidden.value = "";

    if (!arrondissementSelect.value) return;

    fetchResults(localitiesUrl, "arrondissement_id", arrondissementSelect.value)
      .then(function (data) {
        fillSelect(localitySelect, data.results, "Choisir un quartier");
      })
      .catch(function () {
        resetSelect(localitySelect, "Erreur de chargement");
      });
  });

  localitySelect.addEventListener("change", function () {
    quartierHidden.value = localitySelect.value || "";
  });

  // ------------------------------------------------------------
  // Pré-remplissage (édition d'une annonce existante, retour sur
  // une recherche déjà filtrée…) : optionnel, via data-selected-*
  // sur le conteneur #geo-search-form.
  // ------------------------------------------------------------
  async function preselectionner() {
    const depId = form.dataset.selectedDepartment;
    const communeId = form.dataset.selectedCommune;
    const arrId = form.dataset.selectedArrondissement;
    const locId = form.dataset.selectedLocality;

    if (!depId) return;

    try {
      departmentSelect.value = depId;

      const communesData = await fetchResults(communesUrl, "department_id", depId);
      fillSelect(communeSelect, communesData.results, "Choisir une commune");
      if (!communeId) return;
      communeSelect.value = communeId;
      communeHidden.value = communeId;

      const arrData = await fetchResults(arrondissementsUrl, "commune_id", communeId);
      fillSelect(arrondissementSelect, arrData.results, "Choisir un arrondissement");
      if (!arrId) return;
      arrondissementSelect.value = arrId;

      const locData = await fetchResults(localitiesUrl, "arrondissement_id", arrId);
      fillSelect(localitySelect, locData.results, "Choisir un quartier");
      if (!locId) return;
      localitySelect.value = locId;
      quartierHidden.value = locId;
    } catch (e) {
      // Silencieux : l'utilisateur peut resélectionner manuellement.
    }
  }

  preselectionner();
});