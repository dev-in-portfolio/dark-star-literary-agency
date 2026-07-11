(() => {
  "use strict";

  const status = document.getElementById("catalog-verification");
  const staticItems = document.querySelectorAll("[data-source-id]");

  fetch("data/companion-catalog.json")
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Catalog request failed with ${response.status}`);
      }
      return response.json();
    })
    .then((catalog) => {
      const collections = Array.isArray(catalog.collections) ? catalog.collections : [];
      const structuredItems = collections.reduce(
        (total, collection) => total + (Array.isArray(collection.items) ? collection.items.length : 0),
        0
      );
      const staticIds = new Set(Array.from(staticItems, (item) => item.dataset.sourceId));

      if (
        structuredItems !== staticItems.length ||
        structuredItems !== 44 ||
        collections.length !== 12 ||
        staticIds.size !== staticItems.length
      ) {
        throw new Error("Static and structured companion catalogs do not match.");
      }

      if (status) {
        status.textContent =
          "Structured catalog verified: 44 titles across 12 collections match the static page.";
      }
      document.documentElement.dataset.catalogVerified = "true";
    })
    .catch((error) => {
      console.error(error);
      if (status) {
        status.textContent =
          "The static catalog remains available, but its structured-data verification could not be completed.";
      }
      document.documentElement.dataset.catalogVerified = "false";
    });
})();
