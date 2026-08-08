/* ==========================================================================
   iMMoLink — script.js
   Comportements transverses au site public + espaces locataire/propriétaire :
   toggle des favoris (AJAX) et fermeture auto des messages/toasts.
   ========================================================================== */

(function () {
  "use strict";

  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^|; )" + name + "=([^;]*)"));
    return match ? decodeURIComponent(match[2]) : null;
  }

  const csrftoken = getCookie("csrftoken");

  function updateFavoritesBadge(total) {
    const badge = document.querySelector(".favorites-badge");
    if (badge) {
      badge.textContent = total;
      badge.style.display = total > 0 ? "flex" : "none";
    }
  }

  function toggleFavorite(button) {
    const annonceId = button.dataset.annonceId;
    if (!annonceId || button.dataset.loading === "1") return;

    button.dataset.loading = "1";

    fetch(`/favoris/toggle/${annonceId}/`, {
      method: "POST",
      headers: { "X-CSRFToken": csrftoken, "X-Requested-With": "XMLHttpRequest" },
      credentials: "same-origin",
    })
      .then((response) => {
        if (response.redirected) {
          // Utilisateur non connecté : la vue redirige vers la connexion.
          window.location.href = response.url;
          return null;
        }
        return response.json();
      })
      .then((data) => {
        if (!data) return;
        const icon = button.querySelector("i");
        if (icon) {
          icon.classList.toggle("fa-regular", !data.favori);
          icon.classList.toggle("fa-solid", data.favori);
        }
        button.classList.toggle("is-favorite", data.favori);
        updateFavoritesBadge(data.total);
      })
      .catch(() => {})
      .finally(() => {
        button.dataset.loading = "0";
      });
  }

  document.addEventListener("click", function (event) {
    const button = event.target.closest(".listing-card-fav");
    if (!button) return;
    event.preventDefault();
    event.stopPropagation();
    toggleFavorite(button);
  });

  // ------------------------------------------------------------------
  // Menu mobile (drawer plein écran) — ouverture/fermeture.
  // ------------------------------------------------------------------
  document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menuToggle");
    const menuClose = document.getElementById("menuClose");
    const mobileMenu = document.getElementById("mobileMenu");
    const overlay = document.getElementById("mobileMenuOverlay");
    if (!menuToggle || !mobileMenu || !overlay) return;

    function openMenu() {
      mobileMenu.classList.add("is-open");
      overlay.classList.add("is-open");
      document.body.classList.add("menu-open");
      mobileMenu.setAttribute("aria-hidden", "false");
      menuToggle.setAttribute("aria-expanded", "true");
    }

    function closeMenu() {
      mobileMenu.classList.remove("is-open");
      overlay.classList.remove("is-open");
      document.body.classList.remove("menu-open");
      mobileMenu.setAttribute("aria-hidden", "true");
      menuToggle.setAttribute("aria-expanded", "false");
    }

    menuToggle.addEventListener("click", openMenu);
    if (menuClose) menuClose.addEventListener("click", closeMenu);
    overlay.addEventListener("click", closeMenu);
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeMenu();
    });
    // Referme le menu si on clique un lien à l'intérieur (navigation).
    mobileMenu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", closeMenu);
    });
  });

  // Ferme automatiquement les toasts de confirmation après quelques secondes.
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".messages li").forEach(function (item, index) {
      setTimeout(function () {
        item.style.transition = "opacity 0.4s ease";
        item.style.opacity = "0";
        setTimeout(() => item.remove(), 400);
      }, 4000 + index * 300);
    });
  });
})();