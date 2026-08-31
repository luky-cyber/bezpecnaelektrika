(() => {
  const GA_ID = "G-5W84N9FL5X";
  const STORAGE_KEY = "be-consent-v1";

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function(){ dataLayer.push(arguments); };

  // Conservative defaults for EEA users. No Google network request is made
  // until analytics consent is explicitly granted.
  gtag("consent", "default", {
    analytics_storage: "denied",
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    wait_for_update: 500
  });

  let analyticsLoaded = false;

  function loadAnalytics() {
    if (analyticsLoaded) return;
    analyticsLoaded = true;

    gtag("consent", "update", {
      analytics_storage: "granted",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied"
    });

    const script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(GA_ID);
    script.onload = () => {
      gtag("js", new Date());
      gtag("config", GA_ID);
    };
    document.head.appendChild(script);
  }

  function setChoice(choice) {
    localStorage.setItem(STORAGE_KEY, choice);
    if (choice === "analytics") {
      loadAnalytics();
    } else {
      gtag("consent", "update", {
        analytics_storage: "denied",
        ad_storage: "denied",
        ad_user_data: "denied",
        ad_personalization: "denied"
      });
    }
    hideBanner();
    closeSettings();
  }

  function getChoice() {
    const value = localStorage.getItem(STORAGE_KEY);
    return value === "analytics" || value === "necessary" ? value : null;
  }

  function hideBanner() {
    document.querySelector(".consent-banner")?.setAttribute("hidden", "");
  }

  function showBanner() {
    document.querySelector(".consent-banner")?.removeAttribute("hidden");
  }

  function openSettings() {
    const dialog = document.querySelector("#consent-settings");
    const choice = getChoice();
    const checkbox = dialog?.querySelector("#consent-analytics");
    if (checkbox) checkbox.checked = choice === "analytics";
    if (dialog?.showModal) dialog.showModal();
    else dialog?.removeAttribute("hidden");
  }

  function closeSettings() {
    const dialog = document.querySelector("#consent-settings");
    if (!dialog) return;
    if (dialog.close && dialog.open) dialog.close();
    else dialog.setAttribute("hidden", "");
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
          <p>Web používa nevyhnutné lokálne uloženie pre nastavenie vzhľadu a voľby súkromia. Google Analytics zapneme iba s vaším súhlasom, aby sme vedeli, ktoré časti webu sú užitočné.</p>
          <a href="/ochrana-sukromia/">Ako pracujeme so súkromím →</a>
        </div>
        <div class="consent-actions">
          <button type="button" class="button-v04 primary" data-consent="analytics">Povoliť analytiku</button>
          <button type="button" class="button-v04 secondary" data-consent="necessary">Len nevyhnutné</button>
          <button type="button" class="consent-text-button" data-consent-settings>Nastavenia</button>
        </div>
      </div>`;
    document.body.appendChild(banner);

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
      loadAnalytics();
    } else if (choice === "necessary") {
      hideBanner();
    } else {
      showBanner();
    }
  }

  // Public helper for first-party custom events. It is a no-op unless
  // analytics was granted and the Google tag has been loaded.
  window.beTrack = (eventName, params = {}) => {
    if (getChoice() !== "analytics" || !analyticsLoaded) return;
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
