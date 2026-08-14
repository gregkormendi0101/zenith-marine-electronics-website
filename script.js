(() => {
  document.documentElement.classList.add('has-js');

  const header = document.querySelector('[data-header]');
  const updateHeader = () => header?.classList.toggle('is-scrolled', window.scrollY > 18);
  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });

  const revealNodes = [...document.querySelectorAll('[data-reveal]')];
  const heroNodes = [...document.querySelectorAll('.hero [data-reveal]')];
  heroNodes.forEach((node, index) => {
    node.style.transitionDelay = `${80 + index * 75}ms`;
  });

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealNodes.forEach((node) => observer.observe(node));
  } else {
    revealNodes.forEach((node) => node.classList.add('is-visible'));
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
        attribution: sessionStorage.getItem('zenith_attribution') || '{}'
      });
    });
  });

  document.querySelectorAll('[data-year]').forEach((node) => {
    node.textContent = String(new Date().getFullYear());
  });
})();
