document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.querySelector("[data-song-search]");
  const cards = Array.from(document.querySelectorAll("[data-song-card]"));

  if (searchInput && cards.length) {
    searchInput.addEventListener("input", () => {
      const query = searchInput.value.trim().toLowerCase();
      cards.forEach((card) => {
        const haystack = card.getAttribute("data-search") || "";
        card.hidden = query.length > 0 && !haystack.includes(query);
      });
    });
  }
});
