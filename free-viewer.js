(() => {
  "use strict";

  const title = document.getElementById("viewer-title");
  const collection = document.getElementById("viewer-collection");
  const file = document.getElementById("viewer-file");
  const breadcrumb = document.getElementById("viewer-breadcrumb");
  const actions = document.getElementById("viewer-actions");
  const stage = document.getElementById("viewer-stage");
  const status = document.getElementById("viewer-status");

  function actionLink(className, href, text) {
    const link = document.createElement("a");
    link.className = className;
    link.href = href;
    link.textContent = text;
    link.target = "_blank";
    link.rel = "noopener";
    return link;
  }

  function renderPdf(asset) {
    const frame = document.createElement("iframe");
    frame.className = "free-pdf-frame";
    frame.src = asset.download_url;
    frame.title = "Free PDF viewer: " + asset.title;
    frame.loading = "eager";
    stage.append(frame);
  }

  function renderAudio(asset) {
    const audio = document.createElement("audio");
    audio.className = "free-audio-player";
    audio.controls = true;
    audio.preload = "metadata";
    audio.src = asset.download_url;
    stage.append(audio);
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
    image.alt = asset.title;
    image.decoding = "async";
    stage.append(image);
  }

  async function init() {
    const key = new URLSearchParams(window.location.search).get("asset");
    if (!key) {
      status.textContent = "No archive item was selected.";
      title.textContent = "Choose an item from the Free Library";
      actions.append(actionLink("button", "free-library.html", "Back to Free Library"));
      return;
    }

    try {
      const response = await fetch("data/free-library.json", { cache: "no-cache" });
      if (!response.ok) throw new Error("Archive manifest could not be loaded.");
      const manifest = await response.json();
      const asset = manifest.assets.find((item) => item.key === key);
      if (!asset) throw new Error("That archive item is not in the current public manifest.");

      document.title = asset.title + " | Free Lulu & Ellie Viewer";
      title.textContent = asset.title;
      collection.textContent = asset.collection;
      file.textContent = asset.filename + " · " + asset.repo;
      breadcrumb.textContent = asset.title;

      actions.append(
        actionLink("button", asset.download_url, "Download free"),
        actionLink("button secondary", asset.download_url, "Open original"),
        actionLink("button secondary", asset.source_url, "View source record")
      );

      status.textContent = "Free " + asset.kind + " viewer · source-backed from " + asset.repo + ".";

      if (asset.kind === "document") renderPdf(asset);
      else if (asset.kind === "audio") renderAudio(asset);
      else if (asset.kind === "video") renderVideo(asset);
      else if (asset.kind === "image") renderImage(asset);
      else throw new Error("This file type does not have a viewer.");

    } catch (error) {
      status.textContent = error instanceof Error ? error.message : "The viewer could not load this item.";
      title.textContent = "Viewer unavailable";
      actions.append(actionLink("button", "free-library.html", "Back to Free Library"));
    }
  }

  init();
})();
