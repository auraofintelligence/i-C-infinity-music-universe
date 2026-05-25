const INFINITY_STORE_KEY = "ic-infinity-engine-studio-v1";
const HUMAN_STORE_KEY = "ic-infinity-human-ingestion-v1";

const contextFieldKeys = {
  songTitle: "songTitle",
  songPage: "songPage",
  linkedIngestion: "linkedIngestion",
  albumWorld: "albumWorld",
  lyricalSummary: "lyricalSummary",
  emotionArc: "emotionArc",
  toneAndAudience: "toneAndAudience",
  keywordsAndSymbols: "keywordsAndSymbols",
  bpm: "bpm",
  keyPitch: "keyPitch",
  volumeDynamics: "volumeDynamics",
  beatMap: "beatMap",
  stemAccess: "stemAccess",
  videoTimingNotes: "videoTimingNotes",
  audioTimingNotes: "audioTimingNotes",
  audioSource: "audioSource",
  lyricsSource: "lyricsSource",
  lyricsText: "lyricsText",
  lyricStatus: "lyricStatus",
  ingestionTimingProfile: "audioTimingNotes",
  audioCue: "audioTimingNotes",
  timing: "audioTimingNotes",
  metadataTags: "metadataTags",
  metadataSeeds: "metadataTags",
  metadataPackage: "metadataTags",
  targetQuery: "targetQuery",
  nonIntrusiveDeployment: "nonIntrusiveDeployment",
  nonIntrusiveRules: "nonIntrusiveDeployment",
  accessibilityNotes: "accessibilityNotes",
  favouriteImageGen: "favouriteImageGen",
  favouriteVideoGen: "favouriteVideoGen",
  risksOrAvoid: "avoid",
  avoid: "avoid"
};

const studioPages = [
  page("humanIngestion", "001", "Human Listen", "human-ingestion.html", "Listen and tap cues."),
  page("ingestion", "007", "Ingestion", "ingestion.html", "Song profile."),
  page("songBrief", "01", "Visual Brief", "music-video.html", "Image/video brief."),
  page("storyboard", "02", "Storyboard", "storyboard.html", "Panel plan."),
  page("shot", "03", "Keyframe Shot", "keyframe-shot.html", "Motion shot."),
  page("variant", "04", "Distribution Fit", "variants.html", "Screen/export fit."),
  page("review", "05", "Review", "review.html", "Cut notes."),
  page("handoff", "06", "Handoff", "handoff.html", "Agent packet.")
];

const sharedBoundary = [
  "- Public pages should not expose private source-folder paths unless Luke deliberately adds them.",
  "- The songs already exist in the i C. infinity Music Universe song catalogue.",
  "- This Studio creates image, video, edit, and distribution assets for existing songs.",
  "- Ingestion comes before visual production: lyric, audio, stem, and metadata facts guide later choices.",
  "- Distribution targets should be recommended from a targeted query, not copied from a static list.",
  "- The comic/storyboard layer comes before expensive video generation.",
  "- Generator choices are editable because tools and prices change quickly.",
  "- Luke keeps final creative authority; agents prepare options and handoffs."
].join("\n");

