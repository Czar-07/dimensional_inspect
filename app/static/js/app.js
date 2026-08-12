(() => {
  "use strict";

  const root = document.documentElement;
  const sidebar = document.getElementById("sidebar");
  const collapse = document.getElementById("sidebarCollapse");
  const mobile = document.getElementById("mobileMenu");
  const theme = document.getElementById("themeToggle");
  const about = document.getElementById("aboutButton");
  const aboutSystem = document.getElementById("aboutSystemButton");
  const modal = document.getElementById("aboutModal");
  const close = document.getElementById("aboutClose");

  const setTheme = (value) => {
    const themeValue = value === "light" ? "light" : "dark";
    root.dataset.theme = themeValue;
    localStorage.setItem("dimensionRateTheme", themeValue);
    if (theme) {
      theme.innerHTML = themeValue === "dark"
        ? '<i class="fa-regular fa-sun"></i>'
        : '<i class="fa-regular fa-moon"></i>';
    }
  };

  // A identidade visual da ITAESBRA usa o modo escuro como padrão.
  setTheme(localStorage.getItem("dimensionRateTheme") || "dark");

  theme?.addEventListener("click", () => {
    setTheme(root.dataset.theme === "dark" ? "light" : "dark");
  });

  collapse?.addEventListener("click", () => {
    sidebar?.classList.toggle("collapsed");
    localStorage.setItem(
      "dimensionRateSidebar",
      sidebar?.classList.contains("collapsed") ? "collapsed" : "expanded"
    );
  });

  if (localStorage.getItem("dimensionRateSidebar") === "collapsed" && window.innerWidth > 980) {
    sidebar?.classList.add("collapsed");
  }

  mobile?.addEventListener("click", () => sidebar?.classList.toggle("open"));

  document.addEventListener("click", (event) => {
    if (
      window.innerWidth <= 980 &&
      sidebar?.classList.contains("open") &&
      !sidebar.contains(event.target) &&
      !mobile?.contains(event.target)
    ) {
      sidebar.classList.remove("open");
    }
  });

  const openModal = () => {
    if (modal) modal.hidden = false;
  };

  const closeModal = () => {
    if (modal) modal.hidden = true;
  };

  about?.addEventListener("click", openModal);
  aboutSystem?.addEventListener("click", openModal);
  close?.addEventListener("click", closeModal);
  modal?.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeModal();
  });
})();
