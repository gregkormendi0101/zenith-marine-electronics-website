(() => {
  'use strict';

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  const root = document.documentElement;
  const header = document.querySelector('[data-header]');
  const parallaxCards = [...document.querySelectorAll('[data-parallax]')];
  let framePending = false;

  document.querySelectorAll('[data-year]').forEach((node) => {
    node.textContent = String(new Date().getFullYear());
  });

  const updateMotion = () => {
    framePending = false;
    const scrollY = window.scrollY || 0;
    root.style.setProperty('--ambient-one-y', `${Math.min(scrollY * 0.035, 42)}px`);
    root.style.setProperty('--ambient-two-y', `${Math.max(scrollY * -0.022, -42)}px`);
    header?.classList.toggle('is-scrolled', scrollY > 12);

    if (reducedMotion.matches) {
      parallaxCards.forEach((card) => card.style.setProperty('--parallax-y', '0px'));
      return;
    }

    const viewportCenter = window.innerHeight / 2;
    parallaxCards.forEach((card) => {
      const rect = card.getBoundingClientRect();
      if (rect.bottom < -100 || rect.top > window.innerHeight + 100) return;
      const cardCenter = rect.top + rect.height / 2;
      const offset = Math.max(-16, Math.min(16, (viewportCenter - cardCenter) * 0.035));
      card.style.setProperty('--parallax-y', `${offset.toFixed(2)}px`);
    });
  };

  const requestMotionFrame = () => {
    if (framePending) return;
    framePending = true;
    window.requestAnimationFrame(updateMotion);
  };

  window.addEventListener('scroll', requestMotionFrame, { passive: true });
  window.addEventListener('resize', requestMotionFrame, { passive: true });
  reducedMotion.addEventListener?.('change', requestMotionFrame);
  updateMotion();

  const revealNodes = [...document.querySelectorAll('[data-reveal]')];
  if (reducedMotion.matches || !('IntersectionObserver' in window)) {
    revealNodes.forEach((node) => node.classList.add('is-visible'));
  } else {
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        revealObserver.unobserve(entry.target);
      });
    }, { rootMargin: '-4% 0px -8%', threshold: 0.08 });
    revealNodes.forEach((node) => revealObserver.observe(node));
  }

  document.querySelectorAll('[data-tilt]').forEach((surface) => {
    surface.addEventListener('pointermove', (event) => {
      if (!finePointer.matches || reducedMotion.matches) return;
      const rect = surface.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * 100;
      const y = ((event.clientY - rect.top) / rect.height) * 100;
      surface.style.setProperty('--pointer-x', `${x.toFixed(1)}%`);
      surface.style.setProperty('--pointer-y', `${y.toFixed(1)}%`);
    });
    surface.addEventListener('pointerleave', () => {
      surface.style.setProperty('--pointer-x', '50%');
      surface.style.setProperty('--pointer-y', '20%');
    });
  });

  document.querySelectorAll('[data-system-tabs]').forEach((consoleNode) => {
    const tabs = [...consoleNode.querySelectorAll('[data-system-target]')];
    const panels = [...consoleNode.querySelectorAll('[data-system-panel]')];

    const activate = (name, moveFocus = false) => {
      const nextTab = tabs.find((tab) => tab.dataset.systemTarget === name);
      const nextPanel = panels.find((panel) => panel.dataset.systemPanel === name);
      if (!nextTab || !nextPanel || nextTab.classList.contains('is-active')) return;

      tabs.forEach((tab) => {
        const active = tab === nextTab;
        tab.classList.toggle('is-active', active);
        tab.setAttribute('aria-selected', String(active));
        tab.tabIndex = active ? 0 : -1;
      });

      panels.forEach((panel) => {
        const active = panel === nextPanel;
        panel.hidden = !active;
        panel.classList.toggle('is-active', active);
      });

      if (moveFocus) nextTab.focus();
      requestMotionFrame();
    };

    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => activate(tab.dataset.systemTarget));
      tab.addEventListener('keydown', (event) => {
        if (!['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp', 'Home', 'End'].includes(event.key)) return;
        event.preventDefault();
        let nextIndex = index;
        if (event.key === 'ArrowRight' || event.key === 'ArrowDown') nextIndex = (index + 1) % tabs.length;
        if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') nextIndex = (index - 1 + tabs.length) % tabs.length;
        if (event.key === 'Home') nextIndex = 0;
        if (event.key === 'End') nextIndex = tabs.length - 1;
        activate(tabs[nextIndex].dataset.systemTarget, true);
      });
    });
  });

  const campaignKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  const currentParams = new URLSearchParams(window.location.search);
  const campaign = {};

  campaignKeys.forEach((key) => {
    const incoming = currentParams.get(key);
    if (incoming) {
      campaign[key] = incoming;
      try { sessionStorage.setItem(`zenith_${key}`, incoming); } catch (_) { /* storage is optional */ }
      return;
    }
    try {
      const stored = sessionStorage.getItem(`zenith_${key}`);
      if (stored) campaign[key] = stored;
    } catch (_) { /* storage is optional */ }
  });

  if (Object.keys(campaign).length) {
    document.querySelectorAll('a[href]').forEach((link) => {
      const raw = link.getAttribute('href');
      if (!raw || raw.startsWith('#') || raw.startsWith('tel:') || raw.startsWith('sms:') || raw.startsWith('mailto:')) return;
      try {
        const url = new URL(raw, window.location.href);
        if (url.origin !== window.location.origin) return;
        Object.entries(campaign).forEach(([key, value]) => {
          if (!url.searchParams.has(key)) url.searchParams.set(key, value);
        });
        link.href = url.href;
      } catch (_) { /* malformed links remain untouched */ }
    });
  }

  window.dataLayer = window.dataLayer || [];
  document.querySelectorAll('.track[data-event]').forEach((link) => {
    link.addEventListener('click', () => {
      window.dataLayer.push({
        event: 'lead_action',
        lead_action: link.dataset.event,
        page: document.body.dataset.page || 'unknown'
      });
    });
  });
})();
