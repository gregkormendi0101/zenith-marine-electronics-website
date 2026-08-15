(() => {
  const root = document.documentElement;
  const body = document.body;
  root.classList.add('js');

  window.addEventListener('keydown', (event) => {
    if (event.key === 'Tab') body.classList.add('keyboard-nav');
  }, true);
  window.addEventListener('pointerdown', () => body.classList.remove('keyboard-nav'), true);

  const header = document.querySelector('[data-header]');
  let framePending = false;
  const updateHeader = () => {
    framePending = false;
    header?.classList.toggle('is-scrolled', window.scrollY > 18);
  };
  const requestHeaderUpdate = () => {
    if (framePending) return;
    framePending = true;
    requestAnimationFrame(updateHeader);
  };
  window.addEventListener('scroll', requestHeaderUpdate, { passive: true });
  updateHeader();

  const revealNodes = [...document.querySelectorAll('[data-reveal]')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.08 });
    revealNodes.forEach((node) => observer.observe(node));
  } else {
    revealNodes.forEach((node) => node.classList.add('is-visible'));
  }

  document.querySelectorAll('.focus-card').forEach((card) => {
    card.addEventListener('pointermove', (event) => {
      const rect = card.getBoundingClientRect();
      card.style.setProperty('--pointer-x', `${((event.clientX - rect.left) / rect.width) * 100}%`);
      card.style.setProperty('--pointer-y', `${((event.clientY - rect.top) / rect.height) * 100}%`);
    });
  });

  const incoming = new URLSearchParams(window.location.search);
  const attributionKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
  const attribution = attributionKeys.reduce((result, key) => {
    if (incoming.get(key)) result[key] = incoming.get(key);
    return result;
  }, {});

  if (Object.keys(attribution).length) {
    sessionStorage.setItem('zenith_attribution', JSON.stringify(attribution));
  }

  let storedAttribution = {};
  try {
    storedAttribution = JSON.parse(sessionStorage.getItem('zenith_attribution') || '{}');
  } catch (_) {
    storedAttribution = {};
  }

  if (Object.keys(storedAttribution).length) {
    document.querySelectorAll('a[href$=".html"], a[href*=".html#"]').forEach((link) => {
      const url = new URL(link.href, window.location.href);
      if (url.origin !== window.location.origin) return;
      Object.entries(storedAttribution).forEach(([key, value]) => url.searchParams.set(key, value));
      link.href = url.href;
    });
  }

  window.dataLayer = window.dataLayer || [];
  document.querySelectorAll('.track').forEach((link) => {
    link.addEventListener('click', () => {
      window.dataLayer.push({
        event: 'lead_action',
        action: link.dataset.event || 'contact',
        page: body.dataset.page || 'unknown',
        attribution: sessionStorage.getItem('zenith_attribution') || '{}',
      });
    });
  });

  document.querySelectorAll('[data-year]').forEach((node) => {
    node.textContent = String(new Date().getFullYear());
  });
})();
