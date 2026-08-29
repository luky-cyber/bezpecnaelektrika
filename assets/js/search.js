(() => {
  "use strict";

  const INDEX_URL = "/data/search-index.json";
  const MAX_RESULTS = 8;
  let indexPromise = null;
  let lastTrigger = null;
  let overlay = null;
  let overlayInput = null;
  let overlayResults = null;
  let overlayLive = null;
  let activeResultIndex = -1;
  let currentResultLinks = [];
  const trackedNoResults = new Set();
  let overlayTracking = { used: false };

  const normalize = (value = "") => String(value)
    .replace(/i\s*[Δδ]\s*n/gi, " idn ")
    .replace(/[Δδ]/g, " delta ")
    .replace(/z\s*[_-]?\s*s/gi, " zs ")
    .toLocaleLowerCase("sk")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[ľĺ]/g, "l")
    .replace(/ŕ/g, "r")
    .replace(/[–—_\-/]+/g, " ")
    .replace(/[^a-z0-9\s.]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  const loadIndex = () => {
    if (!indexPromise) {
      indexPromise = fetch(INDEX_URL, { credentials: "same-origin", cache: "force-cache" })
        .then((response) => {
          if (!response.ok) throw new Error(`Search index HTTP ${response.status}`);
          return response.json();
        })
        .then((payload) => payload.records || []);
    }
    return indexPromise;
  };

  const typeLabel = (type) => ({
    hub: "Prehľad",
    kb: "Knowledge Base",
    poradna: "Poradňa",
    novinka: "Novinka",
    podcast: "Podcast",
    metodika: "Metodika",
    meranie: "Meranie"
  }[type] || "Obsah");

  const questionIntent = (query) => /^(preco|co|co ak|potrebujem|ako|kedy|mozem|da sa)\b/.test(query) || query.includes("?");
  const abbreviationIntent = (query) => ["rcd", "rccb", "rcbo", "zs", "lps", "pen", "pe"].includes(query.replace(/\s+/g, ""));

  const scoreRecord = (record, query) => {
    const q = normalize(query);
    if (!q) return null;
    const title = normalize(record.title);
    const summary = normalize(record.summary);
    const body = normalize(record.text);
    const aliases = (record.aliases || []).map(normalize);
    const related = (record.relatedTerms || []).map(normalize);
    const headings = (record.headings || []).map((h) => ({ ...h, norm: normalize(h.text) }));
    let score = 0;
    let bestHeading = null;
    const queryTokens = q.split(" ").filter((token) => token.length > 1);

    if (title === q) score = Math.max(score, 120);
    if (aliases.includes(q)) score = Math.max(score, 100);
    if (title.startsWith(q) && title !== q) score = Math.max(score, 80);
    if (aliases.some((a) => a.startsWith(q) && a !== q)) score = Math.max(score, 70);

    for (const heading of headings) {
      if (!heading.norm) continue;
      if (heading.norm === q) {
        score = Math.max(score, 58);
        bestHeading = heading;
      } else if (heading.norm.includes(q) || q.includes(heading.norm)) {
        if (score < 50) bestHeading = heading;
        score = Math.max(score, 50);
      } else if (queryTokens.length > 1 && queryTokens.every((token) => heading.norm.includes(token))) {
        if (score < 50) bestHeading = heading;
        score = Math.max(score, 50);
      }
    }

    if (summary.includes(q)) score = Math.max(score, 30);
    if (related.some((term) => term === q || term.includes(q) || q.includes(term))) score = Math.max(score, 20);
    if (body.includes(q)) score = Math.max(score, 10);

    const searchable = [title, summary, body, ...aliases, ...related, ...headings.map((h) => h.norm)].join(" ");
    const tokenHits = queryTokens.filter((token) => searchable.includes(token)).length;
    if (tokenHits) score += Math.min(tokenHits * 6, 24);

    if (questionIntent(q) && record.type === "poradna") score += 15;
    if (abbreviationIntent(q) && record.type === "kb") score += 15;
    if (!score) return null;

    const targetUrl = bestHeading && !record.url.includes("#") ? `${record.url}#${bestHeading.id}` : record.url;
    return { record, score, targetUrl, bestHeading };
  };

  // Build the same comparison form as `normalize()`, but keep a map back to
  // the original string. This lets snippets/highlights stay diacritic-insensitive
  // without rewriting the visible Slovak text.
  const normalizeWithMap = (value = "") => {
    const raw = String(value);
    let normalized = "";
    const map = [];

    const append = (piece, start, end) => {
      for (const char of piece) {
        const isSpace = /\s/.test(char);
        if (isSpace && (!normalized || normalized.endsWith(" "))) continue;
        normalized += isSpace ? " " : char;
        map.push({ start, end });
      }
    };

    for (let i = 0; i < raw.length;) {
      const rest = raw.slice(i);
      const idn = rest.match(/^i\s*[Δδ]\s*n/i);
      if (idn) { append("idn", i, i + idn[0].length); i += idn[0].length; continue; }
      const zs = rest.match(/^z\s*[_-]?\s*s/i);
      if (zs) { append("zs", i, i + zs[0].length); i += zs[0].length; continue; }

      const char = raw[i];
      if (/[Δδ]/.test(char)) { append("delta", i, i + 1); i += 1; continue; }
      let piece = char.toLocaleLowerCase("sk").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      piece = piece.replace(/[ľĺ]/g, "l").replace(/ŕ/g, "r");
      if (/[–—_\-/]/.test(char) || /\s/.test(char)) piece = " ";
      else piece = piece.replace(/[^a-z0-9.]+/g, " ");
      append(piece, i, i + 1);
      i += 1;
    }

    if (normalized.endsWith(" ")) { normalized = normalized.slice(0, -1); map.pop(); }
    return { normalized, map };
  };

  const findNormalizedRange = (text, query) => {
    const q = normalize(query);
    if (!q) return null;
    const { normalized, map } = normalizeWithMap(text);
    const idx = normalized.indexOf(q);
    if (idx < 0 || !map[idx] || !map[idx + q.length - 1]) return null;
    return { start: map[idx].start, end: map[idx + q.length - 1].end };
  };

  const makeSnippet = (record, query) => {
    const candidates = [record.summary || "", record.text || ""];
    for (const raw of candidates) {
      const range = findNormalizedRange(raw, query);
      if (range) {
        const start = Math.max(0, range.start - 70);
        const end = Math.min(raw.length, range.end + 100);
        return `${start > 0 ? "…" : ""}${raw.slice(start, end).trim()}${end < raw.length ? "…" : ""}`;
      }
    }
    return (record.summary || record.text || "").slice(0, 190);
  };

  const appendHighlightedText = (node, text, query) => {
    const range = findNormalizedRange(text, query);
    if (!range) {
      node.textContent = text;
      return;
    }
    node.append(document.createTextNode(text.slice(0, range.start)));
    const mark = document.createElement("mark");
    mark.textContent = text.slice(range.start, range.end);
    node.append(mark, document.createTextNode(text.slice(range.end)));
  };

  const renderResults = (container, live, records, query, tracking = null) => {
    container.replaceChildren();
    activeResultIndex = -1;
    currentResultLinks = [];
    const q = normalize(query);
    if (q.length < 2) {
      if (live) live.textContent = "Zadajte aspoň dva znaky.";
      const hint = document.createElement("p");
      hint.className = "search-empty";
      hint.textContent = "Zadajte aspoň dva znaky. Hľadať môžete napríklad RCD, TN-C, Zs alebo revíznu správu.";
      container.append(hint);
      return;
    }

    const results = records
      .map((record) => scoreRecord(record, q))
      .filter(Boolean)
      .sort((a, b) => b.score - a.score || (a.record.type === "kb" ? -1 : 1))
      .slice(0, MAX_RESULTS);

    if (tracking?.enabled && !tracking.used) {
      tracking.used = true;
      window.beTrack?.("search_used", { page_path: location.pathname });
    }

    if (!results.length) {
      if (tracking?.enabled && !trackedNoResults.has(q)) {
        trackedNoResults.add(q);
        window.beTrack?.("search_no_results", { page_path: location.pathname });
      }
      if (live) live.textContent = "Nenašli sa žiadne výsledky.";
      const empty = document.createElement("div");
      empty.className = "search-empty";
      empty.innerHTML = '<strong>Nič sa nenašlo.</strong><p>Skúste iný výraz alebo pokračujte cez <a href="/poradna/">Poradňu</a>, <a href="/glosar/">Glosár</a> alebo <a href="/obsah/">Mapu obsahu</a>.</p>';
      container.append(empty);
      return;
    }

    if (live) live.textContent = `${results.length} výsledkov.`;
    const list = document.createElement("div");
    list.className = "search-result-list";
    results.forEach(({ record, targetUrl, bestHeading }) => {
      const link = document.createElement("a");
      link.className = "search-result";
      link.href = targetUrl;
      link.dataset.resultType = record.type;
      link.addEventListener("click", () => {
        window.beTrack?.("search_result_click", { result_type: record.type, page_path: location.pathname });
      });

      const top = document.createElement("span");
      top.className = "search-result__meta";
      top.textContent = bestHeading ? `${typeLabel(record.type)} · sekcia` : typeLabel(record.type);
      const title = document.createElement("strong");
      title.className = "search-result__title";
      appendHighlightedText(title, record.title, query);
      if (bestHeading) {
        const section = document.createElement("span");
        section.className = "search-result__section";
        appendHighlightedText(section, bestHeading.text, query);
        link.append(top, title, section);
      } else {
        link.append(top, title);
      }
      const snippet = document.createElement("span");
      snippet.className = "search-result__snippet";
      appendHighlightedText(snippet, makeSnippet(record, query), query);
      link.append(snippet);
      list.append(link);
    });
    container.append(list);
    currentResultLinks = [...list.querySelectorAll("a.search-result")];
  };

  const runSearch = async (input, results, live, tracking = null) => {
    try {
      const records = await loadIndex();
      renderResults(results, live, records, input.value, tracking);
    } catch (error) {
      console.error(error);
      if (live) live.textContent = "Vyhľadávanie sa nepodarilo načítať.";
      results.innerHTML = '<p class="search-empty">Vyhľadávanie sa nepodarilo načítať. Skúste <a href="/obsah/">Mapu obsahu</a>.</p>';
    }
  };

  const openFirstResult = async (input, results, live, tracking = null) => {
    if (!input || !results) return false;
    await runSearch(input, results, live, tracking);
    const first = results.querySelector("a.search-result");
    if (!first) return false;
    first.click();
    return true;
  };

  const buildOverlay = () => {
    if (overlay) return overlay;
    overlay = document.createElement("div");
    overlay.className = "site-search-overlay";
    overlay.hidden = true;
    overlay.innerHTML = `
      <div class="site-search-backdrop" data-search-close></div>
      <section class="site-search-dialog" role="dialog" aria-modal="true" aria-labelledby="site-search-title">
        <div class="site-search-head">
          <div><span class="eyebrow">Vyhľadávanie</span><h2 id="site-search-title">Nájdite pojem alebo otázku.</h2></div>
          <button class="site-search-close" type="button" data-search-close aria-label="Zavrieť vyhľadávanie">×</button>
        </div>
        <label class="site-search-label" for="site-search-overlay-input">Hľadať na Bezpečnej elektrike</label>
        <input id="site-search-overlay-input" class="site-search-input" type="search" autocomplete="off" spellcheck="false" placeholder="RCD, TN-C, poruchová slučka, revízna správa…">
        <p class="site-search-help">Na otvorenie: <kbd>Ctrl</kbd>+<kbd>K</kbd> alebo <kbd>/</kbd> · <kbd>Enter</kbd> otvorí prvý výsledok · <kbd>Esc</kbd> zatvorí.</p>
        <div class="site-search-live sr-only" aria-live="polite"></div>
        <div class="site-search-results"></div>
        <div class="site-search-footer"><a href="/obsah/">Mapa obsahu →</a><a href="/hladat/">Otvoriť samostatné vyhľadávanie →</a></div>
      </section>`;
    document.body.append(overlay);
    overlayInput = overlay.querySelector("#site-search-overlay-input");
    overlayResults = overlay.querySelector(".site-search-results");
    overlayLive = overlay.querySelector(".site-search-live");
    let timer = null;
    overlayInput.addEventListener("input", () => {
      clearTimeout(timer);
      if (normalize(overlayInput.value).length < 2) overlayTracking.used = false;
      timer = setTimeout(() => runSearch(overlayInput, overlayResults, overlayLive, Object.assign(overlayTracking, { enabled: true })), 450);
    });
    overlay.addEventListener("click", (event) => {
      if (event.target.closest("[data-search-close]")) closeOverlay();
    });
    overlay.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && event.target === overlayInput) {
        event.preventDefault();
        clearTimeout(timer);
        openFirstResult(overlayInput, overlayResults, overlayLive, Object.assign(overlayTracking, { enabled: true }));
      } else if (event.key === "ArrowDown" && currentResultLinks.length) {
        event.preventDefault();
        activeResultIndex = Math.min(activeResultIndex + 1, currentResultLinks.length - 1);
        currentResultLinks[activeResultIndex].focus();
      } else if (event.key === "ArrowUp" && currentResultLinks.length) {
        event.preventDefault();
        activeResultIndex = Math.max(activeResultIndex - 1, 0);
        currentResultLinks[activeResultIndex].focus();
      } else if (event.key === "Tab") {
        const focusables = [...overlay.querySelectorAll('button:not([disabled]), input:not([disabled]), a[href]')].filter((el) => !el.hidden);
        if (!focusables.length) return;
        const first = focusables[0], last = focusables[focusables.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    });
    return overlay;
  };

  const openOverlay = (trigger, initial = "") => {
    buildOverlay();
    lastTrigger = trigger || document.activeElement;
    overlay.hidden = false;
    document.documentElement.classList.add("search-open");
    overlayTracking = { used: false, enabled: true };
    overlayInput.value = initial;
    overlayInput.focus();
    if (initial) runSearch(overlayInput, overlayResults, overlayLive, { used: false, enabled: false });
    else renderResults(overlayResults, overlayLive, [], "");
  };

  const closeOverlay = () => {
    if (!overlay || overlay.hidden) return;
    overlay.hidden = true;
    document.documentElement.classList.remove("search-open");
    lastTrigger?.focus?.();
  };

  const setupInlineSearch = (root) => {
    const input = root.querySelector("[data-site-search-input]");
    const results = root.querySelector("[data-site-search-results]");
    const live = root.querySelector("[data-site-search-live]");
    if (!input || !results) return;
    let timer = null;
    const tracking = { used: false, enabled: true };
    input.addEventListener("input", () => {
      clearTimeout(timer);
      if (normalize(input.value).length < 2) tracking.used = false;
      timer = setTimeout(() => runSearch(input, results, live, tracking), 450);
      if (root.dataset.syncQuery === "true") {
        const url = new URL(location.href);
        if (input.value.trim()) url.searchParams.set("q", input.value.trim()); else url.searchParams.delete("q");
        history.replaceState(null, "", url);
      }
    });
    input.addEventListener("keydown", (event) => {
      if (event.key !== "Enter") return;
      event.preventDefault();
      clearTimeout(timer);
      openFirstResult(input, results, live, tracking);
    });
    const params = new URLSearchParams(location.search);
    let initial = params.get("q") || "";
    if (!initial && root.dataset.prefill404 === "true") {
      const last = decodeURIComponent(location.pathname.split("/").filter(Boolean).pop() || "");
      initial = last.replace(/[-_]+/g, " ");
    }
    if (initial) {
      input.value = initial;
      runSearch(input, results, live, { used: false, enabled: false });
    } else {
      renderResults(results, live, [], "");
    }
  };

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-search-open]").forEach((button) => {
      button.addEventListener("click", () => openOverlay(button));
    });
    document.querySelectorAll("[data-site-search]").forEach(setupInlineSearch);

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") { closeOverlay(); return; }
      const target = event.target;
      const typing = target && (target.matches?.("input, textarea, select") || target.isContentEditable);
      if (typing) return;
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        openOverlay(document.querySelector("[data-search-open]"));
      } else if (event.key === "/" && !event.ctrlKey && !event.metaKey && !event.altKey) {
        event.preventDefault();
        openOverlay(document.querySelector("[data-search-open]"));
      }
    });
  });

  window.beSearchNormalize = normalize;
})();