const forms = {
  ingestion: {
    tab: "Ingestion",
    title: "007 song intelligence ingestion form",
    destination: "Save to ingestion/",
    prefix: "ingestion",
    fields: [
      field("status", "Status", "select", ["seed", "needs audio", "needs stems", "analysis draft", "ready for visual brief", "parked"]),
      field("ingestionTitle", "Ingestion title"),
      field("songTitle", "Song title"),
      field("songPage", "Existing song page URL or local path"),
      field("audioSource", "Audio source / master / reference", "textarea"),
      field("lyricsSource", "Lyrics source", "textarea"),
      field("lyricStatus", "Lyric status"),
      field("lyricsText", "Lyrics from song page", "textarea", null, "Auto-filled when the catalogue song page already has lyrics."),
      field("stemAccess", "Stem access", "textarea", null, "List the stems you can provide or need: vocal, drums, bass, keys, guitars, pads, FX, instrumental, acapella."),
      field("lyricalSummary", "Lyrical summary", "textarea", null, "What is the song saying, without rewriting it?"),
      field("emotionArc", "Emotion arc", "textarea", null, "Opening feeling, verse lift, chorus release, bridge/drop shift, ending state."),
      field("toneAndAudience", "Tone and audience posture", "textarea", null, "Gentle, celebratory, confrontational, sacred, comic, reflective, cinematic, local, cosmic, etc."),
      field("keywordsAndSymbols", "Keywords, symbols, and motifs", "textarea", null, "Tags, repeated images, named places, characters, mythic objects, slogans, lyric hooks."),
      field("bpm", "BPM / tempo"),
      field("keyPitch", "Key / pitch centre"),
      field("volumeDynamics", "Volume and dynamic shape", "textarea", null, "Quiet/loud sections, crescendos, drops, density, chorus lift, ending fade."),
      field("beatMap", "Beat and section map", "textarea", null, "Timecode each section: intro, verse, pre, chorus, bridge, drop, outro, hook, visual hit points."),
      field("vocalNotes", "Vocal, pitch, and performance notes", "textarea"),
      field("instrumentation", "Instrumentation and texture", "textarea"),
      field("videoTimingNotes", "Video timing notes", "textarea", null, "Cut density, motion intensity, camera tempo, stillness moments, lyric caption timing."),
      field("metadataTags", "Metadata tag bank", "textarea", null, "Mood, genre, scene, theme, colour, BPM, energy, audience, placement, accessibility tags."),
      field("targetQuery", "Targeted distribution query", "textarea", null, "Example: For this song profile, where should the completed content appear, for whom, on what screen, and with what level of interruption?"),
      field("nonIntrusiveDeployment", "Non-intrusive marketing deployment notes", "textarea", null, "Opt-in, context-aware, respectful frequency, audience benefit, caption/alt-text needs, platform boundaries."),
      field("accessibilityNotes", "Accessibility and caption notes", "textarea"),
      field("risksOrAvoid", "Risks / avoid", "textarea"),
      field("nextAction", "Next useful action", "textarea")
    ],
    render(data) {
      return doc([
        heading("007 Song Intelligence Ingestion", data.ingestionTitle || data.songTitle),
        meta(data),
        section("Core Boundaries", sharedBoundary),
        section("Existing Song Source", lines([
          line("Song title", data.songTitle),
          line("Song page", data.songPage),
          line("Audio source / master / reference", data.audioSource),
          line("Lyrics source", data.lyricsSource),
          line("Lyric status", data.lyricStatus)
        ])),
        section("Lyrics From Song Page", data.lyricsText),
        section("Stem Access", bulletise(data.stemAccess)),
        section("Lyrical Intelligence", lines([
          block("Lyrical summary", data.lyricalSummary),
          block("Emotion arc", data.emotionArc),
          block("Tone and audience posture", data.toneAndAudience),
          block("Keywords, symbols, and motifs", bulletise(data.keywordsAndSymbols))
        ])),
        section("Auditory Intelligence", lines([
          line("BPM / tempo", data.bpm),
          line("Key / pitch centre", data.keyPitch),
          block("Volume and dynamic shape", data.volumeDynamics),
          block("Beat and section map", data.beatMap),
          block("Vocal, pitch, and performance notes", data.vocalNotes),
          block("Instrumentation and texture", data.instrumentation)
        ])),
        section("Video Optimisation Notes", data.videoTimingNotes),
        section("Metadata Tag Bank", bulletise(data.metadataTags)),
        section("Targeted Distribution Query", data.targetQuery),
        section("Non-Intrusive Marketing Deployment", data.nonIntrusiveDeployment),
        section("Accessibility And Caption Notes", data.accessibilityNotes),
        listSection("Risks / Avoid", data.risksOrAvoid),
        section("Next Useful Action", data.nextAction)
      ]);
    }
  },
  songBrief: {
    tab: "Visual Brief",
    title: "Song-to-visual brief form",
    destination: "Save to visual-briefs/",
    prefix: "visual-brief",
    fields: [
      hiddenField("status", "Status", "select", ["seed", "draft", "ready for images", "ready for video", "parked"]),
      hiddenField("songTitle", "Song title"),
      hiddenField("songPage", "Existing song page URL or local path"),
      hiddenField("linkedIngestion", "Linked 007 ingestion profile"),
      field("albumWorld", "Album world or archive tray"),
      field("assetTypes", "Asset types to create", "textarea", null, "Examples: cover key art, storyboard stills, YouTube video, Shorts/Reels clip, Spotify canvas, thumbnail."),
      field("visualMoment", "Visual moment or lyric cue", "textarea", null, "Do not rewrite the song. Pick the moment the image or video should express."),
      field("visualIntent", "Visual intent", "textarea"),
      field("audioTimingNotes", "Audio timing notes from ingestion", "textarea", null, "BPM, section markers, emotional peaks, dynamic changes, hooks, stems, or beat cuts that should guide the visuals."),
      field("targetQuery", "Target query for later variants", "textarea", null, "Who is this for, where will it appear, what screen context matters, and what would feel non-intrusive?"),
      field("metadataSeeds", "Metadata seeds", "textarea", null, "Use the ingestion tag bank: mood, genre, energy, colours, symbols, accessibility labels, caption terms."),
      field("screenNotes", "Screen / format hypotheses", "textarea", null, "Early guesses only. Final targets should come from the variant query builder."),
      field("narrativeMode", "Visual mode", "select", ["illustrative", "amplifying", "conceptual / abstract", "contradictory", "performance / identity", "hybrid"]),
      field("visualWorld", "Visual world and style references", "textarea"),
      field("favouriteImageGen", "Favourite image generator"),
      field("favouriteVideoGen", "Favourite video generator"),
      field("mustKeep", "Must keep", "textarea"),
      field("avoid", "Avoid", "textarea"),
      field("nextAction", "Next useful action", "textarea")
    ],
    render(data) {
      return doc([
        heading("Infinity Engine Visual Brief", data.songTitle),
        meta(data),
        section("Core Boundaries", sharedBoundary),
        section("Existing Song Source", lines([
          line("Song page", data.songPage),
          line("Linked 007 ingestion profile", data.linkedIngestion),
          line("Album world", data.albumWorld),
          block("Visual moment or lyric cue", data.visualMoment)
        ])),
        section("Image And Video Direction", lines([
          block("Asset types to create", bulletise(data.assetTypes)),
          block("Visual intent", data.visualIntent),
          block("Audio timing notes from ingestion", data.audioTimingNotes),
          line("Visual mode", data.narrativeMode),
          block("Visual world", data.visualWorld)
        ])),
        section("Target Query And Metadata Seeds", lines([
          block("Target query for later variants", data.targetQuery),
          block("Metadata seeds", bulletise(data.metadataSeeds)),
          block("Screen / format hypotheses", data.screenNotes)
        ])),
        section("Generator Preferences", lines([
          line("Favourite image generator", data.favouriteImageGen),
          line("Favourite video generator", data.favouriteVideoGen)
        ])),
        listSection("Must Keep", data.mustKeep),
        listSection("Avoid", data.avoid),
        section("Next Useful Action", data.nextAction)
      ]);
    }
  },
  storyboard: {
    tab: "Storyboard",
    title: "Comic-as-storyboard form",
    destination: "Save to storyboards/",
    prefix: "storyboard",
    fields: [
      hiddenField("status", "Status", "select", ["seed", "draft", "ready for images", "approved panels", "parked"]),
      hiddenField("songTitle", "Song title"),
      field("sceneTitle", "Scene or sequence title"),
      field("panelCount", "Panel count"),
      field("panelBeats", "Panel beats", "textarea", null, "One panel per line works well."),
      field("characterRefs", "Character / subject references", "textarea"),
      field("settingRefs", "Setting references", "textarea"),
      field("artStyle", "Art style and palette", "textarea"),
      field("imagePromptFormula", "Image prompt formula", "textarea", null, "Subject, setting, style, lighting, camera, palette, details, emotion, quality."),
      field("favouriteImageGen", "Favourite image generator"),
      field("approvalNotes", "Approval notes", "textarea"),
      field("nextAction", "Next useful action", "textarea")
    ],
    render(data) {
      return doc([
        heading("Comic-as-Storyboard", data.sceneTitle || data.songTitle),
        meta(data),
        section("Source Song", data.songTitle),
        section("Core Boundaries", sharedBoundary),
        section("Storyboard Shape", lines([
          line("Panel count", data.panelCount),
          block("Panel beats", bulletise(data.panelBeats)),
          block("Character / subject references", data.characterRefs),
          block("Setting references", data.settingRefs),
          block("Art style and palette", data.artStyle)
        ])),
        section("Image Generation Prompt Stack", lines([
          block("Formula", data.imagePromptFormula),
          line("Favourite image generator", data.favouriteImageGen)
        ])),
        section("Human Approval Notes", data.approvalNotes),
        section("Next Useful Action", data.nextAction)
      ]);
    }
  },
  shot: {
    tab: "Keyframe Shot",
    title: "Keyframe-to-video shot form",
    destination: "Save to shots/",
    prefix: "shot",
    fields: [
      hiddenField("status", "Status", "select", ["seed", "draft", "ready to generate", "needs regen", "approved"]),
      field("shotTitle", "Shot title"),
      hiddenField("linkedSong", "Linked song"),
      hiddenField("linkedIngestion", "Linked 007 ingestion profile"),
      field("linkedStoryboard", "Linked storyboard or panel range"),
      field("duration", "Duration"),
      field("ingestionTimingProfile", "Ingestion timing profile", "textarea", null, "Auto-carries BPM, key/pitch centre, dynamics, beat map, stem access, and video timing notes from 007 where available."),
      field("shotOrganisation", "Shot organisation / timing riff", "textarea", null, "Use this to reason from the song profile: where the shot starts, what changes in the middle, and where it should land."),
      field("firstKeyframeMoment", "First keyframe choice", "textarea", null, "Choose the visual state just before movement matters: before a lyric turn, beat lift, emotional reveal, or camera move."),
      field("inbetweenBeats", "In-between beats / motion checkpoints", "textarea", null, "List timing beats between first and last frame: lyric hits, camera accents, gesture changes, lighting shifts, or cuts."),
      field("lastKeyframeMoment", "Last keyframe choice", "textarea", null, "Choose the landing state after the musical or emotional change: resolved pose, revealed symbol, chorus lift, drop, or transition point."),
      field("startFramePrompt", "Start frame prompt", "textarea"),
      field("endFramePrompt", "End frame prompt", "textarea"),
      field("cameraMotion", "Camera motion", "textarea", null, "Example: slow dolly in, pan left, parallax drift, locked-off close-up."),
      field("videoPrompt", "Video generator prompt", "textarea"),
      field("lipSyncStrategy", "Lip-sync strategy", "select", ["creative avoidance", "local / low-cost", "native / premium", "manual edit", "not needed"]),
      field("audioCue", "Audio cue or lyric timing", "textarea"),
      field("favouriteVideoGen", "Favourite video generator"),
      field("editNotes", "Edit / assembly notes", "textarea"),
      field("nextAction", "Next useful action", "textarea")
    ],
    render(data) {
      return doc([
        heading("Keyframe-to-Video Shot", data.shotTitle),
        meta(data),
        section("Links", lines([
          line("Linked song", data.linkedSong),
          line("Linked 007 ingestion profile", data.linkedIngestion),
          line("Linked storyboard or panel range", data.linkedStoryboard),
          line("Duration", data.duration)
        ])),
        section("Core Boundaries", sharedBoundary),
        section("Ingestion Timing Profile", data.ingestionTimingProfile),
        section("Shot Organisation", lines([
          block("Shot organisation / timing riff", data.shotOrganisation),
          block("First keyframe choice", data.firstKeyframeMoment),
          block("In-between beats / motion checkpoints", bulletise(data.inbetweenBeats)),
          block("Last keyframe choice", data.lastKeyframeMoment)
        ])),
        section("Frame Pair", lines([
          block("Start frame prompt", data.startFramePrompt),
          block("End frame prompt", data.endFramePrompt)
        ])),
        section("Motion And Audio", lines([
          block("Camera motion", data.cameraMotion),
          block("Video generator prompt", data.videoPrompt),
          line("Lip-sync strategy", data.lipSyncStrategy),
          block("Audio cue or lyric timing", data.audioCue),
          line("Favourite video generator", data.favouriteVideoGen)
        ])),
        section("Edit / Assembly Notes", data.editNotes),
        section("Next Useful Action", data.nextAction)
      ]);
    }
  },
  variant: {
    tab: "Distribution Fit",
    title: "Distribution fit planner",
    destination: "Save to variants/",
    prefix: "variant",
    fields: [
      hiddenField("status", "Status", "select", ["seed", "draft", "ready to export", "exported", "parked"]),
      hiddenField("variantTitle", "Plan title"),
      hiddenField("linkedSong", "Linked song page"),
      hiddenField("linkedIngestion", "Linked 007 ingestion profile"),
      field("sourceAsset", "Source image / video / edit"),
      field("assetKind", "Asset kind", "select", ["image", "video", "thumbnail", "canvas loop", "storyboard still", "projection / screen", "mixed"]),
      field("targetQuery", "Placement question", "textarea", null, "Ask one useful question: where should this completed image or video appear, for whom, on what screen, and what would feel respectful rather than spammy?"),
      field("audienceMoment", "Audience moment", "textarea", null, "Who is seeing it, what are they doing, and what would make the asset welcome?"),
      field("recommendedPlacements", "Best-fit outputs and reasons", "textarea", null, "One per line: platform or screen, why it fits the song profile, and what must change for that version."),
      field("nonIntrusiveRules", "Respect rules", "textarea", null, "Frequency, opt-in context, caption tone, audience value, avoidances, and platform comfort boundaries."),
      field("aspectRatio", "Primary aspect ratio"),
      field("duration", "Primary duration"),
      field("resolution", "Export settings"),
      field("safeArea", "Safe area and text notes", "textarea"),
      field("captionCopy", "Caption / title / alt text", "textarea"),
      field("metadataPackage", "Metadata package", "textarea", null, "Tags, hashtags, mood labels, energy, accessibility labels, thumbnail terms, searchable phrases."),
      field("reusePlan", "Reuse plan", "textarea", null, "How this asset can become other platform versions."),
      field("generatorNotes", "Generator / editor notes", "textarea"),
      field("nextAction", "Next useful action", "textarea")
    ],
    render(data) {
      return doc([
        heading("Distribution Fit Plan", data.variantTitle),
        meta(data),
        section("Existing Source", lines([
          line("Linked song page", data.linkedSong),
          line("Linked 007 ingestion profile", data.linkedIngestion),
          line("Source image / video / edit", data.sourceAsset),
          line("Asset kind", data.assetKind)
        ])),
        section("Placement Question", lines([
          block("Question", data.targetQuery),
          block("Audience moment", data.audienceMoment),
          block("Best-fit outputs and reasons", bulletise(data.recommendedPlacements)),
          block("Respect rules", data.nonIntrusiveRules)
        ])),
        section("Screen And Export", lines([
          line("Primary aspect ratio", data.aspectRatio),
          line("Primary duration", data.duration),
          line("Export settings", data.resolution),
          block("Safe area and text notes", data.safeArea)
        ])),
        section("Publishing Copy", data.captionCopy),
        section("Metadata Package", bulletise(data.metadataPackage)),
        section("Reuse Plan", data.reusePlan),
        section("Generator / Editor Notes", data.generatorNotes),
        section("Next Useful Action", data.nextAction)
      ]);
    }
  },
  review: {
    tab: "Review",
    title: "First cut review form",
    destination: "Save to reviews/",
    prefix: "review",
    fields: [
      hiddenField("status", "Status", "select", ["rough cut", "revision pass", "approved", "parked"]),
      hiddenField("cutTitle", "Cut title"),
      hiddenField("linkedSong", "Linked song page"),
      field("clipList", "Clip list or timeline notes", "textarea"),
      field("keepMoments", "Keep these moments", "textarea"),
      field("reviseClips", "Regenerate or revise", "textarea"),
      field("manualEditNotes", "Manual edit notes", "textarea"),
      field("publishFormat", "Publish format", "textarea", null, "Example: YouTube landscape, 9:16 short, Spotify canvas, teaser reel."),
      field("feedbackSignals", "Audience / data signals to watch", "textarea"),
      field("nextAction", "Next useful action", "textarea")
    ],
    render(data) {
      return doc([
        heading("First Cut Review", data.cutTitle),
        meta(data),
        section("Linked Song", data.linkedSong),
        section("Core Boundaries", sharedBoundary),
        section("Timeline Notes", data.clipList),
        listSection("Keep These Moments", data.keepMoments),
        listSection("Regenerate Or Revise", data.reviseClips),
        section("Manual Edit Notes", data.manualEditNotes),
        section("Publish Format", data.publishFormat),
        section("Audience / Data Signals To Watch", data.feedbackSignals),
        section("Next Useful Action", data.nextAction)
      ]);
    }
  },
  handoff: {
    tab: "Handoff",
    title: "Agent handoff form",
    destination: "Save to handoffs/",
    prefix: "handoff",
    fields: [
      hiddenField("status", "Status", "select", ["seed", "ready", "done", "parked"]),
      hiddenField("handoffTitle", "Handoff title"),
      field("task", "Exact task", "textarea"),
      hiddenField("linkedSong", "Linked song / album / folder"),
      field("workFrom", "Work from", "textarea"),
      field("allowedSources", "Allowed sources", "textarea"),
      field("doNotTouch", "Do not touch", "textarea"),
      field("generatorLane", "Generator lane", "select", ["text / analysis", "image", "video", "editing", "publishing"]),
      field("expectedOutput", "Expected output", "textarea"),
      field("nextAction", "Next useful action", "textarea")
    ],
    render(data) {
      return doc([
        heading("Infinity Engine Handoff", data.handoffTitle),
        meta(data),
        section("Task", data.task),
        section("Context", lines([
          line("Linked song / album / folder", data.linkedSong),
          line("Generator lane", data.generatorLane),
          block("Work from", data.workFrom)
        ])),
        listSection("Allowed Sources", data.allowedSources),
        listSection("Do Not Touch", data.doNotTouch),
        section("Expected Output", data.expectedOutput),
        section("Next Useful Action", data.nextAction)
      ]);
    }
  }
};

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-reset-all-forms]").forEach((button) => {
    button.addEventListener("click", resetAllBuilderForms);
  });

  const app = document.querySelector("[data-infinity-builder]");
  if (!app) return;

  const formElement = document.getElementById("builderForm");
  const preview = document.getElementById("markdownPreview");
  const filenameElement = document.getElementById("filename");
  const formType = document.getElementById("formType");
  const formTitle = document.getElementById("formTitle");
  const destination = document.getElementById("destination");
  const builderContext = document.getElementById("builderContext");
  const statusLine = document.getElementById("statusLine");
  const sideNav = document.querySelector(".studio-side-nav");
  const songCatalogue = readStudioSongData();

  let activeForm = app.dataset.activeBuilder || "songBrief";
  let savedState = loadState();

  syncContextFromCatalogue();
  renderSideNav();
  renderActiveForm();

  document.getElementById("downloadButton")?.addEventListener("click", downloadMarkdown);
  document.getElementById("copyButton")?.addEventListener("click", copyMarkdown);
  document.getElementById("clearButton")?.addEventListener("click", clearActiveForm);

  function renderSideNav() {
    if (!sideNav) return;
    sideNav.innerHTML = '<p class="studio-kicker">Builder lanes</p>';
    studioPages.forEach((item) => {
      const link = document.createElement("a");
      link.href = item.href;
      link.className = item.key === activeForm ? "active" : "";
      link.innerHTML = `<span>${item.number}</span><strong>${item.label}</strong><em>${item.note}</em>`;
      sideNav.appendChild(link);
    });
  }

  function renderActiveForm() {
    const config = forms[activeForm];
    syncContextFromCatalogue();
    const data = getFormState(activeForm);
    seedFormFromContext(activeForm, data);
    applySelectDefaults(config, data);
    refreshDerivedContext(activeForm, data);
    savedState.forms[activeForm] = data;
    persistState();
    formType.textContent = config.tab;
    formTitle.textContent = config.title;
    destination.textContent = config.destination;
    renderContextStrip(data);
    formElement.innerHTML = "";

    config.fields.filter((item) => !item.hidden).forEach((item) => {
      const wrapper = document.createElement("div");
      wrapper.className = "studio-field";

      const label = document.createElement("label");
      label.htmlFor = item.id;
      label.textContent = item.label;
      wrapper.appendChild(label);

      const input = createInput(item, data[item.id] || "");
      input.addEventListener("input", () => updateField(item.id, input.value));
      input.addEventListener("change", () => updateField(item.id, input.value));
      wrapper.appendChild(input);

      if (item.hint) {
        const hint = document.createElement("p");
        hint.className = "studio-hint";
        hint.textContent = item.hint;
        wrapper.appendChild(hint);
      }

      formElement.appendChild(wrapper);
    });

    updatePreview();
  }

  function renderContextStrip(data) {
    if (!builderContext) return;
    builderContext.innerHTML = "";
    if (activeForm === "ingestion") {
      builderContext.hidden = true;
      return;
    }

    const song = clean(savedState.context?.songTitle) || clean(data.songTitle) || clean(data.linkedSong) || clean(savedState.context?.songPage);
    const profile = clean(data.linkedIngestion) || clean(savedState.context?.linkedIngestion);

    const items = [
      ["Song", song],
      ["007", profile]
    ].filter((item) => clean(item[1]));

    if (!items.length) {
      builderContext.hidden = true;
      return;
    }

    items.forEach(([label, value]) => {
      const chip = document.createElement("span");
      chip.className = "studio-context-chip";
      const strong = document.createElement("strong");
      strong.textContent = label;
      const text = document.createElement("em");
      text.textContent = value;
      chip.append(strong, text);
      builderContext.appendChild(chip);
    });
    builderContext.hidden = false;
  }

  function createInput(item, value) {
    if (item.type === "textarea") {
      const textarea = document.createElement("textarea");
      textarea.id = item.id;
      textarea.value = value;
      return textarea;
    }

    if (item.type === "select") {
      const select = document.createElement("select");
      select.id = item.id;
      item.options.forEach((option) => {
        const node = document.createElement("option");
        node.value = option;
        node.textContent = option;
        select.appendChild(node);
      });
      select.value = value || item.options[0];
      return select;
    }

    const input = document.createElement("input");
    input.id = item.id;
    input.type = "text";
    input.value = value;
    return input;
  }

  function updateField(id, value, shouldRender = true) {
    const data = getFormState(activeForm);
    deleteCarriedValue(activeForm, id);
    data[id] = value;
    savedState.forms[activeForm] = data;
    updateSharedContext(id, value);
    refreshDerivedContext(activeForm, data);
    persistState();
    if (shouldRender) updatePreview();
  }

  function updatePreview() {
    const data = getFormState(activeForm);
    refreshDerivedContext(activeForm, data);
    preview.value = forms[activeForm].render(data);
    filenameElement.textContent = filenameFor(activeForm, data);
    statusLine.textContent = "Autosaved in this browser.";
    persistState();
  }

  function downloadMarkdown() {
    const blob = new Blob([preview.value], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filenameElement.textContent;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    statusLine.textContent = "Markdown download started.";
  }

  async function copyMarkdown() {
    await navigator.clipboard.writeText(preview.value);
    statusLine.textContent = "Markdown copied.";
  }

  function clearActiveForm() {
    savedState.forms[activeForm] = {};
    savedState.carried[activeForm] = {};
    if (activeForm === "ingestion") {
      savedState.context = {};
      savedState.carried = {};
    }
    persistState();
    renderActiveForm();
    statusLine.textContent = "Form reset.";
  }

  function seedFormFromContext(formKey, data) {
    const carried = getCarriedState(formKey);
    forms[formKey].fields.forEach((item) => {
      const nextValue = sharedValueForField(item.id);
      if (!clean(nextValue)) return;

      const currentValue = clean(data[item.id]);
      const wasCarried = carried[item.id] && carried[item.id] === currentValue;
      if (item.hidden || !currentValue || wasCarried) {
        data[item.id] = nextValue;
        carried[item.id] = nextValue;
      }
    });
    if (formKey === "ingestion") applyCatalogueToIngestion(data, carried);
  }

  function applyCatalogueToIngestion(data, carried) {
    const sourceFields = ["songTitle", "songPage", "audioSource", "lyricsSource", "lyricStatus", "lyricsText"];
    sourceFields.forEach((id) => {
      const nextValue = sharedValueForField(id);
      if (!clean(nextValue)) return;
      data[id] = nextValue;
      carried[id] = nextValue;
    });

    if (!clean(data.ingestionTitle) || !clean(data.ingestionTitle).toLowerCase().includes(clean(data.songTitle).toLowerCase())) {
      data.ingestionTitle = titleFromSong("song intelligence ingestion");
      carried.ingestionTitle = data.ingestionTitle;
    }
    if (!clean(data.lyricalSummary) && clean(savedState.context?.lyricalSummary)) {
      data.lyricalSummary = savedState.context.lyricalSummary;
      carried.lyricalSummary = data.lyricalSummary;
    }
    if (!clean(data.metadataTags) && clean(savedState.context?.metadataTags)) {
      data.metadataTags = savedState.context.metadataTags;
      carried.metadataTags = data.metadataTags;
    }
  }

  function applySelectDefaults(config, data) {
    config.fields.forEach((item) => {
      if (item.type === "select" && !clean(data[item.id])) {
        data[item.id] = item.options[0];
      }
    });
  }

  function updateSharedContext(id, value) {
    const contextKey = contextFieldKeys[id];
    if (!contextKey) return;
    if (clean(value)) {
      savedState.context[contextKey] = value;
    } else {
      delete savedState.context[contextKey];
    }
  }

  function refreshDerivedContext(formKey, data) {
    if (formKey === "ingestion" && (clean(data.ingestionTitle) || clean(data.songTitle))) {
      savedState.context.linkedIngestion = filenameFor("ingestion", data);
    }
    if (formKey === "ingestion") {
      const audioTiming = audioTimingFromIngestion(data);
      if (audioTiming) savedState.context.audioTimingNotes = audioTiming;
    }
  }

  function syncContextFromCatalogue() {
    const song = selectedCatalogueSong();
    if (!song) return;

    savedState.context.songTitle = song.title || savedState.context.songTitle || "";
    savedState.context.songPage = song.songPage || savedState.context.songPage || "";
    savedState.context.albumWorld ||= song.album || "";
    savedState.context.audioSource = sourceSummary(song);
    savedState.context.lyricsSource = lyricsSourceSummary(song);
    savedState.context.lyricsText = song.lyrics || "";
    savedState.context.lyricStatus = song.lyricStatus || (song.hasLyrics ? "Lyrics imported on the song page." : "Lyrics not imported yet.");
    if (!clean(savedState.context.lyricalSummary) && clean(song.meaning)) savedState.context.lyricalSummary = song.meaning;
    if (!clean(savedState.context.metadataTags)) savedState.context.metadataTags = [song.album, ...(song.themes || [])].filter(Boolean).join("\n");
  }

  function selectedCatalogueSong() {
    if (!songCatalogue.length) return null;
    const context = savedState.context || {};
    const current = savedState.forms?.[activeForm] || {};
    const ingestion = savedState.forms?.ingestion || {};
    const humanState = readHumanState();
    const candidates = [
      humanState.selectedSlug,
      current.linkedIngestion,
      current.songPage,
      current.linkedSong,
      current.songTitle,
      context.linkedIngestion,
      ingestion.linkedIngestion,
      context.songPage,
      ingestion.songPage,
      context.songTitle,
      ingestion.songTitle
    ].map(clean).filter(Boolean);

    for (const candidate of candidates) {
      const matched = matchCatalogueSong(candidate);
      if (matched) return matched;
    }
    return null;
  }

  function matchCatalogueSong(value) {
    const normal = normaliseSongKey(value);
    return songCatalogue.find((song) => (
      normaliseSongKey(song.songPage) === normal ||
      normaliseSongKey(song.title) === normal ||
      normaliseSongKey(song.slug) === normal ||
      normal.includes(normaliseSongKey(song.slug))
    ));
  }

  function normaliseSongKey(value) {
    return clean(value)
      .toLowerCase()
      .replace(/^https?:\/\/[^/]+/i, "")
      .replace(/^file:\/\/\/?[a-z]:/i, "")
      .replace(/\\/g, "/")
      .replace(/\/index\.html$/, "/")
      .replace(/^(\.\.\/|\.\/)+/, "")
      .replace(/^songs\//, "")
      .replace(/\/$/, "");
  }

  function sourceSummary(song) {
    return compactLines([
      line("Song page", song.songPage),
      line("YouTube", song.youtubeUrl),
      line("Spotify", song.spotifyUrl),
      line("Apple", song.appleUrl)
    ]);
  }

  function lyricsSourceSummary(song) {
    if (song.hasLyrics) {
      return compactLines([
        song.lyricStatus || "Lyrics imported on the song page.",
        line("Song page", song.songPage)
      ]);
    }
    return song.lyricStatus || "Lyrics not imported yet.";
  }

  function readHumanState() {
    try {
      return JSON.parse(localStorage.getItem(HUMAN_STORE_KEY)) || {};
    } catch (error) {
      return {};
    }
  }

  function sharedValueForField(id) {
    const context = savedState.context || {};
    const directKey = contextFieldKeys[id];
    if (directKey && clean(context[directKey])) return context[directKey];

    if (id === "ingestionTitle") return titleFromSong("song intelligence ingestion");
    if (id === "sceneTitle") return titleFromSong("storyboard");
    if (id === "shotTitle") return titleFromSong("keyframe shot");
    if (id === "variantTitle") return titleFromSong("distribution fit");
    if (id === "cutTitle") return titleFromSong("first cut review");
    if (id === "handoffTitle") return titleFromSong("production handoff");
    if (id === "linkedStoryboard") return titleFromSong("storyboard");
    if (id === "linkedSong") return context.songPage || context.songTitle || "";
    if (id === "shotOrganisation") return keyframeTimingRiffFromContext(context);
    if (id === "firstKeyframeMoment") return firstKeyframeHintFromContext(context);
    if (id === "inbetweenBeats") return inbetweenBeatsFromContext(context);
    if (id === "lastKeyframeMoment") return lastKeyframeHintFromContext(context);
    return "";
  }

  function titleFromSong(suffix) {
    const title = clean(savedState.context?.songTitle);
    return title ? `${title} ${suffix}` : "";
  }

  function audioTimingFromIngestion(data) {
    return compactLines([
      line("BPM / tempo", data.bpm),
      line("Key / pitch centre", data.keyPitch),
      block("Volume and dynamic shape", data.volumeDynamics),
      block("Beat and section map", data.beatMap),
      block("Video timing notes", data.videoTimingNotes),
      block("Stem access", bulletise(data.stemAccess))
    ]);
  }

  function keyframeTimingRiffFromContext(context) {
    if (!hasTimingContext(context)) return "";
    return compactLines([
      "Use the first keyframe as the still visual state before the most useful musical or emotional change.",
      "Use in-between beats to organise motion, camera accents, lyric hits, lighting shifts, or subject gestures between the endpoints.",
      "Use the last keyframe as the landing state after the change has visibly happened.",
      block("Available timing data", context.audioTimingNotes || context.beatMap || context.videoTimingNotes),
      block("Emotional / tone clue", compactLines([context.emotionArc, context.toneAndAudience])),
      block("Metadata clue", bulletise(context.metadataTags))
    ]);
  }

  function firstKeyframeHintFromContext(context) {
    if (!hasTimingContext(context)) return "";
    return compactLines([
      "Pick a frame just before a section change, lyric turn, beat lift, dynamic rise, or emotional reveal.",
      block("Use these clues", compactLines([context.beatMap, context.volumeDynamics, context.videoTimingNotes, context.emotionArc]))
    ]);
  }

  function inbetweenBeatsFromContext(context) {
    if (!hasTimingContext(context)) return "";
    return compactLines([
      context.beatMap,
      context.videoTimingNotes,
      "Add 2 to 5 checkpoints between the first and last keyframes: camera move, gesture, lighting, symbol reveal, lyric caption, edit accent."
    ]);
  }

  function lastKeyframeHintFromContext(context) {
    if (!hasTimingContext(context)) return "";
    return compactLines([
      "Pick the landing frame after the musical or emotional change has resolved enough for the viewer to feel the point.",
      block("Use these clues", compactLines([context.beatMap, context.volumeDynamics, context.videoTimingNotes, context.emotionArc]))
    ]);
  }

  function hasTimingContext(context) {
    return Boolean(clean(context.audioTimingNotes) || clean(context.beatMap) || clean(context.videoTimingNotes) || clean(context.emotionArc));
  }

  function compactLines(values) {
    return values.filter((value) => clean(value)).join("\n\n");
  }

  function getCarriedState(key) {
    if (!savedState.carried[key]) savedState.carried[key] = {};
    return savedState.carried[key];
  }

  function deleteCarriedValue(formKey, id) {
    const carried = getCarriedState(formKey);
    delete carried[id];
  }

  function getFormState(key) {
    if (!savedState.forms[key]) savedState.forms[key] = {};
    return savedState.forms[key];
  }

  function loadState() {
    try {
      const parsed = JSON.parse(localStorage.getItem(INFINITY_STORE_KEY));
      if (parsed && parsed.forms) {
        return {
          forms: parsed.forms || {},
          context: parsed.context || {},
          carried: parsed.carried || {}
        };
      }
    } catch (error) {
      console.warn("Could not load Infinity Engine builder state", error);
    }
    return { forms: {}, context: {}, carried: {} };
  }

  function persistState() {
    localStorage.setItem(INFINITY_STORE_KEY, JSON.stringify(savedState));
  }
});

