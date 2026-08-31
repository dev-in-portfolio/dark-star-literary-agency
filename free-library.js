(() => {
  "use strict";

  const PAGE_SIZE = 18;
  const grid = document.getElementById("free-library-grid");
  const count = document.getElementById("free-result-count");
  const context = document.getElementById("free-result-context");
  const stats = document.getElementById("free-library-stats");
  const search = document.getElementById("free-search");
  const collection = document.getElementById("free-collection");
  const kind = document.getElementById("free-kind");
  const reset = document.getElementById("free-reset");
  const loadMore = document.getElementById("free-load-more");
  const shelfTabs = [...document.querySelectorAll(".free-shelf-tab")];

  let manifest = null;
  let activeShelf = "";
  let visibleCount = PAGE_SIZE;

  const originalTitles = {
    1: "Lulu & Ellie and the Secret of Blackwater Bay",
    2: "Lulu & Ellie and the Lost Valley of Thunder",
    3: "Lulu & Ellie and the Clockwork Forest",
    4: "Lulu & Ellie and the Moonlit Circus",
    5: "Lulu & Ellie and the Snow Dragon's Bell",
    6: "Lulu & Ellie and the Mushroom Moon Maze",
    7: "Lulu & Ellie and the Lanterns of the Deep",
    8: "Lulu & Ellie and the Book That Lost Its Ending",
    9: "Lulu & Ellie and the Island That Drifted Away",
    10: "Lulu & Ellie and the Star Map of Everywhere",
    11: "Lulu & Ellie and the Lanterns of Firefly Hollow",
    12: "Lulu & Ellie and the Acorn Crown",
    13: "Lulu & Ellie and the Red Kite in the Impossible Wind",
    14: "Lulu & Ellie and the Silver Door Garden",
    15: "Lulu & Ellie and the Moon That Forgot to Laugh",
    16: "Lulu & Ellie and the Emberleaf Kingdom",
    17: "Lulu & Ellie and the Waterfall That Climbed the Stars",
    18: "Lulu & Ellie and the Crystal Pawprint",
    19: "Lulu & Ellie and the Feather of Two Shadows",
    20: "Lulu & Ellie and the Keeper Ring"
  };

  const formatLabel = (kind) => ({
    document: "PDF",
    audio: "AUDIO",
    video: "VIDEO",
    image: "ART"
  }[kind] || String(kind || "").toUpperCase());

  const actionLabel = (kind) => ({
    document: "Read",
    audio: "Listen",
    video: "Watch",
    image: "View"
  }[kind] || "View");

  const viewerHref = (asset) => "free-viewer.html?asset=" + encodeURIComponent(asset.key);

  function words(value) {
    return String(value || "")
      .replace(/\.[^.]+$/, "")
      .replace(/\(1\)$/i, " alternate")
      .replace(/[_-]+/g, " ")
      .replace(/([a-z])([A-Z])/g, "$1 $2")
      .replace(/([A-Za-z])(\d)/g, "$1 $2")
      .replace(/(\d)([A-Za-z])/g, "$1 $2")
      .replace(/\b(final|optimized|interior|full|repaired|v\d+)\b/gi, "")
      .replace(/\bm\d+\b/gi, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function titleCase(value) {
    const small = new Set(["and", "of", "the", "in", "to", "that", "with", "on", "a"]);
    return words(value).split(" ").map((part, index) => {
      if (!part) return part;
      const lower = part.toLowerCase();
      if (index > 0 && small.has(lower)) return lower;
      if (/^lulu$/i.test(part)) return "Lulu";
      if (/^ellie$/i.test(part)) return "Ellie";
      return part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
    }).join(" ");
  }

  function bookNumber(asset) {
    const source = asset.path || asset.filename || "";
    const patterns = [
      /Book[_ ]?(\d{1,2})/i,
      /Book(\d{1,2})/i,
      /Club[_ ]?(\d{1,2})/i,
      /Time[_ ]?(\d{1,2})/i,
      /Adventure[_ ]?Log[_ ]?(\d{1,2})/i,
      /Adventurelog[_ ]?(\d{1,2})/i,
      /Academy[_ ]?(\d{1,2})/i,
      /Acadamy[_ ]?(\d{1,2})/i,
      /Learning[_ ]?(\d{1,2})/i,
      /Phonics[_ ]?(\d{1,2})/i,
      /Handwriting[_ ]?(\d{1,2})/i,
      /Cursive[_ ]?(\d{1,2})/i,
      /Diary[_ ]?(\d{1,2})/i,
      /FieldGuide[_ ]?(\d{1,2})/i,
      /Fieldguide[_ ]?(\d{1,2})/i,
      /Puzzle[_ ]?(\d{1,2})/i,
      /Keepsake[_ ]?(\d{1,2})/i,
      /Search and find[_ ]?(\d{1,2})/i,
      /Cook[_ ]?(\d{1,2})/i,
      /Bedtime[_ ]?(\d{1,2})/i
    ];
    for (const pattern of patterns) {
      const match = source.match(pattern);
      if (match) return Number(match[1]);
    }
    return null;
  }

  function namedTitleFromFilename(asset) {
    let stem = words(asset.filename);
    stem = stem
      .replace(/^Lulu\s*&?\s*Ellie\s*/i, "")
      .replace(/^Lulu\s+and\s+Ellie\s*/i, "")
      .replace(/^Creature Rescue Club\s*/i, "")
      .replace(/^CRC\s*/i, "")
      .replace(/^Mystery Tails\s*/i, "")
      .replace(/^Time Tails\s*/i, "")
      .replace(/^Go To Camp\s*/i, "")
      .replace(/^Book\s*\d+\s*/i, "")
      .replace(/^\d+\s*/i, "")
      .replace(/^The\s+Case\s+of\s+/i, "The Case of ")
      .trim();
    return titleCase(stem);
  }

  function displayTitle(asset) {
    const n = bookNumber(asset);
    const path = asset.path || "";

    if (asset.collection === "Original Adventure — Full Books" && n && originalTitles[n]) {
      return originalTitles[n];
    }

    if (asset.collection === "Original Adventure — Media") {
      const folderMatch = path.match(/Book_(\d{1,2})/i);
      const number = folderMatch ? Number(folderMatch[1]) : n;
      const base = originalTitles[number] || ("Original Adventure · Book " + number);
      if (/front_cover/i.test(path)) return base + " · Cover";
      if (/fun_book/i.test(path)) return base + " · Feature Art";
      if (/\.mp4$/i.test(path)) return base + " · Animated Cover";
      return base;
    }

    if (asset.collection === "General Lulu & Ellie Media") {
      return "Lulu & Ellie · Short Video";
    }

    if (asset.collection === "Lulu & Ellie in Space") {
      if (/coloring/i.test(path)) return "Lulu & Ellie in Space · Coloring Adventure";
      return n ? "Lulu & Ellie in Space · Book " + n : titleCase(asset.title);
    }

    if (asset.collection === "Creature Rescue Club") {
      const named = namedTitleFromFilename(asset);
      if (/^Club\s*\d+/i.test(words(asset.filename)) || /^Book\s*\d*$/i.test(named)) {
        return n ? "Creature Rescue Club · Book " + n : "Creature Rescue Club";
      }
      return named && !/^Club$/i.test(named)
        ? named + (n ? " · Book " + n : "")
        : "Creature Rescue Club" + (n ? " · Book " + n : "");
    }

    if (asset.collection === "Mystery Tails") {
      const named = namedTitleFromFilename(asset);
      return named && !/^Book\s*\d+/i.test(named)
        ? named + (n ? " · Book " + n : "")
        : "Mystery Tails" + (n ? " · Book " + n : "");
    }

    if (asset.collection === "Time Tails") {
      const named = namedTitleFromFilename(asset);
      return named && !/^Time\s*\d+/i.test(named)
        ? named + (n ? " · Book " + n : "")
        : "Time Tails" + (n ? " · Book " + n : "");
    }

    if (asset.collection === "Go To Camp") {
      const named = namedTitleFromFilename(asset);
      if (named && !/^Book\s*\d+/i.test(named) && !/^Go to Camp/i.test(named)) {
        return named + (n ? " · Book " + n : "");
      }
      return "Lulu & Ellie Go To Camp" + (n ? " · Book " + n : "");
    }

    if (asset.collection === "Backyard Academy") return "Backyard Academy" + (n ? " · Book " + n : "");
    if (asset.collection === "Phonics") return "Phonics Path" + (n ? " · Book " + n : "");
    if (asset.collection === "Handwriting") return "Write & Wag" + (n ? " · Book " + n : "");
    if (asset.collection === "Cursive") return "Cursive Club" + (n ? " · Book " + n : "");
    if (asset.collection === "Learning") return "Learning Club" + (n ? " · Book " + n : "");
    if (asset.collection === "Adventure Logs") return "Adventure Log" + (n ? " " + n : "");
    if (asset.collection === "Cookbooks") return "Lulu & Ellie Cookbook" + (n ? " · Book " + n : "");
    if (asset.collection === "Diaries") return "Adventure Diary" + (n ? " " + n : "");
    if (asset.collection === "Field Guides") return "Field Guide" + (n ? " " + n : "");
    if (asset.collection === "Keepsakes") return "Keepsake Book" + (n ? " " + n : "");
    if (asset.collection === "Puzzle Books") return "Puzzle Book" + (n ? " " + n : "");
    if (asset.collection === "Search & Find") return "Search & Find" + (n ? " · Book " + n : "");
    if (asset.collection === "Bedtime") {
      const named = namedTitleFromFilename(asset);
      if (/moonbeam/i.test(path)) return "The Moonbeam That Wouldn’t Sleep";
      if (/blanket/i.test(path)) return "Blanket Fort Under the Stars";
      return n ? "Bedtime Adventures · Book " + n : (named || "Bedtime Adventures");
    }
    if (asset.collection === "Coloring") {
      const named = namedTitleFromFilename(asset).replace(/\bB\s*\d+\s*S\s*\d+\b/gi, "").trim();
      return named || "Lulu & Ellie Coloring Book";
    }
    if (asset.collection === "Lulu & Ellie Audio") {
      return titleCase(asset.filename).replace(/ Alternate$/i, " · Alternate Version");
    }

    return titleCase(asset.title || asset.filename);
  }

  function shelfFor(asset) {
    if (asset.kind === "audio" || asset.kind === "video") return "listen-watch";
    if (asset.kind === "image" || /Media/.test(asset.collection)) return "art";

    const learningCollections = new Set(["Backyard Academy", "Phonics", "Handwriting", "Cursive", "Learning"]);
    if (learningCollections.has(asset.collection)) return "learning";

    const activityCollections = new Set([
      "Adventure Logs", "Cookbooks", "Diaries", "Field Guides", "Keepsakes",
      "Puzzle Books", "Search & Find", "Coloring"
    ]);
    if (activityCollections.has(asset.collection)) return "activities";

    return "storybooks";
  }

  function shelfLabel(value) {
    return ({
      "": "Everything",
      storybooks: "Storybooks",
      learning: "Learning",
      activities: "Activities",
      "listen-watch": "Listen & Watch",
      art: "Art & Media"
    }[value] || "Everything");
  }

  function card(asset) {
    const article = document.createElement("article");
    article.className = "free-asset-card free-asset-" + asset.kind;

    const visual = document.createElement("div");
    visual.className = "free-asset-visual";
    visual.setAttribute("aria-hidden", "true");

    const ornament = document.createElement("span");
    ornament.className = "free-asset-ornament";
    ornament.textContent = "✦";
    const format = document.createElement("span");
    format.className = "free-asset-format";
    format.textContent = formatLabel(asset.kind);
    visual.append(ornament, format);

    const body = document.createElement("div");
    body.className = "free-asset-body";

    const meta = document.createElement("div");
    meta.className = "free-asset-meta";
    meta.textContent = asset.collection;

    const title = document.createElement("h3");
    title.textContent = displayTitle(asset);

    const access = document.createElement("p");
    access.className = "free-asset-access";
    access.textContent = asset.kind === "document"
      ? "Read online or save a free copy."
      : asset.kind === "audio"
        ? "Listen online or save the audio."
        : asset.kind === "video"
          ? "Watch online or save the video."
          : "View full size or save the image.";

    const actions = document.createElement("div");
    actions.className = "free-asset-actions";

    const view = document.createElement("a");
    view.className = "free-card-action free-card-action-primary";
    view.href = viewerHref(asset);
    view.textContent = actionLabel(asset.kind);

    const download = document.createElement("a");
    download.className = "free-card-action free-card-action-secondary";
    download.href = asset.download_url;
    download.target = "_blank";
    download.rel = "noopener";
    download.textContent = "Download";

    actions.append(view, download);
    body.append(meta, title, access, actions);
    article.append(visual, body);
    return article;
  }

  function filteredAssets() {
    const q = search.value.trim().toLowerCase();
    const selectedCollection = collection.value;
    const selectedKind = kind.value;

    return manifest.assets.filter((asset) => {
      if (activeShelf && shelfFor(asset) !== activeShelf) return false;
      if (selectedCollection && asset.collection !== selectedCollection) return false;
      if (selectedKind && asset.kind !== selectedKind) return false;
      if (!q) return true;

      const readable = displayTitle(asset);
      return [
        readable,
        asset.title,
        asset.filename,
        asset.collection,
        asset.path
      ].some((value) => String(value || "").toLowerCase().includes(q));
    });
  }

  function render() {
    if (!manifest) return;

    const assets = filteredAssets();
    const visible = assets.slice(0, visibleCount);

    grid.replaceChildren(...visible.map(card));

    if (!assets.length) {
      const empty = document.createElement("div");
      empty.className = "free-library-empty";
      empty.innerHTML = "<strong>No matches on this shelf.</strong><span>Try another collection or clear the filters.</span>";
      grid.append(empty);
    }

    if (assets.length > visible.length) {
      loadMore.hidden = false;
      loadMore.textContent = "Show " + Math.min(PAGE_SIZE, assets.length - visible.length) + " more";
    } else {
      loadMore.hidden = true;
    }

    if (assets.length && assets.length > visible.length) {
      count.textContent = "Showing " + visible.length + " of " + assets.length;
    } else {
      count.textContent = assets.length + (assets.length === 1 ? " item" : " items");
    }

    context.textContent = activeShelf
      ? shelfLabel(activeShelf) + " · free to view or download"
      : "Free to view or download";
  }

  function resetVisible() {
    visibleCount = PAGE_SIZE;
    render();
  }

  function selectShelf(value) {
    activeShelf = value;
    shelfTabs.forEach((tab) => {
      const selected = tab.dataset.shelf === value;
      tab.classList.toggle("is-active", selected);
      tab.setAttribute("aria-pressed", selected ? "true" : "false");
    });
    collection.value = "";
    kind.value = "";
    resetVisible();
  }

  async function init() {
    try {
      const response = await fetch("data/free-library.json", { cache: "no-cache" });
      if (!response.ok) throw new Error("The library inventory could not be loaded.");
      manifest = await response.json();

      const collections = [...new Set(manifest.assets.map((asset) => asset.collection))]
        .sort((a, b) => a.localeCompare(b));

      for (const name of collections) {
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        collection.append(option);
      }

      const counts = manifest.assets.reduce((acc, asset) => {
        acc[asset.kind] = (acc[asset.kind] || 0) + 1;
        return acc;
      }, {});

      const statValues = stats.querySelectorAll("strong");
      if (statValues[0]) statValues[0].textContent = manifest.asset_count;
      if (statValues[1]) statValues[1].textContent = counts.document || 0;
      if (statValues[2]) statValues[2].textContent = (counts.audio || 0) + (counts.video || 0);

      render();
    } catch (error) {
      count.textContent = "Library unavailable";
      context.textContent = "";
      const message = document.createElement("div");
      message.className = "free-library-empty";
      message.innerHTML = "<strong>We couldn’t open the shelves.</strong><span>Please try again shortly.</span>";
      grid.replaceChildren(message);
    }
  }

  shelfTabs.forEach((tab) => {
    tab.addEventListener("click", () => selectShelf(tab.dataset.shelf || ""));
  });

  search.addEventListener("input", resetVisible);
  collection.addEventListener("change", resetVisible);
  kind.addEventListener("change", resetVisible);

  reset.addEventListener("click", () => {
    search.value = "";
    collection.value = "";
    kind.value = "";
    selectShelf("");
    search.focus();
  });

  loadMore.addEventListener("click", () => {
    visibleCount += PAGE_SIZE;
    render();
  });

  init();
})();
