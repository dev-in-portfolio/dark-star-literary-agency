(() => {
  "use strict";

  const grid = document.getElementById("free-library-grid");
  const count = document.getElementById("free-result-count");
  const stats = document.getElementById("free-library-stats");
  const search = document.getElementById("free-search");
  const collection = document.getElementById("free-collection");
  const kind = document.getElementById("free-kind");
  const reset = document.getElementById("free-reset");

  let manifest = null;

  const typeLabel = (value) => ({
    document: "PDF",
    audio: "Audio",
    video: "Video",
    image: "Image"
  }[value] || value);

  const viewerHref = (asset) => "free-viewer.html?asset=" + encodeURIComponent(asset.key);

  function actionLink(className, href, text, external = false) {
    const link = document.createElement("a");
    link.className = className;
    link.href = href;
    link.textContent = text;
    if (external) {
      link.target = "_blank";
      link.rel = "noopener";
    }
    return link;
  }

  function card(asset) {
    const article = document.createElement("article");
    article.className = "free-asset-card";

    const top = document.createElement("div");
    top.className = "tag-row";
    const type = document.createElement("span");
    type.className = "status-badge";
    type.textContent = typeLabel(asset.kind);
    const repo = document.createElement("span");
    repo.className = "tag";
    repo.textContent = asset.repo;
    top.append(type, repo);

    const title = document.createElement("h3");
    title.textContent = asset.title;

    const collectionName = document.createElement("p");
    collectionName.className = "free-asset-collection";
    collectionName.textContent = asset.collection;

    const filename = document.createElement("p");
    filename.className = "free-asset-filename";
    filename.textContent = asset.filename;

    const actions = document.createElement("div");
    actions.className = "section-actions";
    actions.append(
      actionLink("button", viewerHref(asset), "View free"),
      actionLink("button secondary", asset.download_url, "Download free", true)
    );

    article.append(top, title, collectionName, filename, actions);
    return article;
  }

  function filteredAssets() {
    const q = search.value.trim().toLowerCase();
    const selectedCollection = collection.value;
    const selectedKind = kind.value;
    return manifest.assets.filter((asset) => {
      if (selectedCollection && asset.collection !== selectedCollection) return false;
      if (selectedKind && asset.kind !== selectedKind) return false;
      if (!q) return true;
      return [
        asset.title,
        asset.filename,
        asset.collection,
        asset.repo,
        asset.path
      ].some((value) => String(value || "").toLowerCase().includes(q));
    });
  }

  function render() {
    const assets = filteredAssets();
    count.textContent = assets.length + (assets.length === 1 ? " free item" : " free items");
    grid.replaceChildren(...assets.map(card));
    if (!assets.length) {
      const empty = document.createElement("div");
      empty.className = "catalog-notice";
      empty.textContent = "No archive items match those filters.";
      grid.append(empty);
    }
  }

  async function init() {
    try {
      const response = await fetch("data/free-library.json", { cache: "no-cache" });
      if (!response.ok) throw new Error("Archive manifest could not be loaded.");
      manifest = await response.json();

      const collections = [...new Set(manifest.assets.map((asset) => asset.collection))].sort((a, b) => a.localeCompare(b));
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
      stats.textContent =
        manifest.asset_count + " items · " +
        (counts.document || 0) + " PDFs · " +
        (counts.audio || 0) + " audio · " +
        (counts.video || 0) + " video · " +
        (counts.image || 0) + " images";

      render();
    } catch (error) {
      count.textContent = "Archive unavailable";
      stats.textContent = "The archive manifest could not be loaded.";
      const message = document.createElement("div");
      message.className = "catalog-notice";
      message.textContent = error instanceof Error ? error.message : "Archive manifest could not be loaded.";
      grid.replaceChildren(message);
    }
  }

  search.addEventListener("input", render);
  collection.addEventListener("change", render);
  kind.addEventListener("change", render);
  reset.addEventListener("click", () => {
    search.value = "";
    collection.value = "";
    kind.value = "";
    search.focus();
    render();
  });

  init();
})();
