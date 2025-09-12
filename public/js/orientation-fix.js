document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".single img").forEach(img => {
    // Handle already-loaded and lazy-loaded images
    function mark() {
      if (img.naturalHeight > img.naturalWidth) {
        img.classList.add("portrait");
      }
    }
    if (img.complete) {
      mark();
    } else {
      img.addEventListener("load", mark);
    }
  });
});
