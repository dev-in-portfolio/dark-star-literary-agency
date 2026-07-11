(() => {
  "use strict";

  const root = document.getElementById("companion-catalog");
  if (!root) return;

  const make = (tag, className, text) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text) element.textContent = text;
    return element;
  };

  const renderItem = (item) => {
    const card = make("article", "book-list-card");
    const tags = make("div", "tag-row");
    tags.append(
      make("span", "book-number", item.format),
      make("span", "status-badge", `${item.pages} pages`)
    );

    card.append(tags, make("h3", "", item.title));

    if (item.subtitle) {
      card.append(make("p", "", item.subtitle));
    }

    card.append(
      make(
        "p",
        "support-note",
        "Collection preview - purchase availability is confirmed separately."
      )
    );
    return card;
  };

  const renderCollection = (collection) => {
    const group = make("article", "card all-books-group");
    group.append(
      make("div", "section-kicker", collection.collection),
      make("p", "", collection.description)
    );

    const grid = make("div", "book-list-grid");
    collection.items.forEach((item) => grid.append(renderItem(item)));
    group.append(grid);
    return group;
  };

  fetch("data/companion-catalog.json")
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Catalog request failed with ${response.status}`);
      }
      return response.json();
    })
    .then((catalog) => {
      root.replaceChildren();
      catalog.collections.forEach((collection) => root.append(renderCollection(collection)));
    })
    .catch((error) => {
      console.error(error);
      const card = make("article", "card");
      card.append(
        make(
          "p",
          "",
          "The companion catalog could not be loaded. Please use the main Library or contact Dark Star Literary Agency."
        )
      );
      root.replaceChildren(card);
    });
})();
