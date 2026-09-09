/* Small, nonblocking event collection for the public website. */
(() => {
  'use strict';
  const hosts = new Set(['tegridydev.com', 'www.tegridydev.com']);
  const campaigns = ['utm_source', 'utm_medium', 'utm_campaign'];
  const demos = new Map([
    ['/blog/agents/minecraft-time-with-astra/wildblock.html', 'wildblock'],
    ['/blog/model-interpretability/what-a-model-map-can-show/viewer.html', 'model-viewer'],
  ]);

  // The tracker strips all queries first. Add back only bounded campaign labels;
  // if this helper cannot load, collection remains free of query parameters.
  window.tegridyAnalyticsFilter = (type, payload) => {
    if (type === 'identify' || !hosts.has(window.location.hostname)) return false;
    const clean = { ...payload };
    delete clean.id;
    try {
      const url = new URL(clean.url, window.location.origin);
      const current = new URL(window.location.href);
      url.username = ''; url.password = ''; url.search = ''; url.hash = '';
      if (hosts.has(url.hostname) && url.pathname === current.pathname) {
        for (const key of campaigns) {
          const value = current.searchParams.get(key);
          if (value && /^[a-zA-Z0-9_ .-]{1,80}$/.test(value)) url.searchParams.set(key, value);
        }
      }
      clean.url = url.href;
      if (clean.referrer) {
        const referrer = new URL(clean.referrer, window.location.origin);
        referrer.username = ''; referrer.password = ''; referrer.search = ''; referrer.hash = '';
        clean.referrer = referrer.href;
      }
      return clean;
    } catch { return false; }
  };

  function track(name, data) {
    if (!hosts.has(window.location.hostname)) return;
    // Never delay navigation or require analytics to be available for a control.
    try { Promise.resolve(window.umami?.track(name, data)).catch(() => {}); } catch {}
  }

  function onClick(event) {
    if (event.type === 'auxclick' ? event.button !== 1 : event.button !== 0) return;
    const target = event.target?.closest?.('a[href], [data-copy-contact]');
    if (!target || target.hasAttribute('data-umami-event')) return;
    if (target.hasAttribute('data-copy-contact')) {
      track('contact-click', { method: 'copy' }); return;
    }
    let url;
    try { url = new URL(target.getAttribute('href'), window.location.href); } catch { return; }
    if (url.protocol === 'mailto:') {
      track('contact-click', { method: 'email' }); return;
    }
    if (!['https:', 'http:'].includes(url.protocol)) return;
    if (hosts.has(url.hostname) && demos.has(url.pathname)) {
      track('project-demo', { project: demos.get(url.pathname) }); return;
    }
    // Resource files are outside the click taxonomy.
    if (target.hasAttribute('download') || /\.(pdf|docx|zip|csv|md|epub|gz|tar)$/i.test(url.pathname)) return;
    if (!hosts.has(url.hostname)) track('outbound-link-click', { domain: url.hostname });
  }
  document.addEventListener('click', onClick, { passive: true });
  document.addEventListener('auxclick', onClick, { passive: true });
  document.addEventListener('submit', event => {
    // The contact handler hides the form only after its local check succeeds.
    if (event.target?.matches?.('[data-contact-check]') && event.target.hidden) {
      track('contact-click', { method: 'reveal' });
    }
  }, { passive: true });
})();
