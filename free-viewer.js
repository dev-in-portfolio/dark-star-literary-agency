(() => {
  "use strict";

  const title = document.getElementById("viewer-title");
  const collection = document.getElementById("viewer-collection");
  const file = document.getElementById("viewer-file");
  const actions = document.getElementById("viewer-actions");
  const stage = document.getElementById("viewer-stage");
  const status = document.getElementById("viewer-status");
  const technical = document.getElementById("viewer-technical");

  const formatLabel = (kind) => ({
    document: "Free PDF",
    audio: "Free audio",
    video: "Free video",
    image: "Free image"
  }[kind] || "Free archive item");

  function words(value) {
    return String(value || "")
      .replace(/\.[^.]+$/, "")
      .replace(/[_-]+/g, " ")
      .replace(/([a-z])([A-Z])/g, "$1 $2")
      .replace(/([A-Za-z])(\d)/g, "$1 $2")
      .replace(/\b(final|optimized|interior|full|repaired|v\d+)\b/gi, "")
      .replace(/\bm\d+\b/gi, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function titleCase(value) {
    return words(value).split(" ").map((part) => {
      if (!part) return part;
      if (/^(and|of|the|in|to|that|with)$/i.test(part)) return part.toLowerCase();
      return part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
    }).join(" ").replace(/^Lulu /, "Lulu ").replace(/ Ellie /g, " Ellie ");
  }

  function displayTitle(asset) {
    const saved = sessionStorage.getItem("free-library-title:" + asset.key);
    if (saved) return saved;
    return titleCase(asset.title || asset.filename);
  }

  function actionLink(className, href, text, external = true) {
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

  function renderPdf(asset) {
    const frame = document.createElement("iframe");
    frame.className = "free-pdf-frame";
    frame.src = asset.download_url;
    frame.title = "PDF viewer: " + displayTitle(asset);
    frame.loading = "eager";
    stage.append(frame);
  }

  function renderAudio(asset) {
    const wrap = document.createElement("div");
    wrap.className = "free-player-wrap";
    const mark = document.createElement("div");
    mark.className = "free-player-mark";
    mark.textContent = "AUDIO";
    const audio = document.createElement("audio");
    audio.className = "free-audio-player";
    audio.controls = true;
    audio.preload = "metadata";
    audio.src = asset.download_url;
    wrap.append(mark, audio);
    stage.append(wrap);
  }

  function renderVideo(asset) {
    const video = document.createElement("video");
    video.className = "free-video-player";
    video.controls = true;
    video.preload = "metadata";
    video.playsInline = true;
    video.src = asset.download_url;
    stage.append(video);
  }

  function renderImage(asset) {
    const image = document.createElement("img");
    image.className = "free-image-viewer";
    image.src = asset.download_url;
    image.alt = displayTitle(asset);
    image.decoding = "async";
    stage.append(image);
  }

  async function init() {
    const key = new URLSearchParams(window.location.search).get("asset");
    if (!key) {
      status.textContent = "Choose something from the Free Library to open it here.";
      title.textContent = "Nothing selected";
      actions.append(actionLink("free-viewer-action free-viewer-action-primary", "free-library.html", "Browse the library", false));
      return;
    }

    try {
      const response = await fetch("data/free-library.json", { cache: "no-cache" });
      if (!response.ok) throw new Error("The library inventory could not be loaded.");
      const manifest = await response.json();
      const asset = manifest.assets.find((item) => item.key === key);
      if (!asset) throw new Error("That item is no longer in the current public library.");

      const readableTitle = displayTitle(asset);
      document.title = readableTitle + " | Free Lulu & Ellie Library";
      title.textContent = readableTitle;
      collection.textContent = asset.collection;
      file.textContent = formatLabel(asset.kind) + " · free to view or download";

      const download = actionLink("free-viewer-action free-viewer-action-primary", asset.download_url, "Download");
      const source = actionLink("free-viewer-action free-viewer-action-secondary", asset.source_url, "Source file");
      actions.append(download, source);

      technical.textContent = asset.filename + " · " + asset.repo;
      status.textContent = asset.kind === "document"
        ? "Read the book below, or download a copy to keep."
        : asset.kind === "audio"
          ? "Press play below, or download the audio to keep."
          : asset.kind === "video"
            ? "Watch below, or download the video to keep."
            : "View the full image below, or download a copy to keep.";

      if (asset.kind === "document") renderPdf(asset);
      else if (asset.kind === "audio") renderAudio(asset);
      else if (asset.kind === "video") renderVideo(asset);
      else if (asset.kind === "image") renderImage(asset);
      else throw new Error("This format does not have an inline viewer.");

    } catch (error) {
      status.textContent = error instanceof Error ? error.message : "The viewer could not load this item.";
      title.textContent = "Viewer unavailable";
      file.textContent = "";
      actions.append(actionLink("free-viewer-action free-viewer-action-primary", "free-library.html", "Back to the library", false));
    }
  }

  init();
})();
