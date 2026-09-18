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
  const safetyNote = document.querySelector("#player-safety-note");
  const download = document.querySelector("#player-download");
  const playerStatus = document.querySelector("#player-status");
  let trackedEpisodeId = null;
  let currentEpisode = null;

  const fmt = (s) => { if (!Number.isFinite(s)) return "0:00"; const m=Math.floor(s/60); const sec=Math.floor(s%60).toString().padStart(2,"0"); return `${m}:${sec}`; };
  const setEnabled = (enabled) => { [toggle,back,forward,progress,speed,volume].forEach(el=>{if(el) el.disabled=!enabled;}); shell.classList.toggle("is-empty",!enabled); };
  const setPlayerStatus = (message="",isError=false) => { if(!playerStatus)return; playerStatus.textContent=message; playerStatus.hidden=!message; playerStatus.classList.toggle("is-error",Boolean(message&&isError)); };
  const ensureAudioSource = () => { if (!currentEpisode?.audio) return false; if (audio.getAttribute("src") !== currentEpisode.audio) audio.src=currentEpisode.audio; return true; };

  const selectEpisode = (ep) => {
    if (!ep?.audio || !ep.published) return;
    audio.pause(); audio.removeAttribute("src"); trackedEpisodeId=null; currentEpisode=ep; setPlayerStatus();
    toggle.textContent="▶"; toggle.setAttribute("aria-label","Prehrať");
    title.textContent=ep.title; summary.textContent=ep.summary||""; category.textContent=ep.category||"Podcast"; if(playerId) playerId.textContent=ep.id||"BE";
    disclosure.textContent=`Zvuk vytvorený pomocou ${ep.aiAudio||"Gemini Notebook"}. Odborný základ a transcript boli pred publikovaním skontrolované. Audio má edukatívny charakter.`;
    if (safetyNote) { safetyNote.hidden=!ep.editorialCorrections; safetyNote.innerHTML=ep.editorialCorrections ? `<strong>Pred prehratím:</strong> ${ep.correctionsNote||"Epizóda obsahuje redakčné odborné spresnenia."} <a href="${ep.page}#odborne-spresnenia">Pozrieť spresnenia →</a>` : ""; }
    download.href=ep.audio; download.removeAttribute("tabindex"); download.classList.remove("is-disabled"); download.setAttribute("aria-disabled","false");
    setEnabled(true); progress.value=0; current.textContent="0:00"; duration.textContent=ep.duration||"0:00";
    document.querySelectorAll(".episode-card").forEach(c=>{ const selected=c.dataset.id===ep.id; c.classList.toggle("is-selected",selected); if(selected)c.setAttribute("aria-current","true"); else c.removeAttribute("aria-current"); const b=c.querySelector(".episode-play"); if(b){b.textContent=selected?"✓ Vybraná epizóda":"Vybrať epizódu"; b.setAttribute("aria-pressed",String(selected));} });
  };

  try {
    const res=await fetch("/data/podcasts.json",{cache:"no-store"}); if(!res.ok) throw new Error(`HTTP ${res.status}`); const data=await res.json(); const episodes=Array.isArray(data.episodes)?data.episodes:[];
    episodes.forEach(ep=>{ const btn=list.querySelector(`.episode-card[data-id="${ep.id}"] .episode-play`); if(btn) btn.addEventListener("click",()=>selectEpisode(ep)); });
    const featured=episodes.find(ep=>ep.published&&ep.audio&&ep.featured)||episodes.find(ep=>ep.published&&ep.audio); if(featured) selectEpisode(featured);
  } catch(err) { console.error("Podcast data:",err); setPlayerStatus("Interaktívny prehrávač sa momentálne nepodarilo pripraviť. Zoznam epizód a odkazy na ich stránky zostávajú dostupné nižšie.",true); }

  toggle.addEventListener("click",async()=>{ if(!currentEpisode||!ensureAudioSource())return; if(audio.paused){try{setPlayerStatus();await audio.play();}catch(e){console.error(e);setPlayerStatus("Prehrávanie sa nepodarilo spustiť. Skúste to znova alebo použite odkaz Stiahnuť MP3.",true);}}else audio.pause(); });
  audio.addEventListener("play",()=>{toggle.textContent="❚❚";toggle.setAttribute("aria-label","Pozastaviť");const episodeId=playerId?.textContent||"BE";if(trackedEpisodeId!==episodeId){trackedEpisodeId=episodeId;window.beTrack?.("podcast_play",{episode_id:episodeId,page_path:location.pathname});}});
  audio.addEventListener("pause",()=>{toggle.textContent="▶";toggle.setAttribute("aria-label","Prehrať");});
  audio.addEventListener("loadedmetadata",()=>{duration.textContent=fmt(audio.duration);setPlayerStatus();});
  audio.addEventListener("error",()=>setPlayerStatus("Audio sa momentálne nepodarilo načítať. Skúste stránku obnoviť alebo použite odkaz Stiahnuť MP3.",true));
  audio.addEventListener("timeupdate",()=>{current.textContent=fmt(audio.currentTime);if(Number.isFinite(audio.duration)&&audio.duration>0)progress.value=Math.round((audio.currentTime/audio.duration)*1000);});
  progress.addEventListener("input",()=>{if(Number.isFinite(audio.duration))audio.currentTime=(Number(progress.value)/1000)*audio.duration;});
  back.addEventListener("click",()=>{audio.currentTime=Math.max(0,audio.currentTime-15);}); forward.addEventListener("click",()=>{audio.currentTime=Math.min(audio.duration||Infinity,audio.currentTime+15);}); speed.addEventListener("change",()=>{audio.playbackRate=Number(speed.value);}); volume.addEventListener("input",()=>{audio.volume=Number(volume.value);});
});
