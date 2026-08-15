(() => {
  const root = document.documentElement;
  const body = document.body;
  root.classList.add('js');

  window.addEventListener('keydown', (event) => {
    if (event.key === 'Tab') body.classList.add('keyboard-nav');
  }, true);
  window.addEventListener('pointerdown', () => body.classList.remove('keyboard-nav'), true);

  const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
  const header = document.querySelector('[data-header]');
  const hero = document.querySelector('[data-hero]');
  const heroImage = document.querySelector('[data-hero-image]');
  const heroPath = document.querySelector('.hero-signal path');
  const heroDot = document.querySelector('[data-hero-dot]');
  const contact = document.querySelector('[data-contact]');
  const progressBar = document.querySelector('[data-page-progress]');
  const driftNodes = [...document.querySelectorAll('[data-drift]')];
  const motionSections = [...document.querySelectorAll('[data-motion-section]')];
  const serviceVisuals = [...document.querySelectorAll('.service-visual')];

  const routeSections = motionSections.map((section) => {
    const path = section.querySelector('[data-route]');
    const dot = section.querySelector('[data-route-dot]');
    return {
      section,
      path,
      dot,
      length: path?.getTotalLength?.() || 0,
    };
  });

  const positionDot = (path, dot, length, progress) => {
    if (!path || !dot || !length) return;
    const point = path.getPointAtLength(length * clamp(progress));
    dot.setAttribute('cx', point.x.toFixed(2));
    dot.setAttribute('cy', point.y.toFixed(2));
  };

  let frameRequested = false;

  const updateMotion = () => {
    frameRequested = false;
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const viewportHeight = window.innerHeight;
    const scrollRange = Math.max(1, document.documentElement.scrollHeight - viewportHeight);
    const pageProgress = clamp(scrollTop / scrollRange);

    progressBar?.style.setProperty('transform', `scaleX(${pageProgress.toFixed(5)})`);
    header?.classList.toggle('is-scrolled', scrollTop > 18);

    if (hero) {
      const heroHeight = Math.max(1, hero.offsetHeight);
      const heroProgress = clamp(scrollTop / heroHeight);
      const heroShift = Math.min(78, scrollTop * 0.1);
      heroImage?.style.setProperty('--hero-shift', heroShift.toFixed(2));
      if (heroPath && heroDot) {
        positionDot(heroPath, heroDot, heroPath.getTotalLength(), heroProgress);
      }

      const heroBottom = hero.getBoundingClientRect().bottom;
      body.classList.toggle('show-mobile-lead', heroBottom < viewportHeight * 0.58);
    }

    if (contact) {
      const contactRect = contact.getBoundingClientRect();
      body.classList.toggle(
        'at-contact',
        contactRect.top < viewportHeight * 0.82 && contactRect.bottom > viewportHeight * 0.15,
      );
    }

    routeSections.forEach(({ section, path, dot, length }) => {
      const rect = section.getBoundingClientRect();
      const travel = viewportHeight + rect.height;
      const progress = clamp((viewportHeight - rect.top) / Math.max(1, travel));
      section.style.setProperty('--section-progress', progress.toFixed(5));
      positionDot(path, dot, length, progress);
    });

    driftNodes.forEach((node) => {
      const rect = node.getBoundingClientRect();
      const centerOffset = (rect.top + rect.height / 2 - viewportHeight / 2) / viewportHeight;
      const drift = clamp(centerOffset, -1.2, 1.2) * -30;
      node.style.setProperty('--drift', drift.toFixed(2));
    });
  };

  const requestMotionUpdate = () => {
    if (frameRequested) return;
    frameRequested = true;
    window.requestAnimationFrame(updateMotion);
  };

  window.addEventListener('scroll', requestMotionUpdate, { passive: true });
  window.addEventListener('resize', requestMotionUpdate, { passive: true });
  window.addEventListener('load', requestMotionUpdate, { once: true });
  requestMotionUpdate();

  const revealNodes = [...document.querySelectorAll('[data-reveal]')];
  if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        revealObserver.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -7% 0px', threshold: 0.08 });
    revealNodes.forEach((node) => revealObserver.observe(node));

    const sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        entry.target.classList.toggle('is-active', entry.isIntersecting);
      });
    }, { rootMargin: '-22% 0px -22% 0px', threshold: 0.08 });
    motionSections.forEach((section) => sectionObserver.observe(section));

    const visibleVisuals = new Set();
    const visualObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) visibleVisuals.add(entry.target);
        else visibleVisuals.delete(entry.target);
      });
      body.classList.toggle('visual-in-view', visibleVisuals.size > 0);
    }, { rootMargin: '-8% 0px -8% 0px', threshold: 0.12 });
    serviceVisuals.forEach((visual) => visualObserver.observe(visual));
  } else {
    revealNodes.forEach((node) => node.classList.add('is-visible'));
    motionSections.forEach((section) => section.classList.add('is-active'));
  }

  const params = new URLSearchParams(window.location.search);
  const attribution = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content']
    .reduce((result, key) => {
      if (params.get(key)) result[key] = params.get(key);
      return result;
    }, {});

  if (Object.keys(attribution).length) {
    sessionStorage.setItem('zenith_attribution', JSON.stringify(attribution));
  }

  window.dataLayer = window.dataLayer || [];
  document.querySelectorAll('.track').forEach((link) => {
    link.addEventListener('click', () => {
      window.dataLayer.push({
        event: 'lead_action',
        action: link.dataset.event || 'contact',
        attribution: sessionStorage.getItem('zenith_attribution') || '{}',
      });
    });
  });

  document.querySelectorAll('[data-year]').forEach((node) => {
    node.textContent = String(new Date().getFullYear());
  });
})();
