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

  const formatLabel = (value) => ({
    document: "PDF",
    audio: "AUDIO",
    video: "VIDEO",
    image: "ART"
  }[value] || String(value || "").toUpperCase());

  const actionLabel = (value) => ({
    document: "Read",
    audio: "Listen",
    video: "Watch",
    image: "View"
  }[value] || "View");

  const viewerHref = (asset) => "free-viewer.html?asset=" + encodeURIComponent(asset.key);

  function shelfFor(asset) {
    if (asset.kind === "audio" || asset.kind === "video") return "listen-watch";
    if (asset.kind === "image" || asset.collection === "Original Adventure — Media") return "art";

    const learning = new Set(["Backyard Academy", "Phonics", "Handwriting", "Cursive", "Learning"]);
    if (learning.has(asset.collection)) return "learning";

    const activities = new Set([
      "Adventure Logs", "Cookbooks", "Diaries", "Field Guides", "Keepsakes",
      "Puzzle Books", "Search & Find", "Coloring"
    ]);
    if (activities.has(asset.collection)) return "activities";

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
    meta.textContent = asset.display_collection;

    const title = document.createElement("h3");
    title.textContent = asset.display_title;

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

      return [
        asset.display_title,
        asset.display_collection,
        asset.filename,
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

    loadMore.hidden = assets.length <= visible.length;
    if (!loadMore.hidden) {
      loadMore.textContent = "Show " + Math.min(PAGE_SIZE, assets.length - visible.length) + " more";
    }

    count.textContent = assets.length > visible.length
      ? "Showing " + visible.length + " of " + assets.length
      : assets.length + (assets.length === 1 ? " item" : " items");

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
      const response = await fetch("data/free-library.json?v=20260831-3", { cache: "no-store" });
      if (!response.ok) throw new Error("The library inventory could not be loaded.");
      manifest = await response.json();

      const byInternalCollection = new Map();
      for (const asset of manifest.assets) {
        if (!byInternalCollection.has(asset.collection)) {
          byInternalCollection.set(asset.collection, asset.display_collection);
        }
      }

      [...byInternalCollection.entries()]
        .sort((a, b) => a[1].localeCompare(b[1]))
        .forEach(([value, label]) => {
          const option = document.createElement("option");
          option.value = value;
          option.textContent = label;
          collection.append(option);
        });

      const counts = manifest.assets.reduce((acc, asset) => {
        acc[asset.kind] = (acc[asset.kind] || 0) + 1;
        return acc;
      }, {});

      const statValues = stats.querySelectorAll("strong");
      if (statValues[0]) statValues[0].textContent = manifest.asset_count;
      if (statValues[1]) statValues[1].textContent = counts.document || 0;
      if (statValues[2]) statValues[2].textContent = (counts.audio || 0) + (counts.video || 0);

      render();
    } catch (_) {
      count.textContent = "Library unavailable";
      context.textContent = "";
      const message = document.createElement("div");
      message.className = "free-library-empty";
      message.innerHTML = "<strong>We couldn’t open the shelves.</strong><span>Please try again shortly.</span>";
      grid.replaceChildren(message);
    }
  }

  shelfTabs.forEach((tab) => tab.addEventListener("click", () => selectShelf(tab.dataset.shelf || "")));
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
