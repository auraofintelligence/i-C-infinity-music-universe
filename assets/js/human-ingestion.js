const HUMAN_STORE_KEY = "ic-infinity-human-ingestion-v1";
const STUDIO_STORE_KEY = "ic-infinity-engine-studio-v1";

const signalPads = [
  ["WORD", "lyric / phrase", "teal"],
  ["HOOK", "hook arrives", "gold"],
  ["TURN", "meaning turns", "coral"],
  ["LIFT", "emotion lifts", "green"],
  ["DROP", "beat / energy drop", "coral"],
  ["BREAK", "section break", "ink"],
  ["IMAGE", "visual appears", "teal"],
  ["STEM", "stem to isolate", "gold"],
  ["CUT", "edit point", "ink"],
  ["HOLD", "hold the shot", "green"],
  ["LIGHT", "lighting shift", "gold"],
  ["CAM", "camera move", "teal"],
  ["INTRO", "opening scene", "teal"],
  ["VERSE", "story section", "ink"],
  ["CHORUS", "refrain / title", "gold"],
  ["BRIDGE", "contrast shift", "coral"],
  ["SOLO", "feature moment", "green"],
  ["OUTRO", "ending release", "ink"]
];

const metricDefinitions = [
  { key: "pace", label: "Pace", low: "slow", high: "fast", fallback: ["pace", "motion", "groove"], value: 50 },
  { key: "groove", label: "Groove", low: "loose", high: "driving", fallback: ["groove", "energy"], value: 55 },
  { key: "hook", label: "Hook", low: "subtle", high: "bold", fallback: ["hook", "lyricClarity"], value: 60 },
  { key: "vocal", label: "Vocal", low: "back", high: "front", fallback: ["vocal", "intimacy"], value: 58 },
  { key: "story", label: "Story", low: "vibe", high: "story", fallback: ["story", "emotion"], value: 52 },
  { key: "density", label: "Density", low: "clean", high: "busy", fallback: ["density", "texture", "awe"], value: 54 },
  { key: "tone", label: "Tone", low: "light", high: "intense", fallback: ["tone", "atmosphere", "light"], value: 56 },
  { key: "scale", label: "Scale", low: "close", high: "epic", fallback: ["scale", "shareFit"], value: 50 },
  { key: "finish", label: "Finish", low: "raw", high: "glossy", fallback: ["finish", "dynamics", "sonicPressure"], value: 48 }
];
let spotifyIframeApi = null;
const spotifyApiCallbacks = [];

window.onSpotifyIframeApiReady = (IFrameAPI) => {
  spotifyIframeApi = IFrameAPI;
  while (spotifyApiCallbacks.length) spotifyApiCallbacks.shift()(IFrameAPI);
};

function withSpotifyApi(callback) {
  if (spotifyIframeApi) {
    callback(spotifyIframeApi);
    return;
  }
  spotifyApiCallbacks.push(callback);
}

