document.addEventListener("DOMContentLoaded", () => {
  const player = document.querySelector("[data-album-player]");
  const iframe = player?.querySelector("[data-album-iframe]");
  if (!player || !iframe) return;

  const watchLinks = Array.from(document.querySelectorAll("[data-album-video]"));
  const feature = player.querySelector("[data-album-video-feature]");
  const frame = player.querySelector("[data-album-video-frame]");
  const heading = player.querySelector("[data-album-player-heading]");
  const currentTitle = player.querySelector("[data-album-current-title]");
  const youtubeLink = player.querySelector("[data-album-open-youtube]");

  watchLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      // Preserve deliberate new-tab clicks and the direct link if JavaScript is unavailable.
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      const videoId = link.dataset.albumVideo;
      if (!/^[A-Za-z0-9_-]{11}$/.test(videoId || "")) return;
      event.preventDefault();

      const src = new URL(`https://www.youtube.com/embed/${videoId}`);
      const playlistId = link.dataset.playlistId;
      if (playlistId) src.searchParams.set("list", playlistId);
      src.searchParams.set("rel", "0");
      src.searchParams.set("autoplay", "1");
      iframe.src = src.href;
      iframe.title = `${link.dataset.videoTitle} video player`;
      iframe.loading = "eager";

      const isWide = link.dataset.videoOrientation !== "vertical";
      feature.classList.toggle("landscape-feature", isWide);
      frame.classList.toggle("wide-video-frame", isWide);
      currentTitle.textContent = `Selected: ${link.dataset.videoTitle}`;
      youtubeLink.href = link.href;

      watchLinks.forEach((other) => {
        const selected = other === link;
        other.closest(".track-row")?.classList.toggle("is-selected", selected);
        if (selected) other.setAttribute("aria-current", "true");
        else other.removeAttribute("aria-current");
      });

      heading.focus({ preventScroll: true });
      const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      player.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
    });
  });
});
