(() => {
  const GA_ID = "G-5W84N9FL5X";
  const STORAGE_KEY = "be-consent-v1";
  const POLICY_VERSION = "2026-09-13-v1";
  const DECISION_MAX_AGE_MS = 365 * 24 * 60 * 60 * 1000;
  let memoryChoice = null;
  let analyticsScriptRequested = false;
  let analyticsScriptLoaded = false;
  let analyticsConfigured = false;
  let settingsOpener = null;

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function(){ dataLayer.push(arguments); };

  const safeStorageGet = (key) => {
    try {
      return window.localStorage?.getItem(key) ?? null;
    } catch (_) {
      return key === STORAGE_KEY ? memoryChoice : null;
    }
  };

  const safeStorageSet = (key, value) => {
    if (key === STORAGE_KEY) memoryChoice = value;
    try {
      window.localStorage?.setItem(key, value);
      return true;
    } catch (_) {
      return false;
    }
  };

  const consentPayload = (analyticsStorage) => ({
    analytics_storage: analyticsStorage,
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied"
  });

  // Conservative defaults for EEA users. No Google network request is made
  // until analytics consent is explicitly granted.
  gtag("consent", "default", {
    ...consentPayload("denied"),
    wait_for_update: 500
  });

  const isProjectUrl = (url) => {
    const host = url.hostname.toLowerCase();
    return host === "bezpecnaelektrika.sk" || host.endsWith(".bezpecnaelektrika.sk") || url.origin === location.origin;
  };

  const sanitizeAnalyticsUrl = (rawUrl) => {
    if (!rawUrl) return "";
    try {
      const url = new URL(rawUrl, location.href);
      if (isProjectUrl(url) && url.pathname === "/hladat/" && url.searchParams.has("q")) {
        url.searchParams.set("q", "(redacted)");
      }
      return url.href;
    } catch (_) {
      return "";
    }
  };

  const updateAnalyticsConsent = (granted) => {
    gtag("consent", "update", consentPayload(granted ? "granted" : "denied"));
  };

  const clearAnalyticsCookies = () => {
    try {
      const names = document.cookie.split(";").map((part) => part.split("=", 1)[0].trim()).filter((name) => name === "_ga" || name.startsWith("_ga_"));
      const domains = ["", "bezpecnaelektrika.sk", ".bezpecnaelektrika.sk"];
      names.forEach((name) => {
        domains.forEach((domain) => {
          const domainPart = domain ? `; Domain=${domain}` : "";
          document.cookie = `${name}=; Max-Age=0; Path=/${domainPart}; SameSite=Lax`;
        });
      });
    } catch (_) {
      // Cookie cleanup is best-effort; consent state remains denied even if the browser blocks cookie access.
    }
  };

  const configureAnalytics = () => {
    if (analyticsConfigured || getChoice() !== "analytics") return;
    const pageLocation = sanitizeAnalyticsUrl(location.href) || location.href;
    const pageReferrer = sanitizeAnalyticsUrl(document.referrer);
    const config = { page_location: pageLocation };
    if (pageReferrer) config.page_referrer = pageReferrer;
    gtag("js", new Date());
    gtag("config", GA_ID, config);
    analyticsConfigured = true;
  };

  const ensureAnalyticsLoaded = () => {
    if (analyticsScriptLoaded) {
      configureAnalytics();
      return;
    }
    if (analyticsScriptRequested) return;
    analyticsScriptRequested = true;
    const script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(GA_ID);
    script.onload = () => {
      analyticsScriptLoaded = true;
      configureAnalytics();
    };
    script.onerror = () => {
      analyticsScriptRequested = false;
      analyticsScriptLoaded = false;
    };
    document.head.appendChild(script);
  };

  const grantAnalytics = () => {
    // Always send a fresh update. This is intentionally separate from the
    // one-time script load so grant -> deny -> grant works on one page load.
    updateAnalyticsConsent(true);
    ensureAnalyticsLoaded();
  };

  const denyAnalytics = () => {
    updateAnalyticsConsent(false);
    clearAnalyticsCookies();
  };

  function setChoice(choice) {
    const record = { choice, decidedAt: new Date().toISOString(), policyVersion: POLICY_VERSION };
    safeStorageSet(STORAGE_KEY, JSON.stringify(record));
    if (choice === "analytics") grantAnalytics();
    else denyAnalytics();
    // Close first so focus can return to a still-visible opener; only then hide the banner.
    closeSettings();
    hideBanner();
  }

  function getChoice() {
    const value = safeStorageGet(STORAGE_KEY);
    if (value) {
      try {
        const record = JSON.parse(value);
        const decidedAt = Date.parse(record?.decidedAt || "");
        const fresh = Number.isFinite(decidedAt) && (Date.now() - decidedAt) <= DECISION_MAX_AGE_MS;
        if ((record?.choice === "analytics" || record?.choice === "necessary") && record?.policyVersion === POLICY_VERSION && fresh) {
          memoryChoice = record.choice;
          return record.choice;
        }
      } catch (_) {
        // Legacy v1 string values are intentionally re-prompted after the policy update.
      }
    }
    return memoryChoice === "analytics" || memoryChoice === "necessary" ? memoryChoice : null;
  }

  const updateConsentClearance = () => {
    const banner = document.querySelector(".consent-banner");
    if (!banner || banner.hidden) {
      document.documentElement.style.removeProperty("--consent-clearance");
      return;
    }
    const rect = banner.getBoundingClientRect();
    document.documentElement.style.setProperty("--consent-clearance", `${Math.ceil(rect.height + Math.max(0, innerHeight - rect.bottom))}px`);
  };

  function hideBanner() {
    document.querySelector(".consent-banner")?.setAttribute("hidden", "");
    document.body.classList.remove("consent-visible");
    updateConsentClearance();
  }

  function showBanner() {
    document.querySelector(".consent-banner")?.removeAttribute("hidden");
    document.body.classList.add("consent-visible");
    requestAnimationFrame(updateConsentClearance);
  }

  function openSettings(event) {
    const dialog = document.querySelector("#consent-settings");
    const choice = getChoice();
    const checkbox = dialog?.querySelector("#consent-analytics");
    settingsOpener = event?.currentTarget instanceof HTMLElement
      ? event.currentTarget
      : (document.activeElement instanceof HTMLElement ? document.activeElement : null);
    if (checkbox) checkbox.checked = choice === "analytics";
    if (dialog?.showModal) {
      dialog.showModal();
      dialog.querySelector(".consent-close")?.focus();
    } else {
      dialog?.removeAttribute("hidden");
    }
  }

  function restoreSettingsFocus() {
    if (settingsOpener?.isConnected && !settingsOpener.closest("[hidden]")) settingsOpener.focus();
    settingsOpener = null;
  }

  function closeSettings() {
    const dialog = document.querySelector("#consent-settings");
    if (!dialog) return;
    if (dialog.close && dialog.open) dialog.close();
    else {
      dialog.setAttribute("hidden", "");
      restoreSettingsFocus();
    }
  }

  function renderConsentUI() {
    if (document.querySelector(".consent-banner")) return;

    const banner = document.createElement("aside");
    banner.className = "consent-banner";
    banner.setAttribute("aria-label", "Nastavenie analytiky");
    banner.innerHTML = `
      <div class="consent-banner__inner">
        <div class="consent-copy">
          <strong>Analytika návštevnosti</strong>
          <p>Web používa nevyhnutné lokálne uloženie pre nastavenie vzhľadu a voľby súkromia. Google Analytics zapneme iba s vaším súhlasom. Nevyhnutné lokálne uloženie slúži pre vzhľad a zapamätanie voľby súkromia.</p>
          <a href="/ochrana-sukromia/">Ako pracujeme so súkromím →</a>
        </div>
        <div class="consent-actions">
          <button type="button" class="button-v04 primary" data-consent="analytics">Povoliť analytiku</button>
          <button type="button" class="button-v04 secondary" data-consent="necessary">Len nevyhnutné</button>
          <button type="button" class="consent-text-button" data-consent-settings>Nastavenia</button>
        </div>
      </div>`;
    document.body.appendChild(banner);
    if ("ResizeObserver" in window) new ResizeObserver(updateConsentClearance).observe(banner);
    window.addEventListener("resize", updateConsentClearance, { passive: true });

    const dialog = document.createElement("dialog");
    dialog.id = "consent-settings";
    dialog.className = "consent-dialog";
    dialog.setAttribute("aria-labelledby", "consent-settings-title");
    dialog.innerHTML = `
      <form method="dialog" class="consent-dialog__panel">
        <div class="consent-dialog__head">
          <div>
            <span class="eyebrow">Súkromie</span>
            <h2 id="consent-settings-title">Nastavenia analytiky</h2>
          </div>
          <button type="button" class="consent-close" aria-label="Zavrieť nastavenia">×</button>
        </div>
        <div class="consent-option is-required">
          <div>
            <strong>Nevyhnutné</strong>
            <p>Lokálna voľba vzhľadu a zapamätanie vášho rozhodnutia o analytike.</p>
          </div>
          <span>Vždy aktívne</span>
        </div>
        <label class="consent-option">
          <div>
            <strong>Analytika</strong>
            <p>Google Analytics 4 – návštevnosť a používanie webu. Reklamné úložisko zostáva vypnuté.</p>
          </div>
          <input id="consent-analytics" type="checkbox">
        </label>
        <div class="consent-dialog__actions">
          <button type="button" class="button-v04 primary" data-consent-save>Uložiť voľbu</button>
          <a href="/ochrana-sukromia/">Podrobnosti o súkromí</a>
        </div>
      </form>`;
    document.body.appendChild(dialog);

    banner.querySelector('[data-consent="analytics"]').addEventListener("click", () => setChoice("analytics"));
    banner.querySelector('[data-consent="necessary"]').addEventListener("click", () => setChoice("necessary"));
    banner.querySelector("[data-consent-settings]").addEventListener("click", openSettings);
    dialog.querySelector(".consent-close").addEventListener("click", closeSettings);
    dialog.addEventListener("close", restoreSettingsFocus);
    dialog.querySelector("[data-consent-save]").addEventListener("click", () => {
      const checked = dialog.querySelector("#consent-analytics").checked;
      setChoice(checked ? "analytics" : "necessary");
    });

    document.querySelectorAll("[data-open-consent]").forEach((button) => {
      button.addEventListener("click", openSettings);
    });

    const choice = getChoice();
    if (choice === "analytics") {
      hideBanner();
      grantAnalytics();
    } else if (choice === "necessary") {
      hideBanner();
      denyAnalytics();
    } else {
      showBanner();
    }
  }

  // Search may keep the useful local q= URL while GA receives only a redacted
  // page_location. Set the safe value before history.replaceState can trigger
  // a history-based page-view measurement.
  window.beSetSafeAnalyticsLocation = (rawUrl) => {
    if (getChoice() !== "analytics" || !analyticsConfigured) return;
    const safeUrl = sanitizeAnalyticsUrl(rawUrl);
    if (safeUrl) gtag("set", { page_location: safeUrl });
  };

  // Public helper for first-party custom events. It is a no-op unless
  // analytics was granted and the Google tag has completed configuration.
  window.beTrack = (eventName, params = {}) => {
    if (getChoice() !== "analytics" || !analyticsConfigured) return;
    gtag("event", eventName, params);
  };

  document.addEventListener("DOMContentLoaded", () => {
    renderConsentUI();

    // Measure interest in contact only after consent.
    document.addEventListener("click", (event) => {
      const link = event.target.closest('a[href="#kontakt"], a[href="/#kontakt"], a[href^="mailto:kontakt@bezpecnaelektrika.sk"]');
      if (!link) return;
      window.beTrack?.("contact_click", {
        link_text: (link.textContent || "").trim().slice(0, 100),
        page_path: location.pathname
      });
    });

    // Customer-journey events use only fixed categories and page paths; no email/message contents are sent.
    document.addEventListener("click", (event) => {
      const serviceLink = event.target.closest("[data-service-interest]");
      if (serviceLink) {
        window.beTrack?.("service_interest_click", {
          placement: serviceLink.dataset.serviceInterest || "other",
          page_path: location.pathname
        });
      }

      const priceLink = event.target.closest('a[href="/revizie/#cena"], a[href="#cena"]');
      if (priceLink) {
        window.beTrack?.("price_interest_click", { page_path: location.pathname });
      }

      const situationLink = event.target.closest("[data-service-situation]");
      if (situationLink) {
        window.beTrack?.("service_situation_click", {
          situation: situationLink.dataset.serviceSituation || "other",
          page_path: location.pathname
        });
      }

      const expertLink = event.target.closest(".expert-strip a");
      if (expertLink) {
        const expertTargets = {
          "/glosar/": "glossary",
          "/meranie/": "measurement",
          "/novinky/": "news",
          "/metodika/": "methodology"
        };
        const targetArea = expertTargets[expertLink.getAttribute("href")];
        if (targetArea) {
          window.beTrack?.("expert_content_click", {
            target_area: targetArea,
            page_path: location.pathname
          });
        }
      }
    });

    // Measure outbound interest in official project profiles only after consent.
    document.addEventListener("click", (event) => {
      const link = event.target.closest('a[href*="instagram.com/bezpecnaelektrika"], a[href*="facebook.com/61591729689209"]');
      if (!link) return;
      const platform = link.href.includes("instagram.com") ? "instagram" : "facebook";
      window.beTrack?.("social_click", {
        platform,
        page_path: location.pathname
      });
    });
  });
})();
