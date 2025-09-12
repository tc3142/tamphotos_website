document.addEventListener('DOMContentLoaded', () => {
  // ✅ Make sure these filenames & folder match exactly
  const paths = [
    '/assets/img/slide/photo1.jpg',
    '/assets/img/slide/photo2.jpg',
    '/assets/img/slide/photo3.jpg',
    '/assets/img/slide/photo4.jpg',
    '/assets/img/slide/photo5.jpg',
    '/assets/img/slide/photo6.jpg',
    '/assets/img/slide/photo7.jpg',
    '/assets/img/slide/photo8.jpg',
    '/assets/img/slide/photo9.jpg',
    '/assets/img/slide/photo10.jpg',
    '/assets/img/slide/photo11.jpg',
    '/assets/img/slide/photo12.jpg',
    '/assets/img/slide/photo13.jpg',
    '/assets/img/slide/photo14.jpg',
    '/assets/img/slide/photo15.jpg',
    '/assets/img/slide/photo16.jpg',
    '/assets/img/slide/photo17.jpg',
    '/assets/img/slide/photo18.jpg',
    '/assets/img/slide/photo19.jpg',
    '/assets/img/slide/photo20.jpg',
    '/assets/img/slide/photo21.jpg',
    '/assets/img/slide/photo22.jpg',
    '/assets/img/slide/photo23.jpg',
    '/assets/img/slide/photo24.jpg',
    '/assets/img/slide/photo25.jpg',
    '/assets/img/slide/photo26.jpg'
    // add more...
  ];

  const bg = document.getElementById('bg');
  if (!bg) {
    console.error('[slideshow] #bg not found in DOM');
    return;
  }
  if (!paths || paths.length < 2) {
    console.warn('[slideshow] Need at least 2 images to rotate. paths.length=', paths.length);
  }

  // Preload + map to {src,img,ok}
  const items = paths.map(src => {
    const im = new Image();
    const item = { src, img: im, ok: false };
    im.onload = () => { item.ok = true; };
    im.onerror = () => { item.ok = false; console.error('[slideshow] failed to load:', src); };
    im.src = src;
    return item;
  });

  let i = 0;
  // Show first immediately (uses the <img src="..."> in HTML if present, else this sets it)
  bg.src = items[i].src;

  function nextIndex(start) {
    // find the next loadable image (avoid infinite loop if all fail)
    for (let step = 1; step <= items.length; step++) {
      const idx = (start + step) % items.length;
      if (items[idx].ok || items.length === 1) return idx;
    }
    return start; // fallback
  }

  function tick() {
    i = nextIndex(i);
    bg.src = items[i].src;
    // DEBUG: see changes in console
    // console.log('[slideshow] showing', bg.src);
  }

  // Hold each frame 3s, then hard-swap (no fade)
  setInterval(tick, 3000);
});
