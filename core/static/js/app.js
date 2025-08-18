// Dark/Light theme toggle with persistence
(() => {
  const root = document.documentElement;
  const btn = document.getElementById('themeToggleBtn');
  const icon = document.getElementById('themeIcon');
  if (!btn || !icon) return;
  
  const apply = (mode) => {
    root.setAttribute('data-theme', mode);
    icon.className = mode === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
  };
  
  apply(localStorage.getItem('atlasly-theme') || 'light');
  
  btn.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    localStorage.setItem('atlasly-theme', next);
    apply(next);
  });
})();

// Header shadow on scroll
(() => {
  const header = document.querySelector('.sticky-header');
  if (!header) return;
  
  const onScroll = () => header.classList.toggle('is-stuck', window.scrollY > 10);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

// Products top search hide/show on scroll
(() => {
  const bar = document.getElementById('productsTopSearch');
  if (!bar) return;
  
  let lastY = window.scrollY;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (y > lastY && y > 160) {
      bar.classList.add('hide');
    } else {
      bar.classList.remove('hide');
    }
    lastY = y;
  }, { passive: true });
})();

// AJAX products list
(() => {
  const gridSel = '#productsGrid';
  const pagSel = '#productsPagination';
  
  const enhance = (html) => {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    const newGrid = doc.querySelector(gridSel);
    const newPag = doc.querySelector(pagSel);
    const grid = document.querySelector(gridSel);
    const pag = document.querySelector(pagSel);
    
    if (newGrid && grid) grid.replaceWith(newGrid);
    if (newPag && pag) pag.replaceWith(newPag);
    window.scrollTo({ top: 120, behavior: 'smooth' });
  };
  
  const fetchSwap = (url) => {
    fetch(url, { headers: { 'X-Requested-With': 'fetch' } })
    .then(r => r.text()).then(enhance).catch(console.error);
  };
  
  ['productsSearchForm', 'filtersForm'].forEach(id => {
    const form = document.getElementById(id);
    if (!form) return;
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const u = new URL(window.location.href);
      const fd = new FormData(form);
      for (const [k, v] of fd.entries()) {
        if (v) u.searchParams.set(k, v);
        else u.searchParams.delete(k);
      }
      u.searchParams.delete('page');
      history.replaceState(null, '', u.toString());
      fetchSwap(u.toString());
    });
  });
  
  document.addEventListener('click', (e) => {
    const a = e.target.closest('#productsPagination a.page-link');
    if (!a) return;
    e.preventDefault();
    history.replaceState(null, '', a.href);
    fetchSwap(a.href);
  });
})();

// Favorites toggle (session-based)
(() => {
  const updateBtn = (btn, active) => {
    const icon = btn.querySelector('i');
    if (!icon) return;
    icon.className = active ? 'bi bi-heart-fill text-danger' : 'bi bi-heart';
  };
  
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.favorite-toggle');
    if (!btn) return;
    e.preventDefault();
    const productId = btn.getAttribute('data-product-id');
    
    try {
      const response = await fetch('/products/favorites/toggle/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'fetch',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ product_id: productId })
      });
      
      const data = await response.json();
      if (response.ok) {
        updateBtn(btn, data.is_favorite);
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  });
  
  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content');
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
  }
})();

// Home products carousel
(() => {
  const carousel = document.getElementById('newProductsCarousel');
  if (!carousel || typeof Swiper === 'undefined') return;
  
  new Swiper(carousel, {
    slidesPerView: 1,
    spaceBetween: 20,
    loop: true,
    autoplay: {
      delay: 6000,
      disableOnInteraction: false,
      reverseDirection: true
    },
    breakpoints: {
      576: { slidesPerView: 2 },
      768: { slidesPerView: 3 },
      992: { slidesPerView: 4 },
      1200: { slidesPerView: 5 }
    }
  });
})();
