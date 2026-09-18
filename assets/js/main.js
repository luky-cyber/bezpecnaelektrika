document.documentElement.classList.add("js-ready");

document.addEventListener("DOMContentLoaded", () => {
  const q = (selector, context = document) => context.querySelector(selector);
  const qa = (selector, context = document) => [...context.querySelectorAll(selector)];
  const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
  const safeStorageGet = (key) => { try { return window.localStorage?.getItem(key) ?? null; } catch (_) { return null; } };
  const safeStorageSet = (key, value) => { try { window.localStorage?.setItem(key, value); return true; } catch (_) { return false; } };

  // Mobile / responsive navigation.
  const navToggle = q(".nav-toggle");
  const mainNav = q("#main-nav");
  const closeNav = () => {
    if (!mainNav || !navToggle) return;
    mainNav.classList.remove("open");
    navToggle.setAttribute("aria-expanded", "false");
    navToggle.setAttribute("aria-label", "Otvoriť menu");
  };

  // One contextual navigation model for /revizie/: click/hash and scroll position
  // drive the same active state. This mirrors the authorial navigation grammar
  // used on Likavcan.cz without copying its information architecture.
  const syncRevisionNavCurrent = () => {
    if (!mainNav) return;
    const path = window.location.pathname.replace(/\/index\.html$/, "/");
    if (path !== "/revizie/") return;

    const primaryLinks = qa(".nav-primary > a", mainNav);
    const tracked = [
      { key: "#kedy-a-ako-casto", section: q("#kedy-a-ako-casto") },
      { key: "#cena", section: q("#cena") }
    ].filter((item) => item.section);

    const setCurrent = (hash = "") => {
      const currentHref = hash ? `/revizie/${hash}` : "/revizie/";
      primaryLinks.forEach((link) => {
        const current = link.getAttribute("href") === currentHref;
        link.classList.toggle("active", current);
        if (current) link.setAttribute("aria-current", hash ? "location" : "page");
        else link.removeAttribute("aria-current");
      });
    };

    const trackedKeys = new Set(tracked.map((item) => item.key));
    let frame = 0;
    let navigationIntent = "";
    let navigationIntentUntil = 0;

    const startNavigationIntent = (hash) => {
      if (!trackedKeys.has(hash)) return;
      navigationIntent = hash;
      navigationIntentUntil = performance.now() + 1800;
      // Switch the selected item immediately. During smooth scrolling we keep
      // this intent locked so an intermediate section cannot flash as active.
      setCurrent(hash);
    };

    const updateFromScroll = () => {
      frame = 0;
      const headerBottom = q(".site-header")?.getBoundingClientRect().bottom || 0;
      const trigger = Math.max(headerBottom + 24, Math.min(window.innerHeight * 0.30, 210));

      if (navigationIntent) {
        const target = tracked.find((item) => item.key === navigationIntent);
        const rect = target?.section.getBoundingClientRect();
        const targetReached = !!rect && rect.top <= trigger && rect.bottom > trigger;
        if (!targetReached && performance.now() < navigationIntentUntil) {
          setCurrent(navigationIntent);
          return;
        }
        navigationIntent = "";
        navigationIntentUntil = 0;
      }

      // Treat contextual items as milestones, not isolated rectangles. Once a
      // tracked section reaches the reading line it stays current until the next
      // tracked section reaches it. This avoids falling back to "Revízie" in
      // the content gaps after Kedy revíziu and after Cena. It also behaves
      // consistently in the mobile hamburger, where section heights differ.
      let activeHash = "";
      for (const item of tracked) {
        const rect = item.section.getBoundingClientRect();
        if (rect.top <= trigger) activeHash = item.key;
        else break;
      }
      setCurrent(activeHash);
    };
    const schedule = () => {
      if (frame) return;
      frame = window.requestAnimationFrame(updateFromScroll);
    };

    primaryLinks.forEach((link) => {
      const href = link.getAttribute("href") || "";
      const target = tracked.find((item) => href === `/revizie/${item.key}`);
      if (target) link.addEventListener("click", () => startNavigationIntent(target.key));
    });

    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule, { passive: true });
    window.addEventListener("hashchange", () => {
      if (trackedKeys.has(window.location.hash)) startNavigationIntent(window.location.hash);
      schedule();
    });

    if (trackedKeys.has(window.location.hash)) {
      startNavigationIntent(window.location.hash);
      schedule();
    } else {
      updateFromScroll();
    }
  };

  syncRevisionNavCurrent();

  // Homepage mobile dock: Contact is a real in-page destination, not the
  // homepage default state. Keep Home current above the Contact heading and
  // Contact current from that milestone to the end of the page.
  const syncHomeMobileContactCurrent = () => {
    const path = window.location.pathname.replace(/\/index\.html$/, "/");
    if (path !== "/") return;

    const mobileNav = q(".mobile-bottom-nav");
    const contactSection = q("#kontakt");
    if (!mobileNav || !contactSection) return;

    const homeLink = q('a[href="/"]', mobileNav);
    const contactLink = q('a[href="/#kontakt"]', mobileNav);
    if (!homeLink || !contactLink) return;

    let frame = 0;
    let contactIntentUntil = 0;

    const setCurrent = (contactCurrent) => {
      homeLink.classList.toggle("active", !contactCurrent);
      contactLink.classList.toggle("active", contactCurrent);
      if (contactCurrent) {
        contactLink.setAttribute("aria-current", "location");
        homeLink.removeAttribute("aria-current");
      } else {
        homeLink.setAttribute("aria-current", "page");
        contactLink.removeAttribute("aria-current");
      }
    };

    const startContactIntent = () => {
      contactIntentUntil = performance.now() + 1800;
      setCurrent(true);
    };

    const updateFromScroll = () => {
      frame = 0;
      const headerBottom = q(".site-header")?.getBoundingClientRect().bottom || 0;
      const trigger = Math.max(headerBottom + 24, Math.min(window.innerHeight * 0.30, 210));
      const rect = contactSection.getBoundingClientRect();

      if (contactIntentUntil) {
        const reached = rect.top <= trigger;
        if (!reached && performance.now() < contactIntentUntil) {
          setCurrent(true);
          return;
        }
        contactIntentUntil = 0;
      }

      setCurrent(rect.top <= trigger);
    };

    const schedule = () => {
      if (frame) return;
      frame = window.requestAnimationFrame(updateFromScroll);
    };

    contactLink.addEventListener("click", startContactIntent);
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule, { passive: true });
    window.addEventListener("hashchange", () => {
      if (window.location.hash === "#kontakt") startContactIntent();
      schedule();
    });

    if (window.location.hash === "#kontakt") startContactIntent();
    schedule();
  };

  syncHomeMobileContactCurrent();

  if (navToggle && mainNav) {
    navToggle.addEventListener("click", (event) => {
      event.preventDefault();
      const open = !mainNav.classList.contains("open");
      mainNav.classList.toggle("open", open);
      navToggle.setAttribute("aria-expanded", String(open));
      navToggle.setAttribute("aria-label", open ? "Zavrieť menu" : "Otvoriť menu");
      if (open) mainNav.querySelector("a")?.focus();
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
  const storedTheme = safeStorageGet("be-theme");
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
    safeStorageSet("be-theme", next);
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

  // On touch/coarse pointers, the first tap outside an open explanation only dismisses it.
  // This prevents an accidental navigation when a link happens to sit under the dismissing tap.
  document.addEventListener("click", (event) => {
    const openItem = popovers.find((item) => item.classList.contains("is-open"));
    if (!openItem) return;
    if (openItem.contains(event.target)) return;
    if (event.target.closest?.(".term-popover__trigger")) return;
    const coarsePointer = window.matchMedia?.("(pointer: coarse)").matches || window.matchMedia?.("(hover: none)").matches;
    if (!coarsePointer) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    close(openItem);
  }, true);

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
