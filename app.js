(() => {
  const PHONE = "+13053066391";
  const header = document.querySelector("[data-header]");
  const form = document.querySelector("[data-booking-form]");
  const serviceSelect = document.querySelector("#service");
  const status = document.querySelector("[data-form-status]");
  const morphHero = document.querySelector("[data-morph-hero]");
  const morphSticky = document.querySelector("[data-morph-sticky]");
  const morphStage = document.querySelector("[data-morph-stage]");
  const mobileMotion = window.matchMedia("(max-width: 820px)");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  let animationFrame = 0;
  let currentProgress = 0;

  const clamp = (value, minimum = 0, maximum = 1) => Math.min(maximum, Math.max(minimum, value));

  const setHeaderState = () => {
    header?.classList.toggle("is-scrolled", window.scrollY > 12);
  };

  const renderMorph = (value) => {
    if (!morphStage) return 0;

    const progress = clamp(Number(value) || 0);
    currentProgress = progress;
    morphStage.style.setProperty("--reveal", `${(progress * 100).toFixed(2)}%`);
    morphStage.style.setProperty("--turn", `${(-8 * (1 - progress)).toFixed(2)}deg`);
    morphStage.style.setProperty("--morph-scale", `${(1.14 - (0.14 * progress)).toFixed(4)}`);
    morphStage.style.setProperty("--shift", "0%");
    morphStage.style.setProperty("--scan-opacity", Math.min(1, progress * 12, (1 - progress) * 12).toFixed(3));
    morphStage.dataset.morphProgress = progress.toFixed(3);
    morphStage.dataset.morphState = progress < 0.08 ? "blueprint" : progress > 0.92 ? "vessel" : "transforming";
    return progress;
  };

  const updateMorph = () => {
    if (!morphHero || !morphSticky || !morphStage) return;

    if (reducedMotion.matches) {
      renderMorph(1);
      return;
    }

    if (mobileMotion.matches) {
      const stageRect = morphStage.getBoundingClientRect();
      const start = window.innerHeight * 0.78;
      const end = window.innerHeight * 0.18;
      renderMorph((start - stageRect.top) / Math.max(1, start - end));
      return;
    }

    const heroRect = morphHero.getBoundingClientRect();
    const headerHeight = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--header-height")) || 0;
    const travel = Math.max(1, morphHero.offsetHeight - morphSticky.offsetHeight);
    renderMorph((headerHeight - heroRect.top) / travel);
  };

  const updateFrame = () => {
    animationFrame = 0;
    setHeaderState();
    updateMorph();
  };

  const requestUpdate = () => {
    if (!animationFrame) animationFrame = window.requestAnimationFrame(updateFrame);
  };

  const buildMessage = ({ service, location, vessel, date, details }) => [
    "Zenith service request",
    `Service: ${service}`,
    `Boat location: ${location}`,
    `Vessel / equipment: ${vessel}`,
    `Preferred date: ${date || "Flexible"}`,
    `Request: ${details}`,
    "I can send clear photos.",
  ].join("\n");

  const buildHref = (data) => `sms:${PHONE}?body=${encodeURIComponent(buildMessage(data))}`;

  window.ZenithBooking = { buildMessage, buildHref };
  window.ZenithMorph = {
    render: renderMorph,
    update: updateMorph,
    progress: () => currentProgress,
  };

  document.querySelectorAll("[data-service]").forEach((button) => {
    button.addEventListener("click", () => {
      if (serviceSelect) {
        serviceSelect.value = button.dataset.service || "";
      }
      document.querySelector("#book")?.scrollIntoView({ behavior: "smooth", block: "start" });
      window.setTimeout(() => serviceSelect?.focus({ preventScroll: true }), 450);
    });
  });

  form?.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!form.reportValidity()) {
      status.textContent = "Complete the required fields first.";
      return;
    }

    const data = Object.fromEntries(new FormData(form).entries());
    status.textContent = "Opening your prepared text message…";
    window.location.href = buildHref(data);
  });

  document.querySelectorAll("[data-year]").forEach((node) => {
    node.textContent = new Date().getFullYear();
  });

  window.addEventListener("scroll", requestUpdate, { passive: true });
  window.addEventListener("resize", requestUpdate, { passive: true });
  mobileMotion.addEventListener?.("change", requestUpdate);
  reducedMotion.addEventListener?.("change", requestUpdate);
  updateFrame();
})();
