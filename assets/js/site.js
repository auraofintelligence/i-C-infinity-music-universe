document.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector(".site-header");
  const navToggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");
  const searchInput = document.querySelector("[data-song-search]");
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
    searchInput.addEventListener("input", () => {
      const query = searchInput.value.trim().toLowerCase();
      cards.forEach((card) => {
        const haystack = card.getAttribute("data-search") || "";
        card.hidden = query.length > 0 && !haystack.includes(query);
      });
    });
  }
});
