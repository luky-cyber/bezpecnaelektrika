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
  const disclosure = document.querySelector("#player-disclosure");
  const download = document.querySelector("#player-download");

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
    audio.src = ep.audio;
    audio.load();
    title.textContent = ep.title;
    summary.textContent = ep.summary || "";
    category.textContent = ep.category || "Podcast";
    disclosure.textContent = `Zvuk vytvorený pomocou ${ep.aiAudio || "Gemini Notebook"}. Odborný obsah bol pred publikovaním skontrolovaný.`;
    download.href = ep.audio;
    download.classList.remove("is-disabled");
    download.setAttribute("aria-disabled","false");
    setEnabled(true);
    progress.value = 0;
    current.textContent = "0:00";
    duration.textContent = ep.duration || "0:00";
    document.querySelectorAll(".episode-card").forEach(c => c.classList.toggle("is-selected", c.dataset.id === ep.id));
    shell.scrollIntoView({behavior:"smooth",block:"center"});
  };

  try {
    const res = await fetch("/data/podcasts.json", {cache:"no-store"});
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
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
  } catch (err) {
    console.error("Podcast data:", err);
    list.innerHTML = '<p class="quiet">Zoznam epizód sa nepodarilo načítať. Skontrolujte, či stránku otvárate cez lokálny server alebo web.</p>';
  }

  toggle.addEventListener("click", async () => {
    if (!audio.src) return;
    if (audio.paused) {
      try { await audio.play(); } catch(e) { console.error(e); }
    } else audio.pause();
  });
  audio.addEventListener("play", () => { toggle.textContent = "❚❚"; toggle.setAttribute("aria-label","Pozastaviť"); });
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