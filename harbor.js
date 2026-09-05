
(()=>{
  const cleanTrackingToken = (value) => String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9._-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 48);

  const readAttribution = () => {
    const params = new URLSearchParams(window.location.search);
    const taggedSource = cleanTrackingToken(params.get("utm_source"));
    const medium = cleanTrackingToken(params.get("utm_medium"));
    const campaign = cleanTrackingToken(params.get("utm_campaign"));
    const partner = cleanTrackingToken(params.get("ref") || params.get("utm_content"));
    let referrer = "";

    if (!taggedSource && document.referrer) {
      try {
        const referrerHost = new URL(document.referrer).hostname.replace(/^www\./, "");
        if (referrerHost && referrerHost !== window.location.hostname) {
          referrer = cleanTrackingToken(referrerHost);
        }
      } catch (_) {
        referrer = "";
      }
    }

    return {
      source: taggedSource || referrer || partner || "direct",
      medium,
      campaign,
      partner: partner && partner !== taggedSource ? partner : "",
    };
  };

  const attribution = readAttribution();

  const trackEvent = (name, parameters = {}) => {
    if (typeof window.gtag !== "function") return false;
    window.gtag("event", name, parameters);
    return true;
  };


  window.ZenithAnalytics={trackEvent};

  const form=document.getElementById('request-form');
  document.getElementById('prepare-text').disabled=false;
  const service=document.getElementById('service');
  const draft=document.getElementById('draft');
  const status=document.getElementById('form-status');
  const preview=document.getElementById('message-preview');
  const link=document.getElementById('sms-link');
  const read=id=>document.getElementById(id).value.trim();
  const motion=()=>matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth';
  function resetDraft(){draft.hidden=true;status.textContent='';preview.value='';link.href='sms:+13053066391';}
  window.buildZenithMessage=()=>{
    const lines=['Hi Greg — I’d like to discuss marine electronics service.','Service: '+read('service'),'Boat location: '+read('location')];
    if(read('vessel')) lines.push('Boat / equipment: '+read('vessel'));
    lines.push('Request: '+read('details'));
    const source=[attribution.source,attribution.medium,attribution.campaign,attribution.partner].filter(Boolean).join(' / ');
    lines.push('Lead source: '+(source||'direct'));
    return lines.join('\n');
  };
  document.querySelectorAll('[data-select-service]').forEach(button=>button.addEventListener('click',event=>{
    event.preventDefault();
    service.value=button.dataset.selectService;
    trackEvent("service_select",{service_name:service.value});
    resetDraft();
    document.getElementById('contact').scrollIntoView({behavior:motion(),block:'start'});
    service.focus({preventScroll:true});
  }));
  form.addEventListener('input',event=>{event.target.setCustomValidity?.('');resetDraft();});
  form.addEventListener('change',event=>{resetDraft();if(event.target===service) trackEvent("service_select",{service_name:service.value});});
  form.addEventListener('submit',event=>{
    event.preventDefault();
    ['location','details'].forEach(id=>{const field=document.getElementById(id);field.setCustomValidity(field.value.trim()?'':'Please add a short detail here.');});
    if(!form.reportValidity()) return;
    const message=window.buildZenithMessage();
    preview.value=message;
    // iOS uses &body; other handlers conventionally use ?body.
    const apple=/iPad|iPhone|iPod/.test(navigator.userAgent)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
    link.href='sms:+13053066391'+(apple?'&':'?')+'body='+encodeURIComponent(message);
    draft.hidden=false;
    status.textContent='Message prepared on this device. Nothing has been sent.';
    link.focus({preventScroll:true});
    draft.scrollIntoView({behavior:motion(),block:'nearest'});
  });

  window.ZenithBooking={attribution:()=>({...attribution}),buildMessage:window.buildZenithMessage};
  document.querySelectorAll('a[href^="tel:"]').forEach(a=>a.addEventListener('click',()=>trackEvent("call_click",{link_text:a.textContent.trim(),lead_source:attribution.source})));
  document.querySelectorAll('a[href^="sms:"]').forEach(a=>a.addEventListener('click',()=>trackEvent("sms_open",{service_name:a.id==='sms-link'?service.value:'direct_text',lead_source:attribution.source})));
  // Preserve only bounded campaign tokens when navigating to existing service pages.
  document.querySelectorAll('.service-page-link').forEach(a=>{
    const destination=new URL(a.getAttribute('href'),location.href);
    const current=new URLSearchParams(location.search);
    ['utm_source','utm_medium','utm_campaign','ref','utm_content'].forEach(key=>{
      const value=cleanTrackingToken(current.get(key));
      if(value) destination.searchParams.set(key,value);
    });
    a.href=destination.href;
  });
})();
