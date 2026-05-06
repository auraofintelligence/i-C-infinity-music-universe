document.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector(".site-header");
  const navToggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");
  const searchInput = document.querySelector("[data-song-search]");
  const keywordSelect = document.querySelector("[data-song-keyword]");
  const filterCount = document.querySelector("[data-filter-count]");
  const cards = Array.from(document.querySelectorAll("[data-song-card]"));

  if (header && navToggle && nav) {
    const closeNav = () => {
      header.classList.remove("nav-open");
      navToggle.setAttribute("aria-expanded", "false");
    };

    navToggle.addEventListener("click", () => {
      const isOpen = header.classList.toggle("nav-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });

    nav.addEventListener("click", (event) => {
      if (event.target instanceof HTMLAnchorElement) {
        closeNav();
      }
    });

    document.addEventListener("click", (event) => {
      if (event.target instanceof Node && !header.contains(event.target)) {
        closeNav();
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeNav();
      }
    });
  }

  if (searchInput && cards.length) {
    const cardKeywords = new Map();
    const keywordCounts = new Map();
    const keywordLabels = new Map();

    cards.forEach((card) => {
      const keywords = Array.from(card.querySelectorAll(".tag-line span"))
        .map((tag) => (tag.textContent || "").trim())
        .filter(Boolean);
      const normalised = keywords.map((keyword) => keyword.toLowerCase());
      cardKeywords.set(card, normalised);

      normalised.forEach((keyword, index) => {
        keywordCounts.set(keyword, (keywordCounts.get(keyword) || 0) + 1);
        if (!keywordLabels.has(keyword)) {
          keywordLabels.set(keyword, keywords[index]);
        }
      });
    });

    if (keywordSelect instanceof HTMLSelectElement && keywordCounts.size) {
      Array.from(keywordCounts.keys())
        .sort((a, b) => a.localeCompare(b))
        .forEach((keyword) => {
          const option = document.createElement("option");
          option.value = keyword;
          option.textContent = `${keywordLabels.get(keyword) || keyword} (${keywordCounts.get(keyword)})`;
          keywordSelect.appendChild(option);
        });
    }

    const applySongFilters = () => {
      const query = searchInput.value.trim().toLowerCase();
      const keyword = keywordSelect instanceof HTMLSelectElement ? keywordSelect.value : "";
      let visibleCount = 0;

      cards.forEach((card) => {
        const haystack = card.getAttribute("data-search") || "";
        const matchesQuery = !query || haystack.includes(query);
        const matchesKeyword = !keyword || (cardKeywords.get(card) || []).includes(keyword);
        const isVisible = matchesQuery && matchesKeyword;
        card.hidden = !isVisible;
        if (isVisible) visibleCount += 1;
      });

      if (filterCount) {
        filterCount.textContent = `Showing ${visibleCount} of ${cards.length} songs`;
      }
    };

    searchInput.addEventListener("input", applySongFilters);
    if (keywordSelect instanceof HTMLSelectElement) {
      keywordSelect.addEventListener("change", applySongFilters);
    }
    applySongFilters();
  }
});
