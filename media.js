(() => {
  "use strict";

  const allVideos = Array.from(document.querySelectorAll("video"));
  if (!allVideos.length) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const managedVideos = allVideos.filter((video) => !video.hasAttribute("controls"));
  const visibility = new Map();
  let observer;

  function prepareVideos() {
    allVideos.forEach((video) => {
      video.muted = true;
      video.playsInline = true;
      video.removeAttribute("autoplay");
      if (!video.hasAttribute("controls")) {
        video.preload = "metadata";
      }
    });
  }

  function pauseManagedVideos() {
    managedVideos.forEach((video) => video.pause());
  }

  function syncPlayback() {
    if (!managedVideos.length || document.hidden || reducedMotion.matches) {
      pauseManagedVideos();
      return;
    }

    let activeVideo = null;
    let bestRatio = 0;

    visibility.forEach((ratio, video) => {
      if (ratio > bestRatio) {
        activeVideo = video;
        bestRatio = ratio;
      }
    });

    managedVideos.forEach((video) => {
      if (video === activeVideo && bestRatio >= 0.45) {
        const playPromise = video.play();
        if (playPromise && typeof playPromise.catch === "function") {
          playPromise.catch(() => undefined);
        }
      } else {
        video.pause();
      }
    });
  }

  function startObserver() {
    if (!managedVideos.length) return;

    if (!("IntersectionObserver" in window)) {
      visibility.set(managedVideos[0], 1);
      syncPlayback();
      return;
    }

    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => visibility.set(entry.target, entry.intersectionRatio));
        syncPlayback();
      },
      { threshold: [0, 0.25, 0.45, 0.65, 0.85] }
    );

    managedVideos.forEach((video) => observer.observe(video));
  }

  prepareVideos();
  startObserver();

  document.addEventListener("visibilitychange", syncPlayback);
  reducedMotion.addEventListener?.("change", syncPlayback);
})();
