(() => {
  const videos = Array.from(document.querySelectorAll("video"));
  if (!videos.length) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const visibility = new Map();
  let observer;

  function pauseAll() {
    videos.forEach((video) => video.pause());
  }

  function prepareVideos() {
    videos.forEach((video) => {
      video.muted = true;
      video.playsInline = true;
      video.preload = "metadata";
      video.removeAttribute("autoplay");
    });
  }

  function syncPlayback() {
    if (document.hidden || reducedMotion.matches) {
      pauseAll();
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

    videos.forEach((video) => {
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
    if (!("IntersectionObserver" in window)) {
      visibility.set(videos[0], 1);
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

    videos.forEach((video) => observer.observe(video));
  }

  prepareVideos();
  startObserver();

  document.addEventListener("visibilitychange", syncPlayback);
  reducedMotion.addEventListener?.("change", syncPlayback);
})();
