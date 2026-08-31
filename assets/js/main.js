document.documentElement.classList.add("js-ready");

document.addEventListener("DOMContentLoaded", () => {
  const q = (selector, context = document) => context.querySelector(selector);
  const qa = (selector, context = document) => [...context.querySelectorAll(selector)];
  const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;

  // Mobile / responsive navigation.
  const navToggle = q(".nav-toggle");
  const mainNav = q("#main-nav");
  const closeNav = () => {
    if (!mainNav || !navToggle) return;
    mainNav.classList.remove("open");
    navToggle.setAttribute("aria-expanded", "false");
    navToggle.setAttribute("aria-label", "Otvoriť menu");
  };

  if (navToggle && mainNav) {
    navToggle.addEventListener("click", (event) => {
      event.preventDefault();
      const open = !mainNav.classList.contains("open");
      mainNav.classList.toggle("open", open);
      navToggle.setAttribute("aria-expanded", String(open));
      navToggle.setAttribute("aria-label", open ? "Zavrieť menu" : "Otvoriť menu");
    });

    qa("a", mainNav).forEach((link) => link.addEventListener("click", closeNav));

    document.addEventListener("click", (event) => {
      if (mainNav.classList.contains("open") && !mainNav.contains(event.target) && !navToggle.contains(event.target)) {
        closeNav();
      }
    });
  }

  // Supplemental desktop navigation.
  const more = q(".nav-more");
  const moreToggle = q(".more-toggle");
  const closeMore = () => {
    if (!more || !moreToggle) return;
    more.classList.remove("open");
    moreToggle.setAttribute("aria-expanded", "false");
  };

  if (more && moreToggle) {
    moreToggle.addEventListener("click", (event) => {
      event.stopPropagation();
      const open = more.classList.toggle("open");
      moreToggle.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("click", (event) => {
      if (more.classList.contains("open") && !more.contains(event.target)) closeMore();
    });
  }

  // Theme preference. Stored locally only for UI consistency.
  const html = document.documentElement;
  const themeToggle = q(".theme-toggle");
  const storedTheme = localStorage.getItem("be-theme");
  const systemPrefersLight = window.matchMedia?.("(prefers-color-scheme: light)").matches ?? false;

  const applyTheme = (mode) => {
    const resolved = mode === "light" ? "light" : "dark";
    html.dataset.theme = resolved;
    if (!themeToggle) return;
    themeToggle.setAttribute("aria-label", resolved === "dark" ? "Prepnúť na svetlý režim" : "Prepnúť na tmavý režim");
    themeToggle.title = resolved === "dark" ? "Svetlý režim" : "Tmavý režim";
    const icon = q(".theme-icon", themeToggle);
    if (icon) icon.textContent = resolved === "dark" ? "☀" : "☾";
  };

  applyTheme(storedTheme === "light" || storedTheme === "dark" ? storedTheme : (systemPrefersLight ? "light" : "dark"));
  themeToggle?.addEventListener("click", () => {
    const next = html.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem("be-theme", next);
    applyTheme(next);
  });

  // FAQ buttons retained for older FAQ markup; native <details> needs no JS.
  qa(".faq-question").forEach((button) => {
    button.addEventListener("click", () => {
      const item = button.closest(".faq-item");
      if (!item) return;
      const open = item.classList.toggle("open");
      button.setAttribute("aria-expanded", String(open));
    });
  });

  // Reveal animations.
  const revealItems = qa(".reveal");
  if (!reducedMotion && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add("visible"));
  }

  // Back to top.
  const backToTop = q("[data-top]");
  if (backToTop) {
    const updateTopButton = () => backToTop.classList.toggle("show", window.scrollY > 700);
    window.addEventListener("scroll", updateTopButton, { passive: true });
    updateTopButton();
    backToTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: reducedMotion ? "auto" : "smooth" }));
  }

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const navWasOpen = mainNav?.classList.contains("open") ?? false;
    const moreWasOpen = more?.classList.contains("open") ?? false;
    closeNav();
    closeMore();
    if (moreWasOpen) moreToggle?.focus();
    else if (navWasOpen) navToggle?.focus();
  });
});

// v0.5.11 — stable permalinks and copy-link feedback.
document.addEventListener("DOMContentLoaded", () => {
  let toast = document.querySelector(".copy-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.className = "copy-toast";
    toast.setAttribute("role", "status");
    toast.setAttribute("aria-live", "polite");
    document.body.append(toast);
  }
  let toastTimer = null;
  const notify = (message) => {
    toast.textContent = message;
    toast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 1800);
  };
  const copyText = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (_) {
      const area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.append(area);
      area.select();
      document.execCommand("copy");
      area.remove();
    }
  };
  document.addEventListener("click", async (event) => {
    const sectionButton = event.target.closest("[data-copy-anchor]");
    const pageButton = event.target.closest("[data-copy-page]");
    if (!sectionButton && !pageButton) return;
    const url = new URL(location.href);
    url.search = "";
    if (sectionButton) url.hash = sectionButton.dataset.copyAnchor || "";
    else url.hash = "";
    await copyText(url.href);
    notify(sectionButton ? "Odkaz na sekciu skopírovaný" : "Odkaz skopírovaný");
  });
});


// v0.6.0 prototype A3 — inline term explanations without forcing navigation away.
document.addEventListener("DOMContentLoaded", () => {
  const popovers = [...document.querySelectorAll("[data-term-popover]")];
  if (!popovers.length) return;

  const close = (item) => {
    const trigger = item.querySelector(".term-popover__trigger");
    const bubble = item.querySelector(".term-popover__bubble");
    if (!trigger || !bubble) return;
    item.classList.remove("is-open");
    trigger.setAttribute("aria-expanded", "false");
    bubble.setAttribute("aria-hidden", "true");
    bubble.querySelectorAll("a,button").forEach((el) => el.setAttribute("tabindex", "-1"));
  };
  const open = (item) => {
    popovers.forEach((other) => { if (other !== item) close(other); });
    item.classList.remove("is-dismissed");
    const trigger = item.querySelector(".term-popover__trigger");
    const bubble = item.querySelector(".term-popover__bubble");
    if (!trigger || !bubble) return;
    item.classList.add("is-open");
    trigger.setAttribute("aria-expanded", "true");
    bubble.setAttribute("aria-hidden", "false");
    bubble.querySelectorAll("a,button").forEach((el) => el.removeAttribute("tabindex"));
  };

  popovers.forEach((item) => {
    close(item);
    const trigger = item.querySelector(".term-popover__trigger");
    trigger?.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      item.classList.contains("is-open") ? close(item) : open(item);
    });
    item.querySelector(".term-popover__close")?.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      item.classList.add("is-dismissed");
      close(item);
      trigger?.focus();
    });
    item.addEventListener("mouseleave", () => item.classList.remove("is-dismissed"));
  });

  document.addEventListener("click", (event) => {
    popovers.forEach((item) => { if (!item.contains(event.target)) close(item); });
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    popovers.forEach((item) => {
      const wasOpen = item.classList.contains("is-open");
      const trigger = item.querySelector(".term-popover__trigger");
      const focusWasInside = item.contains(document.activeElement);
      close(item);
      if (wasOpen && focusWasInside) trigger?.focus();
    });
  });
});