document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("[data-human-ingestion]");
  if (!root) return;

  const songs = readSongData();
  const state = loadState();
  let activeTab = "md";
  let timer = null;
  let lastTick = 0;
  let timerMode = "manual";
  let spotifyController = null;
  let spotifyControllerKey = "";
  let spotifyFallbackTimer = null;
  let spotifyStartFallbackTimer = null;
  let spotifyLastPlayingUpdate = 0;
  const spotifySync = { active: false, position: 0, duration: 0, anchor: 0 };

  const songSelect = document.getElementById("songSelect");
  const sourceFrame = document.getElementById("sourceFrame");
  const sourceLinks = document.getElementById("sourceLinks");
  const songLinkInput = document.getElementById("songLinkInput");
  const embedSongLink = document.getElementById("embedSongLink");
  const clock = document.getElementById("listenClock");
  const timerProgress = document.getElementById("timerProgress");
  const timerProgressBar = document.getElementById("timerProgressBar");
  const listenState = document.getElementById("listenState");
  const statusChip = document.getElementById("humanStatus");
  const fullscreenButton = document.getElementById("fullscreenButton");
  const topbarSong = document.getElementById("topbarSong");
  const signalGrid = document.getElementById("signalPads");
  const quickNote = document.getElementById("quickNote");
  const cueLog = document.getElementById("cueLog");
  const cueCount = document.getElementById("cueCount");
  const exportBox = document.getElementById("humanExport");
  const curveSelectors = document.getElementById("curveSelectors");
  const currentFocus = document.getElementById("currentFocus");
  let fallbackFullscreen = false;

  state.selectedSlug ||= songs[0]?.slug || "";
  state.activeSource ||= "auto";
  if (state.activeSource === "spotify" || state.activeSource === "custom-spotify") state.activeSource = "auto";
  state.customSource ||= null;
  state.elapsed ||= 0;
  state.sourceDuration ||= 0;
  state.cues ||= [];
  state.curves ||= [];
  state.currentValues = normaliseMetricValues(state.currentValues);
  state.cues = state.cues.map((cue) => ({ ...cue, values: normaliseMetricValues(cue.values) }));
  state.curves = state.curves.map((sample) => ({ ...sample, values: normaliseMetricValues(sample.values) }));

  populateSongs();
  renderPads();
  renderCurveMap();
  renderAll();

  songSelect.addEventListener("change", () => {
    state.selectedSlug = songSelect.value;
    state.activeSource = "auto";
    state.customSource = null;
    state.sourceDuration = 0;
    songLinkInput.value = "";
    syncStudioContext();
    persist();
    renderAll();
  });

  document.getElementById("timerStart").addEventListener("click", startTimer);
  document.getElementById("timerPause").addEventListener("click", pauseTimer);
  document.getElementById("timerBack").addEventListener("click", () => moveTime(-5));
  document.getElementById("timerForward").addEventListener("click", () => moveTime(5));
  document.getElementById("timerMark").addEventListener("click", () => addCue("MARK", "manual mark", "teal"));
  document.getElementById("addNoteCue").addEventListener("click", () => addCue("NOTE", "human note", "gold"));
  document.getElementById("clearCues").addEventListener("click", clearCues);
  document.getElementById("resetSession").addEventListener("click", resetSession);
  document.getElementById("copyHumanExport").addEventListener("click", copyExport);
  document.getElementById("downloadHumanMd").addEventListener("click", () => downloadFile("md"));
  document.getElementById("downloadHumanSrt").addEventListener("click", () => downloadFile("srt"));
  embedSongLink.addEventListener("click", embedPastedSongLink);
  songLinkInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      embedPastedSongLink();
    }
  });
  quickNote.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      addCue("NOTE", "human note", "gold");
    }
  });
  fullscreenButton.addEventListener("click", toggleFullscreen);
  document.addEventListener("fullscreenchange", updateFullscreenState);
  document.querySelectorAll("[data-human-tab]").forEach((button) => {
    button.addEventListener("click", () => activateHumanTab(button.dataset.humanTab));
  });
  activateHumanTab(document.body.dataset.humanActiveTab || "live");

  document.querySelectorAll("[data-export-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      activeTab = button.dataset.exportTab;
      document.querySelectorAll("[data-export-tab]").forEach((item) => item.classList.toggle("active", item === button));
      updateExport();
    });
  });

  curveSelectors.addEventListener("click", (event) => {
    const button = event.target.closest("[data-map-curve]");
    if (!button) return;
    const metric = metricDefinitions.find((item) => item.key === button.dataset.mapCurve);
    if (!metric) return;
    const rect = button.getBoundingClientRect();
    const direction = event.clientX < rect.left + (rect.width / 2) ? -1 : 1;
    nudgeCurveValue(metric.key, direction, direction > 0 ? metric.high : metric.low);
  });

  curveSelectors.addEventListener("keydown", (event) => {
    const button = event.target.closest("[data-map-curve]");
    if (!button) return;
    const metric = metricDefinitions.find((item) => item.key === button.dataset.mapCurve);
    if (!metric) return;
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      nudgeCurveValue(metric.key, -1, metric.low);
    }
    if (event.key === "ArrowRight" || event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      nudgeCurveValue(metric.key, 1, metric.high);
    }
  });

  function populateSongs() {
    const groups = new Map();
    songs.forEach((song) => {
      if (!groups.has(song.album)) groups.set(song.album, []);
      groups.get(song.album).push(song);
    });
    songSelect.innerHTML = "";
    groups.forEach((items, album) => {
      const group = document.createElement("optgroup");
      group.label = album;
      items.forEach((song) => {
        const option = document.createElement("option");
        option.value = song.slug;
        option.textContent = song.title;
        group.appendChild(option);
      });
      songSelect.appendChild(group);
    });
    songSelect.value = state.selectedSlug;
  }

  function renderPads() {
    signalGrid.innerHTML = "";
    signalPads.forEach(([label, meaning, colour]) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `human-pad ${colour}`;
      button.innerHTML = `<strong>${label}</strong><span>${meaning}</span>`;
      button.addEventListener("click", () => addCue(label, meaning, colour));
      signalGrid.appendChild(button);
    });
  }

  function activeSong() {
    return songs.find((song) => song.slug === state.selectedSlug) || songs[0] || {};
  }

  function renderAll(options = {}) {
    if (options.source !== false) renderSource();
    renderClock();
    renderCurveMap();
    renderLog();
    updateExport();
    syncStudioContext();
  }

  function renderSource() {
    const song = activeSong();
    const sources = sourceOptions(song);
    const selected = selectedSource(sources);
    if (selected?.type === "spotify" && selected.uri) {
      renderSpotifySource(song, selected);
    } else if (selected?.embed) {
      destroySpotifyController();
      sourceFrame.innerHTML = "";
      sourceFrame.innerHTML = iframeForSource(song, selected);
    } else if (selected?.url) {
      destroySpotifyController();
      sourceFrame.innerHTML = "";
      sourceFrame.innerHTML = sourceCard(song, selected);
    } else {
      destroySpotifyController();
      sourceFrame.innerHTML = "";
      sourceFrame.innerHTML = '<div class="human-empty-source">Paste a public song link or choose a catalogue source.</div>';
    }

    sourceLinks.innerHTML = sources
      .filter((source) => source.url || source.embed)
      .map((source) => `<button type="button" class="${source.key === selected?.key ? "active" : ""}" data-source-key="${escapeAttr(source.key)}">${escapeHtml(source.label)}</button>`)
      .join("");
    sourceLinks.querySelectorAll("[data-source-key]").forEach((button) => {
      button.addEventListener("click", () => {
        state.activeSource = button.dataset.sourceKey;
        persist();
        renderSource();
      });
    });
    topbarSong.textContent = `${song.title || "Untitled song"}${song.album ? ` / ${song.album}` : ""}`;
    currentFocus.textContent = focusCue(song);
  }

  function sourceOptions(song) {
    const options = [
      { key: "page", label: "Song page", url: song.songPage, embed: song.songPage, type: "page" },
      { key: "youtube", label: "YouTube", url: song.youtubeUrl, embed: song.youtubeEmbed, type: "youtube" },
      { key: "spotify", label: "Spotify", url: song.spotifyUrl, embed: song.spotifyEmbed, uri: song.spotifyUri, type: "spotify" },
      { key: "apple", label: "Apple", url: song.appleUrl, embed: song.appleEmbed, type: "apple" }
    ];
    if (state.customSource?.embed || state.customSource?.url) options.unshift(state.customSource);
    return options.filter((source) => source.url || source.embed);
  }

  function selectedSource(sources) {
    if (!sources.length) return null;
    if (state.activeSource && state.activeSource !== "auto") {
      const explicit = sources.find((source) => source.key === state.activeSource);
      if (explicit) return explicit;
    }
    return sources.find((source) => source.type === "youtube" && source.embed)
      || sources.find((source) => source.type === "apple" && source.embed)
      || sources.find((source) => source.type === "spotify" && source.embed)
      || sources[0];
  }

  function iframeForSource(song, source) {
    const src = source.type === "youtube" ? withYouTubeOrigin(source.embed) : source.embed;
    const title = `${song.title || "Selected song"} on ${source.label}`;
    if (source.type === "youtube") {
      return `<iframe title="${escapeAttr(title)}" src="${escapeAttr(src)}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" loading="lazy" allowfullscreen></iframe>`;
    }
    if (source.type === "spotify") {
      return `<iframe title="${escapeAttr(title)}" src="${escapeAttr(src)}" loading="lazy" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>`;
    }
    if (source.type === "apple") {
      return `<iframe title="${escapeAttr(title)}" src="${escapeAttr(src)}" loading="lazy" allow="autoplay *; encrypted-media *; fullscreen *"></iframe>`;
    }
    return `<iframe title="${escapeAttr(title)}" src="${escapeAttr(src)}" loading="lazy"></iframe>`;
  }

  function sourceCard(song, source) {
    return `<div class="human-empty-source"><strong>${escapeHtml(source.label)}</strong><span>${escapeHtml(song.title || "Selected song")}</span><small>${escapeHtml(source.url || "")}</small></div>`;
  }

  function renderSpotifySource(song, source) {
    const key = source.uri || source.embed || source.url;
    if (spotifyController && spotifyControllerKey === key && sourceFrame.querySelector(".human-spotify-api")) return;
    destroySpotifyController();
    sourceFrame.innerHTML = '<div class="human-spotify-api"><span>Loading Spotify sync...</span></div>';
    const target = sourceFrame.querySelector(".human-spotify-api");
    spotifyFallbackTimer = window.setTimeout(() => {
      if (!spotifyController && target.isConnected) {
        sourceFrame.innerHTML = iframeForSource(song, source);
        timerMode = "manual";
        renderTimerProgress();
      }
    }, 4500);
    withSpotifyApi((IFrameAPI) => {
      if (!target.isConnected) return;
      if (spotifyFallbackTimer) window.clearTimeout(spotifyFallbackTimer);
      spotifyFallbackTimer = null;
      const width = Math.max(300, Math.round(sourceFrame.clientWidth || 480));
      const height = Math.max(208, Math.round(sourceFrame.clientHeight || 208));
      IFrameAPI.createController(target, { uri: source.uri, width, height }, (controller) => {
        spotifyController = controller;
        spotifyControllerKey = key;
        timerMode = "spotify";
        controller.addListener("ready", () => {
          setTimerState("standby");
          renderTimerProgress("Spotify sync ready");
        });
        controller.addListener("playback_started", () => {
          timerMode = "spotify";
          spotifySync.active = true;
          spotifySync.anchor = performance.now();
          ensureTimerTick();
          setTimerState("spotify sync");
          renderClock();
        });
        controller.addListener("playback_update", handleSpotifyPlaybackUpdate);
        renderTimerProgress("Spotify sync ready");
      });
    });
  }

  function destroySpotifyController() {
    if (spotifyFallbackTimer) window.clearTimeout(spotifyFallbackTimer);
    if (spotifyStartFallbackTimer) window.clearTimeout(spotifyStartFallbackTimer);
    spotifyFallbackTimer = null;
    spotifyStartFallbackTimer = null;
    if (spotifyController?.destroy) {
      try {
        spotifyController.destroy();
      } catch (error) {
        console.warn("Could not destroy Spotify controller", error);
      }
    }
    spotifyController = null;
    spotifyControllerKey = "";
    spotifySync.active = false;
    spotifySync.duration = 0;
    state.sourceDuration = 0;
  }

  function embedPastedSongLink() {
    const source = sourceFromUrl(songLinkInput.value);
    if (!source) {
      sourceFrame.innerHTML = '<div class="human-empty-source">Could not recognise that as a YouTube, Spotify, Apple, or song-page link yet.</div>';
      return;
    }
    state.customSource = source;
    state.activeSource = source.key;
    persist();
    renderAll();
  }

  function sourceFromUrl(rawValue) {
    const raw = clean(rawValue);
    if (!raw) return null;
    let url;
    try {
      url = new URL(raw, window.location.href);
    } catch {
      return null;
    }
    const knownSong = songs.find((song) => samePath(url, song.songPage));
    if (knownSong) {
      state.selectedSlug = knownSong.slug;
      songSelect.value = knownSong.slug;
      return { key: "custom-page", label: "Song page", url: knownSong.songPage, embed: knownSong.songPage, type: "page" };
    }
    const youtube = youtubeEmbedFromUrl(url);
    if (youtube) return { key: "custom-youtube", label: "YouTube", url: raw, embed: youtube, type: "youtube" };
    const spotify = spotifyDetailsFromUrl(url);
    if (spotify) return { key: "custom-spotify", label: "Spotify", url: raw, embed: spotify.embed, uri: spotify.uri, type: "spotify" };
    if (/music\.apple\.com$/i.test(url.hostname) || /music\.apple\.com$/i.test(url.hostname.replace(/^embed\./, ""))) {
      return { key: "custom-apple", label: "Apple", url: raw, embed: raw.replace("https://music.apple.com/", "https://embed.music.apple.com/"), type: "apple" };
    }
    return null;
  }

  function startTimer() {
    const selected = selectedSource(sourceOptions(activeSong()));
    if (selected?.type === "spotify" && spotifyController?.resume) {
      timerMode = "spotify";
      setTimerState("starting");
      const runRequestedAt = performance.now();
      try {
        spotifyController.resume();
        if (spotifyStartFallbackTimer) window.clearTimeout(spotifyStartFallbackTimer);
        spotifyStartFallbackTimer = window.setTimeout(() => {
          spotifyStartFallbackTimer = null;
          if (timerMode === "spotify" && spotifyLastPlayingUpdate < runRequestedAt) startManualTimer();
        }, 1800);
      } catch (error) {
        console.warn("Could not start Spotify controller", error);
        startManualTimer();
      }
      return;
    }
    startManualTimer();
  }

  function pauseTimer() {
    if (spotifyStartFallbackTimer) window.clearTimeout(spotifyStartFallbackTimer);
    spotifyStartFallbackTimer = null;
    if (timerMode === "spotify" && spotifyController?.pause) {
      try {
        spotifyController.pause();
      } catch (error) {
        console.warn("Could not pause Spotify controller", error);
      }
    }
    stopTicker();
    spotifySync.active = false;
    setTimerState("paused");
    persist();
  }

  function moveTime(delta) {
    const nextTime = Math.max(0, state.elapsed + delta);
    if (timerMode === "spotify" && spotifyController?.seek) {
      try {
        spotifyController.seek(nextTime);
      } catch (error) {
        console.warn("Could not seek Spotify controller", error);
      }
      spotifySync.position = nextTime;
      spotifySync.anchor = performance.now();
    }
    state.elapsed = nextTime;
    sampleCurves("time nudge");
    persist();
    renderAll({ source: false });
  }

  function addCue(label, meaning, colour) {
    const note = clean(quickNote.value);
    const cue = {
      id: Date.now(),
      time: state.elapsed,
      label,
      meaning,
      colour,
      note,
      values: { ...state.currentValues }
    };
    state.cues.push(cue);
    quickNote.value = "";
    sampleCurves(label);
    syncStudioContext();
    persist();
    renderAll({ source: false });
  }

  function sampleCurves(source) {
    state.curves.push({ time: state.elapsed, source, values: { ...state.currentValues } });
    state.curves = state.curves.slice(-80);
  }

  function setCurveValue(name, value, source) {
    state.currentValues[name] = clamp(value, 0, 100);
    sampleCurves(source || name);
    persist();
    renderCurveMap();
    updateExport();
  }

  function renderCurveMap() {
    if (!curveSelectors) return;
    curveSelectors.innerHTML = metricDefinitions.map((metric) => {
      const value = Number(state.currentValues[metric.key] || 0);
      const angle = -135 + (value / 100) * 270;
      return `<button type="button" class="human-map-button" data-map-curve="${escapeAttr(metric.key)}" style="--dial-value: ${value}%; --dial-angle: ${angle.toFixed(1)}deg" title="Tap the left side to move toward ${escapeAttr(metric.low)}. Tap the right side to move toward ${escapeAttr(metric.high)}."><span class="human-dial-hit left" aria-hidden="true">-</span><span class="human-dial-hit right" aria-hidden="true">+</span><span class="human-dial-face" aria-hidden="true"><i></i></span><span class="human-dial-copy"><strong>${escapeHtml(metric.label)}</strong><b><em>LEFT - ${escapeHtml(metric.low)}</em><em>${escapeHtml(metric.high)} + RIGHT</em></b></span><span class="human-dial-value">${value}</span></button>`;
    }).join("");
  }

  function nudgeCurveValue(name, direction, source) {
    const current = Number(state.currentValues[name] || 0);
    setCurveValue(name, current + (direction * 10), source);
  }

  function startManualTimer() {
    timerMode = "manual";
    spotifySync.active = false;
    ensureTimerTick();
    setTimerState("listening");
  }

  function ensureTimerTick() {
    if (timer) return;
    lastTick = performance.now();
    timer = window.setInterval(tickTimer, 100);
  }

  function stopTicker() {
    if (timer) window.clearInterval(timer);
    timer = null;
  }

  function tickTimer() {
    const now = performance.now();
    if (timerMode === "spotify" && spotifySync.active) {
      state.elapsed = spotifySync.position + ((now - spotifySync.anchor) / 1000);
      if (spotifySync.duration) state.elapsed = Math.min(state.elapsed, spotifySync.duration);
    } else {
      state.elapsed += (now - lastTick) / 1000;
    }
    lastTick = now;
    renderClock();
  }

  function handleSpotifyPlaybackUpdate(event) {
    const data = event?.data || {};
    const position = spotifyMsToSeconds(data.position);
    const duration = spotifyMsToSeconds(data.duration);
    const paused = data.isPaused === true || data.paused === true;
    const wasActive = spotifySync.active;
    if (Number.isFinite(duration) && duration > 0) {
      spotifySync.duration = duration;
      state.sourceDuration = duration;
    }
    if (Number.isFinite(position)) {
      spotifySync.position = position;
      state.elapsed = position;
    }
    spotifySync.anchor = performance.now();
    if (!paused) {
      timerMode = "spotify";
      spotifySync.active = true;
      spotifyLastPlayingUpdate = performance.now();
      if (spotifyStartFallbackTimer) window.clearTimeout(spotifyStartFallbackTimer);
      spotifyStartFallbackTimer = null;
      ensureTimerTick();
      setTimerState("spotify sync");
    } else if (wasActive) {
      spotifySync.active = false;
      timerMode = "spotify";
      stopTicker();
      setTimerState("paused");
    } else if (!timer && listenState.textContent !== "paused") {
      spotifySync.active = false;
      setTimerState("standby");
    }
    renderClock();
    persist();
  }

  function setTimerState(label) {
    listenState.textContent = label;
    statusChip.classList.toggle("live", ["listening", "spotify sync", "starting"].includes(label));
    statusChip.classList.toggle("paused", label === "paused");
  }

  function renderClock() {
    clock.textContent = formatClock(state.elapsed);
    renderTimerProgress();
  }

  function renderTimerProgress(message = "") {
    if (!timerProgress || !timerProgressBar) return;
    const duration = spotifySync.duration || state.sourceDuration || 0;
    if (duration > 0) {
      const elapsed = Math.min(Math.max(state.elapsed, 0), duration);
      const percent = Math.min(100, (elapsed / duration) * 100);
      const modeLabel = timerMode === "spotify" ? "Spotify sync" : "manual timer";
      timerProgress.textContent = `${formatClock(elapsed)} / ${formatClock(duration)} | ${modeLabel}`;
      timerProgressBar.style.width = `${percent.toFixed(1)}%`;
      return;
    }
    timerProgress.textContent = message || (timerMode === "spotify" ? "Spotify sync ready" : "manual timer ready");
    timerProgressBar.style.width = "0%";
  }

  function renderLog() {
    cueLog.innerHTML = "";
    state.cues.slice().reverse().forEach((cue) => {
      const item = document.createElement("li");
      item.innerHTML = `<span>${formatClock(cue.time)}</span><strong>${escapeHtml(cue.label)}</strong><em>${escapeHtml(cue.note || cue.meaning)}</em>`;
      cueLog.appendChild(item);
    });
    cueCount.textContent = `${state.cues.length} cue${state.cues.length === 1 ? "" : "s"}`;
  }

  function updateExport() {
    const logActive = activeTab === "log";
    exportBox.hidden = logActive;
    cueLog.hidden = !logActive;
    if (!logActive) exportBox.value = outputText();
  }

  function outputText() {
    if (activeTab === "log") return buildLogText();
    return activeTab === "srt" ? buildSrt() : buildMarkdown();
  }

  function buildMarkdown() {
    const song = activeSong();
    const cues = state.cues.map((cue) => `- ${formatClock(cue.time)} | ${cue.label} | ${cue.note || cue.meaning} | ${metricSnapshot(cue.values)}`).join("\n");
    const curves = metricDefinitions.map((metric) => `${metric.label}: ${state.currentValues[metric.key]} (${metric.low} -> ${metric.high})`).join("\n");
    return `# Human Guided Ingestion - ${song.title || "Untitled song"}\n\nStatus: human listening pass\nGenerated: ${new Date().toISOString().slice(0, 10)}\nSong page: ${song.songPage || ""}\nAlbum: ${song.album || ""}\nYouTube: ${song.youtubeUrl || ""}\nSpotify: ${song.spotifyUrl || ""}\nApple: ${song.appleUrl || ""}\n\n## Purpose\n\nReverse-engineer the song from human listening into imagination, timing, video direction, metadata, and cue signals for the Infinity Engine.\n\n## Listening Dials\n\n${curves}\n\n## Human Signal Cues\n\n${cues || "- No cues recorded yet."}\n\n## Infinity Engine Translation\n\n- Use WORD / HOOK / TURN cues to identify lyric moments and image prompts.\n- Use LIFT / DROP / BREAK cues to plan first keyframes, last keyframes, and in-between beats.\n- Use INTRO / VERSE / CHORUS / BRIDGE / SOLO / OUTRO cues to organise sections before keyframe choices.\n- Use IMAGE / LIGHT / CAM cues for visual world, camera motion, lighting, and shot design.\n- Use PACE / GROOVE / HOOK / VOCAL / STORY / DENSITY / TONE / SCALE / FINISH dials to guide visual rhythm, edit density, shot size, captions, thumbnails, and platform-safe marketing tags.\n- Use STEM cues to request stems or isolate sound layers before video timing.\n`;
  }

  function buildSrt() {
    if (!state.cues.length) return "";
    return state.cues.map((cue, index) => {
      const start = cue.time;
      const end = state.cues[index + 1]?.time || cue.time + 3;
      return `${index + 1}\n${formatSrt(start)} --> ${formatSrt(Math.max(end, start + 1))}\n${cue.label}: ${cue.note || cue.meaning}\n`;
    }).join("\n");
  }

  function buildLogText() {
    if (!state.cues.length) return "No human observations recorded yet.";
    return state.cues
      .slice()
      .reverse()
      .map((cue) => `${formatClock(cue.time)} | ${cue.label} | ${cue.note || cue.meaning}`)
      .join("\n");
  }

  function syncStudioContext() {
    const song = activeSong();
    try {
      const parsed = JSON.parse(localStorage.getItem(STUDIO_STORE_KEY)) || {};
      parsed.forms ||= {};
      parsed.context ||= {};
      parsed.carried ||= {};
      parsed.context.songTitle = song.title || "";
      parsed.context.songPage = song.songPage || "";
      parsed.context.audioSource = compactLines([
        line("Song page", song.songPage),
        line("YouTube", song.youtubeUrl),
        line("Spotify", song.spotifyUrl),
        line("Apple", song.appleUrl)
      ]);
      parsed.context.lyricStatus = song.lyricStatus || (song.hasLyrics ? "Lyrics imported on the song page." : "Lyrics not imported yet.");
      parsed.context.lyricsSource = song.hasLyrics
        ? compactLines([parsed.context.lyricStatus, line("Song page", song.songPage)])
        : parsed.context.lyricStatus;
      parsed.context.lyricsText = song.lyrics || "";
      if (!clean(parsed.context.lyricalSummary) && clean(song.meaning)) parsed.context.lyricalSummary = song.meaning;
      parsed.context.targetQuery ||= "Use the human listening cues to recommend respectful, non-intrusive visual and distribution variants.";
      parsed.context.metadataTags = [song.album, ...(song.themes || [])].filter(Boolean).join("\n");
      parsed.context.videoTimingNotes = state.cues.map((cue) => `${formatClock(cue.time)} ${cue.label}: ${cue.note || cue.meaning}`).join("\n");
      parsed.context.audioTimingNotes = parsed.context.videoTimingNotes;
      localStorage.setItem(STUDIO_STORE_KEY, JSON.stringify(parsed));
    } catch (error) {
      console.warn("Could not sync human listening context", error);
    }
  }

  async function copyExport() {
    await navigator.clipboard.writeText(outputText());
  }

  function downloadFile(type) {
    const song = activeSong();
    const body = type === "srt" ? buildSrt() : buildMarkdown();
    const ext = type === "srt" ? "srt" : "md";
    const blob = new Blob([body], { type: type === "srt" ? "text/plain;charset=utf-8" : "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `human-ingestion-${new Date().toISOString().slice(0, 10)}-${slugify(song.title || "song")}.${ext}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function clearCues() {
    state.cues = [];
    state.curves = [];
    persist();
    renderAll({ source: false });
  }

  function resetSession() {
    pauseTimer();
    state.elapsed = 0;
    state.cues = [];
    state.curves = [];
    persist();
    renderAll();
  }

  function toggleFullscreen() {
    const active = Boolean(document.fullscreenElement) || (fallbackFullscreen && document.body.classList.contains("human-fullscreen"));
    if (active) {
      fallbackFullscreen = false;
      document.body.classList.remove("human-fullscreen");
      if (document.fullscreenElement) document.exitFullscreen?.();
      updateFullscreenState();
      return;
    }
    if (document.documentElement.requestFullscreen) {
      fallbackFullscreen = false;
      document.documentElement.requestFullscreen().catch(() => {
        fallbackFullscreen = true;
        document.body.classList.add("human-fullscreen");
        updateFullscreenState();
      });
      return;
    }
    fallbackFullscreen = true;
    document.body.classList.add("human-fullscreen");
    updateFullscreenState();
  }

  function updateFullscreenState() {
    if (!document.fullscreenElement && !fallbackFullscreen) document.body.classList.remove("human-fullscreen");
    const active = Boolean(document.fullscreenElement) || (fallbackFullscreen && document.body.classList.contains("human-fullscreen"));
    document.body.classList.toggle("human-fullscreen", active);
    root.classList.toggle("is-fullscreen", active);
    fullscreenButton.textContent = active ? "EXT" : "FUL";
    fullscreenButton.dataset.icon = active ? "X" : "F";
  }

  function activateHumanTab(tabName) {
    document.body.dataset.humanActiveTab = tabName || "live";
    document.querySelectorAll("[data-human-tab]").forEach((button) => {
      button.classList.toggle("active", button.dataset.humanTab === document.body.dataset.humanActiveTab);
    });
  }

  function persist() {
    localStorage.setItem(HUMAN_STORE_KEY, JSON.stringify(state));
  }
});

