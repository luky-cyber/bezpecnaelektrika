document.addEventListener("DOMContentLoaded", async () => {
  const list = document.querySelector("#podcast-list");
  const shell = document.querySelector("#podcast-player");
  if (!list || !shell) return;

  const audio = document.querySelector("#podcast-audio");
  const toggle = document.querySelector("#player-toggle");
  const back = document.querySelector("#player-back");
  const forward = document.querySelector("#player-forward");
  const progress = document.querySelector("#player-progress");
  const current = document.querySelector("#player-current");
  const duration = document.querySelector("#player-duration");
  const speed = document.querySelector("#player-speed");
  const volume = document.querySelector("#player-volume");
  const title = document.querySelector("#player-title");
  const summary = document.querySelector("#player-summary");
  const category = document.querySelector("#player-category");
  const playerId = document.querySelector("#player-id");
  const disclosure = document.querySelector("#player-disclosure");
  const download = document.querySelector("#player-download");
  let trackedEpisodeId = null;

  const fmt = (s) => {
    if (!Number.isFinite(s)) return "0:00";
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60).toString().padStart(2, "0");
    return `${m}:${sec}`;
  };

  const setEnabled = (enabled) => {
    [toggle, back, forward, progress, speed, volume].forEach(el => { if (el) el.disabled = !enabled; });
    shell.classList.toggle("is-empty", !enabled);
  };

  const loadEpisode = (ep) => {
    if (!ep.audio || !ep.published) return;
    audio.pause();
    // Pri zmene epizódy sa nový diel nespúšťa automaticky.
    // Vizuálny stav prehrávača musí zodpovedať reálnemu stavu audia.
    toggle.textContent = "▶";
    toggle.setAttribute("aria-label", "Prehrať");
    trackedEpisodeId = null;
    audio.src = ep.audio;
    audio.load();
    title.textContent = ep.title;
    summary.textContent = ep.summary || "";
    category.textContent = ep.category || "Podcast";
    if (playerId) playerId.textContent = ep.id || "BE";
    disclosure.textContent = `Zvuk vytvorený pomocou ${ep.aiAudio || "Gemini Notebook"}. Odborný základ a transcript boli pred publikovaním skontrolované. Audio má edukatívny charakter.`;
    download.href = ep.audio;
    download.classList.remove("is-disabled");
    download.setAttribute("aria-disabled","false");
    setEnabled(true);
    progress.value = 0;
    current.textContent = "0:00";
    duration.textContent = ep.duration || "0:00";
    document.querySelectorAll(".episode-card").forEach(c => {
      const selected = c.dataset.id === ep.id;
      c.classList.toggle("is-selected", selected);
      if (selected) c.setAttribute("aria-current","true"); else c.removeAttribute("aria-current");
      const b=c.querySelector(".episode-play");
      if (b) b.textContent = selected ? "▶ Načítané" : "▶ Prehrať";
    });
  };

  try {
    const candidates = ["../data/podcasts.json", "/data/podcasts.json"];
    let data = null;
    let lastError = null;
    for (const url of candidates) {
      try {
        const res = await fetch(url, {cache:"no-store"});
        if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
        data = await res.json();
        break;
      } catch (err) { lastError = err; }
    }
    if (!data) throw lastError || new Error("Podcast JSON sa nepodarilo načítať");
    const episodes = Array.isArray(data.episodes) ? data.episodes : [];
    if (!episodes.length) {
      list.innerHTML = '<p class="quiet">Epizódy zatiaľ pripravujem.</p>';
      return;
    }
    list.innerHTML = "";
    episodes.forEach(ep => {
      const article = document.createElement("article");
      article.className = "episode-card" + (ep.published && ep.audio ? "" : " is-draft");
      article.dataset.id = ep.id;
      article.innerHTML = `
        <div class="episode-meta"><span class="tag">${ep.category || "Podcast"}</span><span>${ep.id}</span>${ep.duration ? `<span>${ep.duration}</span>` : ""}</div>
        <h3>${ep.title}</h3>
        <p>${ep.summary || ""}</p>
        <div class="episode-actions">
          ${ep.published && ep.audio ? '<button type="button" class="button episode-play">▶ Prehrať</button>' : '<span class="status-chip">Pripravujeme</span>'}
        </div>`;
      const btn = article.querySelector(".episode-play");
      if (btn) btn.addEventListener("click", () => loadEpisode(ep));
      list.appendChild(article);
    });

    const featured = episodes.find(ep => ep.published && ep.audio && ep.featured)
      || episodes.find(ep => ep.published && ep.audio);
    if (featured) loadEpisode(featured);
  } catch (err) {
    console.error("Podcast data:", err);
    list.innerHTML = '<p class="podcast-error"><strong>Zoznam epizód sa momentálne nepodarilo načítať.</strong><br>Skúste stránku obnoviť neskôr.</p>';
  }

  toggle.addEventListener("click", async () => {
    if (!audio.src) return;
    if (audio.paused) {
      try { await audio.play(); } catch(e) { console.error(e); }
    } else audio.pause();
  });
  audio.addEventListener("play", () => {
    toggle.textContent = "❚❚";
    toggle.setAttribute("aria-label","Pozastaviť");
    const episodeId = playerId?.textContent || "BE";
    if (trackedEpisodeId !== episodeId) {
      trackedEpisodeId = episodeId;
      window.beTrack?.("podcast_play", { episode_id: episodeId, page_path: location.pathname });
    }
  });
  audio.addEventListener("pause", () => { toggle.textContent = "▶"; toggle.setAttribute("aria-label","Prehrať"); });
  audio.addEventListener("loadedmetadata", () => { duration.textContent = fmt(audio.duration); });
  audio.addEventListener("timeupdate", () => {
    current.textContent = fmt(audio.currentTime);
    if (Number.isFinite(audio.duration) && audio.duration > 0) progress.value = Math.round((audio.currentTime / audio.duration) * 1000);
  });
  progress.addEventListener("input", () => {
    if (Number.isFinite(audio.duration)) audio.currentTime = (Number(progress.value) / 1000) * audio.duration;
  });
  back.addEventListener("click", () => { audio.currentTime = Math.max(0, audio.currentTime - 15); });
  forward.addEventListener("click", () => { audio.currentTime = Math.min(audio.duration || Infinity, audio.currentTime + 15); });
  speed.addEventListener("change", () => { audio.playbackRate = Number(speed.value); });
  volume.addEventListener("input", () => { audio.volume = Number(volume.value); });
});