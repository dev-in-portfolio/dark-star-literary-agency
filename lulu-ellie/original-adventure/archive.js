(() => {
  "use strict";

  const namedBooks = [
    { number: 1, title: "Lulu & Ellie and the Secret of Blackwater Bay", slug: "lulu-and-ellie-and-the-secret-of-blackwater-bay.html", cover: "png" },
    { number: 2, title: "Lulu & Ellie and the Lost Valley of Thunder", slug: "lulu-and-ellie-and-the-lost-valley-of-thunder.html", cover: "jpg" },
    { number: 3, title: "Lulu & Ellie and the Clockwork Forest", slug: "lulu-and-ellie-and-the-clockwork-forest.html", cover: "jpg" },
    { number: 4, title: "Lulu & Ellie and the Moonlit Circus", slug: "lulu-and-ellie-and-the-moonlit-circus.html", cover: "jpg" },
    { number: 5, title: "Lulu & Ellie and the Snow Dragon's Bell", slug: "lulu-and-ellie-and-the-snow-dragons-bell.html", cover: "jpg" },
    { number: 6, title: "Lulu & Ellie and the Mushroom Moon Maze", slug: "lulu-and-ellie-and-the-mushroom-moon-maze.html", cover: "jpg" },
    { number: 7, title: "Lulu & Ellie and the Lanterns of the Deep", slug: "lulu-and-ellie-and-the-lanterns-of-the-deep.html", cover: "jpg" },
    { number: 8, title: "Lulu & Ellie and the Book That Lost Its Ending", slug: "lulu-and-ellie-and-the-book-that-lost-its-ending.html", cover: "jpg" },
    { number: 9, title: "Lulu & Ellie and the Island That Drifted Away", slug: "lulu-and-ellie-and-the-island-that-drifted-away.html", cover: "jpg" },
    { number: 10, title: "Lulu & Ellie and the Star Map of Everywhere", slug: "lulu-and-ellie-and-the-star-map-of-everywhere.html", cover: "jpg" }
  ];

  const archiveVolumes = Array.from({ length: 10 }, (_, index) => ({
    number: index + 11,
    title: `Archive Volume ${index + 11}`,
    cover: "jpg"
  }));

  const assetRoot = "../../assets/lulu-ellie/original-adventure";
  const make = (tag, className, text) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text) element.textContent = text;
    return element;
  };

  const mediaCard = (item, isArchive) => {
    const article = make("article", "card book-media-card");
    const video = document.createElement("video");
    video.controls = true;
    video.muted = true;
    video.loop = true;
    video.playsInline = true;
    video.preload = "none";
    video.poster = `${assetRoot}/book-${item.number}/front-cover.${item.cover}`;

    const source = document.createElement("source");
    source.src = `${assetRoot}/book-${item.number}/animated-cover.mp4`;
    source.type = "video/mp4";
    video.append(source, document.createTextNode("Your browser does not support the animated cover preview."));

    const copy = make("div", "card-copy");
    const tags = make("div", "tag-row");
    tags.append(
      make("span", "book-number", isArchive ? `Archive Volume ${item.number}` : `Book ${item.number}`),
      make("span", "status-badge", isArchive ? "Media preview" : (item.number === 6 ? "Temporarily unavailable" : "Named storybook"))
    );
    copy.append(tags, make("h3", "", item.title));
    copy.append(
      make(
        "p",
        "",
        isArchive
          ? "Cover, motion, and interior media exist. Public title and publication details remain unconfirmed."
          : "Cover art and an optional motion preview from the matching numbered archive folder."
      )
    );

    if (!isArchive) {
      const actions = make("div", "section-actions");
      const link = make("a", "button ghost", "Explore Book");
      link.href = `../../books/${item.slug}`;
      actions.append(link);
      copy.append(actions);
    }

    article.append(video, copy);
    return article;
  };

  const featureCard = (item, isArchive) => {
    const article = make("article", "card book-media-card");
    const image = document.createElement("img");
    image.src = `${assetRoot}/book-${item.number}/feature-page.png`;
    image.alt = isArchive
      ? `Original Adventure Archive Volume ${item.number} interior feature page`
      : `${item.title} interior feature page`;
    image.loading = "lazy";

    const copy = make("div", "card-copy");
    const tags = make("div", "tag-row");
    tags.append(
      make("span", "book-number", isArchive ? `Archive Volume ${item.number}` : `Book ${item.number}`),
      make("span", "status-badge", "Interior media")
    );
    copy.append(tags, make("h3", "", item.title), make("p", "", "Interior feature art preserved in the numbered media archive."));
    article.append(image, copy);
    return article;
  };

  const namedRoot = document.getElementById("named-media-grid");
  const archiveRoot = document.getElementById("archive-media-grid");
  const featureRoot = document.getElementById("feature-media-grid");

  namedBooks.forEach((item) => namedRoot?.append(mediaCard(item, false)));
  archiveVolumes.forEach((item) => archiveRoot?.append(mediaCard(item, true)));
  namedBooks.filter((item) => item.number >= 2).forEach((item) => featureRoot?.append(featureCard(item, false)));
  archiveVolumes.forEach((item) => featureRoot?.append(featureCard(item, true)));
})();