function readSongData() {
  try {
    return JSON.parse(document.getElementById("humanSongData").textContent);
  } catch (error) {
    console.warn("Could not read embedded song data", error);
    return [];
  }
}

function focusCue(song) {
  const tags = (song.themes || []).slice(0, 2).join(" / ");
  return tags ? `${tags}: hook, turn, first image.` : "Hook, turn, first image.";
}

function samePath(url, relativePath) {
  try {
    const target = new URL(relativePath, window.location.href);
    return trimSlash(url.pathname) === trimSlash(target.pathname);
  } catch {
    return false;
  }
}

function trimSlash(value) {
  return String(value || "").replace(/\/+$/, "");
}

function youtubeEmbedFromUrl(url) {
  const host = url.hostname.replace(/^www\./, "");
  let id = "";
  if (host === "youtu.be") id = url.pathname.split("/").filter(Boolean)[0] || "";
  if (host.endsWith("youtube.com")) {
    if (url.pathname.startsWith("/watch")) id = url.searchParams.get("v") || "";
    if (url.pathname.startsWith("/shorts/") || url.pathname.startsWith("/embed/")) id = url.pathname.split("/").filter(Boolean)[1] || "";
  }
  if (!id) return "";
  const embed = new URL(`https://www.youtube.com/embed/${id}`);
  const list = url.searchParams.get("list");
  if (list) embed.searchParams.set("list", list);
  embed.searchParams.set("rel", "0");
  return embed.toString();
}