function page(key, number, label, href, note) {
  return { key, number, label, href, note };
}

function field(id, label, type = "text", options = null, hint = "", flags = {}) {
  return { id, label, type, options, hint, ...flags };
}

function hiddenField(id, label, type = "text", options = null, hint = "") {
  return field(id, label, type, options, hint, { hidden: true });
}

function readStudioSongData() {
  const node = document.getElementById("studioSongData");
  if (!node) return [];
  try {
    return JSON.parse(node.textContent || "[]");
  } catch (error) {
    console.warn("Could not read Studio song data", error);
    return [];
  }
}

function resetAllBuilderForms() {
  const ok = window.confirm("Reset all Infinity Engine forms and human listening cues in this browser?");
  if (!ok) return;
  localStorage.removeItem(INFINITY_STORE_KEY);
  localStorage.removeItem(HUMAN_STORE_KEY);
  window.location.reload();
}

function doc(parts) {
  return parts.filter(Boolean).join("\n\n").trim() + "\n";
}

function heading(type, title) {
  return `# ${type}${clean(title) ? ` - ${clean(title)}` : ""}`;
}

function meta(data) {
  return [
    line("Status", data.status || "seed"),
    line("Generated", new Date().toISOString().slice(0, 10)),
    "Generated by the i C. infinity Infinity Engine Studio."
  ].join("\n");
}

