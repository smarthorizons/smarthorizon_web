/* Smart Horizon — site behaviour
   1. Language switching (EN / AR + RTL), persisted
   2. Mobile navigation
   3. GA4, loaded only after explicit consent
   No dependencies, no build step. */

(function () {
  'use strict';

  /* ---------------------------------------------------------------
     1. Language
     Both languages are present in the HTML; CSS hides the inactive
     one. This only flips the lang/dir attributes on <html>.
  ---------------------------------------------------------------- */
  var STORE_KEY = 'sh-lang';

  function preferredLang() {
    try {
      var saved = localStorage.getItem(STORE_KEY);
      if (saved === 'ar' || saved === 'en') return saved;
    } catch (e) { /* private mode — fall through */ }
    var nav = (navigator.languages || [navigator.language || 'en']).join(',');
    return /\bar\b|^ar|,ar/i.test(nav) ? 'ar' : 'en';
  }

  function applyLang(lang) {
    var html = document.documentElement;
    html.setAttribute('lang', lang);
    html.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');

    document.querySelectorAll('[data-lang-toggle]').forEach(function (btn) {
      // The button always offers the *other* language.
      btn.textContent = lang === 'ar' ? 'English' : 'العربية';
      btn.setAttribute('lang', lang === 'ar' ? 'en' : 'ar');
      btn.setAttribute(
        'aria-label',
        lang === 'ar' ? 'Switch to English' : 'التبديل إلى العربية'
      );
    });

    // Keep the document title in step with the active language.
    var t = document.querySelector('title[data-title-' + lang + ']');
    if (t) document.title = t.getAttribute('data-title-' + lang);
  }

  function setLang(lang) {
    applyLang(lang);
    try { localStorage.setItem(STORE_KEY, lang); } catch (e) { /* ignore */ }
  }

  applyLang(preferredLang());

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-lang-toggle]');
    if (!btn) return;
    e.preventDefault();
    setLang(document.documentElement.getAttribute('lang') === 'ar' ? 'en' : 'ar');
  });

  /* ---------------------------------------------------------------
     2. Mobile navigation
  ---------------------------------------------------------------- */
  var navToggle = document.querySelector('[data-nav-toggle]');
  var nav = document.getElementById('site-nav');

  function syncNav() {
    if (!nav || !navToggle) return;
    if (window.innerWidth > 860) {
      nav.hidden = false;
      navToggle.setAttribute('aria-expanded', 'false');
    } else if (navToggle.getAttribute('aria-expanded') !== 'true') {
      nav.hidden = true;
    }
  }

  if (navToggle && nav) {
    navToggle.addEventListener('click', function () {
      var open = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', String(!open));
      nav.hidden = open;
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A' && window.innerWidth <= 860) {
        navToggle.setAttribute('aria-expanded', 'false');
        nav.hidden = true;
      }
    });
    window.addEventListener('resize', syncNav);
    syncNav();
  }

  /* ---------------------------------------------------------------
     3. Analytics (GA4) — consent-gated
     GA4 sets cookies, so under GDPR it must not run until the visitor
     agrees. Nothing is loaded unless consent === 'granted'.
     Replace SH_GA_ID below with the real G-XXXXXXXXXX measurement ID.
  ---------------------------------------------------------------- */
  var GA_ID = window.SH_GA_ID || '';           // set in each page's <head>
  var CONSENT_KEY = 'sh-analytics-consent';

  function consentState() {
    try { return localStorage.getItem(CONSENT_KEY); } catch (e) { return null; }
  }

  function loadGA() {
    if (!GA_ID || /^G-X+$/i.test(GA_ID) || window.__shGaLoaded) return;
    window.__shGaLoaded = true;

    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_ID);
    document.head.appendChild(s);

    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('consent', 'default', {
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      analytics_storage: 'granted'
    });
    window.gtag('config', GA_ID, { anonymize_ip: true });
  }

  function buildBanner() {
    var ar = document.documentElement.getAttribute('lang') === 'ar';
    var el = document.createElement('div');
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', ar ? 'إشعار ملفات تعريف الارتباط' : 'Cookie notice');
    el.style.cssText =
      'position:fixed;inset-block-end:0;inset-inline:0;z-index:300;background:#fff;' +
      'border-block-start:1px solid #E3E8EF;box-shadow:0 -6px 24px rgba(16,23,32,.10);' +
      'padding:16px 22px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;' +
      'justify-content:center;font-size:.93rem;color:#33404F';

    var text = document.createElement('p');
    text.style.cssText = 'margin:0;max-width:60ch';
    text.innerHTML = ar
      ? 'نستخدم تحليلات Google لفهم كيفية استخدام الموقع. لا نشغّلها إلا بموافقتك. ' +
        '<a href="/legal/">سياسة الخصوصية</a>'
      : 'We use Google Analytics to understand how this site is used. It only runs if you agree. ' +
        '<a href="/legal/">Privacy</a>';

    function mkBtn(label, primary) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = label;
      b.style.cssText =
        'font:inherit;font-weight:700;padding:9px 20px;border-radius:9px;cursor:pointer;border:1.5px solid ' +
        (primary ? '#0A63D8;background:#0A63D8;color:#fff' : '#E3E8EF;background:#fff;color:#33404F');
      return b;
    }

    var accept  = mkBtn(ar ? 'أوافق'  : 'Accept',  true);
    var decline = mkBtn(ar ? 'أرفض'   : 'Decline', false);

    function close(value) {
      try { localStorage.setItem(CONSENT_KEY, value); } catch (e) { /* ignore */ }
      el.remove();
      if (value === 'granted') loadGA();
    }

    accept.addEventListener('click', function () { close('granted'); });
    decline.addEventListener('click', function () { close('denied'); });

    el.append(text, accept, decline);
    document.body.appendChild(el);
  }

  if (GA_ID && !/^G-X+$/i.test(GA_ID)) {
    var state = consentState();
    if (state === 'granted') loadGA();
    else if (state !== 'denied') buildBanner();
  }
})();