function spotifyDetailsFromUrl(url) {
  const match = url.href.match(/open\.spotify\.com\/(track|album|playlist)\/([A-Za-z0-9]+)/);
  if (!match) return null;
  return {
    embed: `https://open.spotify.com/embed/${match[1]}/${match[2]}?utm_source=generator`,
    uri: `spotify:${match[1]}:${match[2]}`
  };
}

function spotifyMsToSeconds(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number / 1000 : NaN;
}

function withYouTubeOrigin(embedUrl) {
  try {
    const url = new URL(embedUrl);
    if (window.location.origin.startsWith("http")) url.searchParams.set("origin", window.location.origin);
    url.searchParams.set("rel", "0");
    return url.toString();
  } catch {
    return embedUrl;
  }
}

function loadState() {
  try {
    return JSON.parse(localStorage.getItem(HUMAN_STORE_KEY)) || {};
  } catch (error) {
    console.warn("Could not load human ingestion state", error);
    return {};
  }
}

function normaliseMetricValues(values = {}) {
  return metricDefinitions.reduce((next, metric) => {
    const existing = values?.[metric.key];
    const fallbackValue = [metric.fallback].flat().map((key) => values?.[key]).find((value) => value !== undefined && value !== null);
    next[metric.key] = clamp(existing ?? fallbackValue ?? metric.value, 0, 100);
    return next;
  }, {});
}

function metricSnapshot(values = {}) {
  const safeValues = normaliseMetricValues(values);
  return metricDefinitions
    .map((metric) => `${metric.label.toLowerCase()} ${safeValues[metric.key]}`)
    .join(" / ");
}

function formatClock(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = Math.floor(totalSeconds % 60);
  const tenths = Math.floor((totalSeconds % 1) * 10);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}.${tenths}`;
}

function formatSrt(totalSeconds) {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = Math.floor(totalSeconds % 60);
  const millis = Math.floor((totalSeconds % 1) * 1000);
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")},${String(millis).padStart(3, "0")}`;
}

function clean(value) {
  return String(value || "").trim();
}

function line(label, value) {
  if (!clean(value)) return "";
  return `${label}: ${clean(value)}`;
}

function compactLines(values) {
  return values.filter((value) => clean(value)).join("\n");
}

function clamp(value, min, max) {
  const number = Number(value);
  if (!Number.isFinite(number)) return min;
  return Math.min(max, Math.max(min, Math.round(number)));
}

function escapeHtml(value) {
  return clean(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
}

function escapeAttr(value) {
  return escapeHtml(value);
}

function slugify(value) {
  return clean(value).toLowerCase().replace(/&/g, " and ").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "song";
}