function section(title, value) {
  if (!clean(value)) return "";
  return `## ${title}\n\n${clean(value)}`;
}

function listSection(title, value) {
  const list = bulletise(value);
  if (!list) return "";
  return `## ${title}\n\n${list}`;
}

function bulletise(value) {
  const items = clean(value)
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean);
  if (!items.length) return "";
  return items.map((item) => `- ${item.replace(/^-+\s*/, "")}`).join("\n");
}

function line(label, value) {
  if (!clean(value)) return "";
  return `${label}: ${clean(value)}`;
}

function block(label, value) {
  if (!clean(value)) return "";
  return `${label}:\n\n${clean(value)}`;
}

function lines(values) {
  return values.filter(Boolean).join("\n\n");
}

function clean(value) {
  return String(value || "").trim();
}

function filenameFor(key, data) {
  const config = forms[key];
  const title =
    data.ingestionTitle ||
    data.songTitle ||
    data.sceneTitle ||
    data.shotTitle ||
    data.cueTitle ||
    data.variantTitle ||
    data.cutTitle ||
    data.handoffTitle ||
    "draft";
  const date = new Date().toISOString().slice(0, 10);
  return `${config.prefix}-${date}-${slugify(title)}.md`;
}

function slugify(value) {
  const slug = clean(value)
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug || "draft";
}
