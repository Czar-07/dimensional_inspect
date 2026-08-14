(() => {
  "use strict";

  const root = document.documentElement;
  const body = document.body;
  const sidebar = document.getElementById("sidebar");
  const collapse = document.getElementById("sidebarCollapse");
  const mobile = document.getElementById("mobileMenu");
  const overlay = document.getElementById("sidebarOverlay");
  const quickTheme = document.getElementById("quickTheme");
  const about = document.getElementById("aboutButton");
  const aboutSystem = document.getElementById("aboutSystemButton");
  const aboutModal = document.getElementById("aboutModal");
  const aboutClose = document.getElementById("aboutClose");
  const settingsButton = document.getElementById("settingsButton");
  const settingsModal = document.getElementById("settingsModal");
  const settingsClose = document.getElementById("settingsClose");
  const resetSettings = document.getElementById("resetSettings");

  const STORAGE = {
    theme: "dimensionRateTheme",
    style: "dimensionRateStyle",
    sidebar: "dimensionRateSidebar",
    motion: "dimensionRateMotion",
    mobileClose: "dimensionRateMobileClose"
  };

  const validStyles = ["minimal", "artdeco", "industrial", "scandinavian", "boho", "rustic", "contemporary", "wabisabi"];

  function setTheme(value, persist = true) {
    const theme = value === "dark" ? "dark" : "light";
    root.dataset.theme = theme;
    if (persist) localStorage.setItem(STORAGE.theme, theme);
    if (quickTheme) {
      quickTheme.innerHTML = theme === "dark"
        ? '<i class="fa-regular fa-sun"></i>'
        : '<i class="fa-regular fa-moon"></i>';
    }
    document.querySelectorAll("[data-theme-value]").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.themeValue === theme);
    });
  }

  function setStyle(value, persist = true) {
    const style = validStyles.includes(value) ? value : "minimal";
    root.dataset.style = style;
    if (persist) localStorage.setItem(STORAGE.style, style);
    document.querySelectorAll("[data-style-value]").forEach(card => {
      card.classList.toggle("selected", card.dataset.styleValue === style);
    });
  }

  function setMotion(enabled, persist = true) {
    root.classList.toggle("no-motion", !enabled);
    if (persist) localStorage.setItem(STORAGE.motion, enabled ? "on" : "off");
    const input = document.getElementById("uiMotion");
    if (input) input.checked = enabled;
  }

  function setSidebarCompact(compact, persist = true) {
    if (!sidebar) return;
    const isDesktop = window.innerWidth > 1050;
    if (isDesktop) sidebar.classList.toggle("collapsed", compact);
    if (persist) localStorage.setItem(STORAGE.sidebar, compact ? "collapsed" : "expanded");
    if (collapse) {
      collapse.setAttribute("aria-expanded", String(!compact));
      collapse.setAttribute("aria-label", compact ? "Expandir menu" : "Recolher menu");
      collapse.innerHTML = compact
        ? '<i class="fa-solid fa-angles-right"></i>'
        : '<i class="fa-solid fa-angles-left"></i>';
    }
    const input = document.getElementById("compactSidebar");
    if (input) input.checked = compact;
  }

  function openSidebar() {
    sidebar?.classList.add("open");
    overlay?.classList.add("is-visible");
    mobile?.setAttribute("aria-expanded", "true");
  }

  function closeSidebar() {
    sidebar?.classList.remove("open");
    overlay?.classList.remove("is-visible");
    mobile?.setAttribute("aria-expanded", "false");
  }

  function openDialog(element, focusTarget) {
    if (!element) return;
    element.hidden = false;
    element.classList.add("is-open");
    body.classList.add("modal-open");
    focusTarget?.focus();
  }

  function closeDialog(element) {
    if (!element) return;
    element.hidden = true;
    element.classList.remove("is-open");

    const aboutOpen = aboutModal && !aboutModal.hidden;
    const settingsOpen = settingsModal && !settingsModal.hidden;
    if (!aboutOpen && !settingsOpen) body.classList.remove("modal-open");
  }

  // Restore preferences. Minimalismo + claro is the official default.
  setTheme(localStorage.getItem(STORAGE.theme) || "light", false);
  setStyle(localStorage.getItem(STORAGE.style) || "minimal", false);
  setMotion(localStorage.getItem(STORAGE.motion) !== "off", false);
  setSidebarCompact(localStorage.getItem(STORAGE.sidebar) === "collapsed", false);

  quickTheme?.addEventListener("click", () => {
    setTheme(root.dataset.theme === "dark" ? "light" : "dark");
  });

  collapse?.addEventListener("click", () => {
    const compact = !sidebar.classList.contains("collapsed");
    setSidebarCompact(compact);
  });

  mobile?.addEventListener("click", () => {
    if (sidebar?.classList.contains("open")) closeSidebar();
    else openSidebar();
  });
  overlay?.addEventListener("click", closeSidebar);

  sidebar?.querySelectorAll("a.nav-item").forEach(link => {
    link.addEventListener("click", () => {
      if (window.innerWidth <= 1050 && localStorage.getItem(STORAGE.mobileClose) !== "off") closeSidebar();
    });
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 1050) {
      closeSidebar();
      setSidebarCompact(localStorage.getItem(STORAGE.sidebar) === "collapsed", false);
    }
  });

  // About dialog
  about?.addEventListener("click", () => openDialog(aboutModal, aboutClose));
  aboutSystem?.addEventListener("click", () => openDialog(aboutModal, aboutClose));
  aboutClose?.addEventListener("click", () => closeDialog(aboutModal));
  aboutModal?.addEventListener("click", event => {
    if (event.target === aboutModal) closeDialog(aboutModal);
  });

  // Settings dialog
  settingsButton?.addEventListener("click", () => {
    openDialog(settingsModal, settingsClose);
    settingsButton.classList.add("settings-button-active");
  });
  settingsClose?.addEventListener("click", () => {
    closeDialog(settingsModal);
    settingsButton?.classList.remove("settings-button-active");
  });
  settingsModal?.addEventListener("click", event => {
    if (event.target === settingsModal) {
      closeDialog(settingsModal);
      settingsButton?.classList.remove("settings-button-active");
    }
  });

  // Settings tabs
  document.querySelectorAll(".settings-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;
      document.querySelectorAll(".settings-tab").forEach(item => {
        const active = item === tab;
        item.classList.toggle("active", active);
        item.setAttribute("aria-selected", String(active));
      });
      document.querySelectorAll(".settings-panel").forEach(panel => {
        panel.classList.toggle("active", panel.dataset.panel === target);
      });
    });
  });

  document.querySelectorAll("[data-theme-value]").forEach(button => {
    button.addEventListener("click", () => setTheme(button.dataset.themeValue));
  });

  document.querySelectorAll("[data-style-value]").forEach(card => {
    card.addEventListener("click", () => setStyle(card.dataset.styleValue));
  });

  document.getElementById("compactSidebar")?.addEventListener("change", event => {
    setSidebarCompact(event.target.checked);
  });
  document.getElementById("uiMotion")?.addEventListener("change", event => {
    setMotion(event.target.checked);
  });
  document.getElementById("closeMobileNav")?.addEventListener("change", event => {
    localStorage.setItem(STORAGE.mobileClose, event.target.checked ? "on" : "off");
  });

  resetSettings?.addEventListener("click", () => {
    Object.values(STORAGE).forEach(key => localStorage.removeItem(key));
    setTheme("light");
    setStyle("minimal");
    setMotion(true);
    setSidebarCompact(false);
    const mobileClose = document.getElementById("closeMobileNav");
    if (mobileClose) mobileClose.checked = true;
  });

  document.addEventListener("keydown", event => {
    if (event.key !== "Escape") return;
    if (settingsModal && !settingsModal.hidden) {
      closeDialog(settingsModal);
      settingsButton?.classList.remove("settings-button-active");
      return;
    }
    if (aboutModal && !aboutModal.hidden) {
      closeDialog(aboutModal);
      return;
    }
    closeSidebar();
  });
})();
