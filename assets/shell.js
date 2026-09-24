/* Оболочка: тема, мобильное меню, подсветка текущего подраздела. */
(function () {
  'use strict';

  // ── тема ──────────────────────────────────────────────────────────────────
  var KEY = 'jobescape-present-theme';
  var root = document.documentElement;

  function label() {
    var t = root.getAttribute('data-theme');
    return t === 'dark' ? 'Тёмная' : t === 'light' ? 'Светлая' : 'Система';
  }
  function paint() {
    [].forEach.call(document.querySelectorAll('[data-theme-toggle]'), function (b) {
      b.textContent = label();
      b.setAttribute('aria-label', 'Тема: ' + label().toLowerCase());
    });
  }
  try {
    var saved = localStorage.getItem(KEY);
    if (saved === 'dark' || saved === 'light') root.setAttribute('data-theme', saved);
  } catch (e) { /* приватный режим — просто остаёмся на системной */ }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('[data-theme-toggle]');
    if (!btn) return;
    var order = ['', 'light', 'dark'];
    var next = order[(order.indexOf(root.getAttribute('data-theme') || '') + 1) % 3];
    if (next) root.setAttribute('data-theme', next); else root.removeAttribute('data-theme');
    try { next ? localStorage.setItem(KEY, next) : localStorage.removeItem(KEY); } catch (e2) {}
    paint();
  });
  paint();

  // ── мобильное меню ────────────────────────────────────────────────────────
  var body = document.body;
  document.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('[data-nav-toggle]')) {
      body.classList.toggle('nav-open');
      return;
    }
    if (e.target.classList && e.target.classList.contains('scrim')) body.classList.remove('nav-open');
    if (e.target.closest && e.target.closest('.subnav a, .navlink')) body.classList.remove('nav-open');
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') body.classList.remove('nav-open');
  });

  // ── подсветка подраздела при прокрутке ────────────────────────────────────
  var links = [].slice.call(document.querySelectorAll('.subnav a[href^="#"]'));
  if (!links.length) return;

  var targets = links
    .map(function (a) { return { a: a, el: document.getElementById(a.getAttribute('href').slice(1)) }; })
    .filter(function (p) { return p.el; });
  if (!targets.length) return;

  var current = null;
  function sync() {
    var line = window.scrollY + window.innerHeight * 0.25;
    var hit = targets[0];
    for (var i = 0; i < targets.length; i++) {
      if (targets[i].el.offsetTop <= line) hit = targets[i];
    }
    if (hit === current) return;
    if (current) current.a.classList.remove('is-active');
    hit.a.classList.add('is-active');
    current = hit;
  }

  var queued = false;
  window.addEventListener('scroll', function () {
    if (queued) return;
    queued = true;
    requestAnimationFrame(function () { queued = false; sync(); });
  }, { passive: true });
  window.addEventListener('resize', sync, { passive: true });
  sync();
})();
