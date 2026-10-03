/* casperboekee.com – klein beetje gedrag: menu, header, CTA-balk en het formulier. */
(function () {
  'use strict';
  var header = document.querySelector('.site-header');
  var menuBtn = document.querySelector('.menu-btn');
  var nav = document.getElementById('nav');

  /* Menu (mobiel) */
  function isOpen() { return !!(header && header.classList.contains('is-open')); }
  function setMenu(open) {
    if (!header || !menuBtn) return;
    var wasOpen = isOpen();
    header.classList.toggle('is-open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    var label = menuBtn.querySelector('.menu-btn__label');
    if (label) label.textContent = open ? menuBtn.dataset.close : menuBtn.dataset.open;
    document.documentElement.style.overflow = open ? 'hidden' : '';
    /* Toetsenbord: bij openen naar de eerste link, bij sluiten terug naar de menuknop */
    if (open && nav) {
      var first = nav.querySelector('a');
      if (first) first.focus();
    } else if (wasOpen && !open && nav && nav.contains(document.activeElement)) {
      menuBtn.focus();
    }
  }
  if (menuBtn) {
    menuBtn.addEventListener('click', function () {
      setMenu(!isOpen());
    });
    /* Tab vanaf de menuknop gaat weer naar het menu, zodat je er niet 'achter' terechtkomt */
    menuBtn.addEventListener('keydown', function (e) {
      if (e.key === 'Tab' && !e.shiftKey && isOpen() && nav) {
        var first = nav.querySelector('a');
        if (first) { e.preventDefault(); first.focus(); }
      }
    });
  }
  if (nav) {
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setMenu(false);
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && isOpen()) setMenu(false);
  });
  window.addEventListener('resize', function () {
    if (window.innerWidth >= 1100) setMenu(false);
  });

  /* Header-achtergrond en CTA-balk bij scrollen */
  var bar = document.querySelector('[data-cta-bar]');
  var quiet = false; // true zolang het formulier of de oranje band in beeld is
  function onScroll() {
    var y = window.scrollY || 0;
    if (header) header.classList.toggle('is-scrolled', y > 12);
    if (bar) bar.classList.toggle('is-visible', y > 520 && !quiet);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  if (bar && 'IntersectionObserver' in window) {
    var seen = new Set();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) seen.add(en.target); else seen.delete(en.target);
      });
      quiet = seen.size > 0;
      onScroll();
    }, { threshold: 0.05 });
    document.querySelectorAll('.contact__form, .cta-band, .site-footer').forEach(function (el) { io.observe(el); });
  }

  /* Formulier */
  var form = document.getElementById('intro-form');
  if (form) {
    var status = form.querySelector('.form__status');
    var button = form.querySelector('button[type="submit"]');
    function say(kind) {
      status.textContent = status.dataset[kind];
      status.hidden = false;
      status.classList.toggle('is-error', kind === 'error' || kind === 'invalid');
    }
    /* Markering weghalen zodra een veld alsnog is ingevuld */
    form.addEventListener('input', function (e) {
      var el = e.target;
      if (el.classList && el.classList.contains('is-invalid') && el.checkValidity()) {
        el.classList.remove('is-invalid');
        el.setAttribute('aria-invalid', 'false');
      }
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true;
      form.querySelectorAll('[required]').forEach(function (el) {
        var valid = el.checkValidity();
        el.classList.toggle('is-invalid', !valid);
        el.setAttribute('aria-invalid', valid ? 'false' : 'true');
        if (!valid && ok) { el.focus(); ok = false; }
      });
      if (!ok) { say('invalid'); return; }
      status.hidden = true;
      if (form.querySelector('[name="botcheck"]').checked) return;
      var key = form.dataset.key;
      if (!key) { say('demo'); return; }
      var data = {};
      new FormData(form).forEach(function (v, k) { if (k !== 'botcheck') data[k] = v; });
      button.disabled = true;
      button.textContent = button.dataset.sending;
      fetch(form.dataset.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(data)
      }).then(function (r) { return r.json(); }).then(function (res) {
        if (res && res.success) { form.reset(); say('success'); if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: 'intro-request', title: 'Intro request sent', event: true }); } else { say('error'); }
      }).catch(function () { say('error'); }).then(function () {
        button.disabled = false;
        button.textContent = button.dataset.label;
      });
    });
  }
})();
