// Hayru Şifa — arayüz etkileşimleri
(function () {
  var MOBILE = function () { return window.matchMedia('(max-width:720px)').matches; };

  // ---- mobil menü -------------------------------------------------------
  var tgl = document.querySelector('.nav-tgl');
  var nav = document.getElementById('nav');

  function closeMenu() {
    if (!nav) return;
    nav.classList.remove('open');
    document.body.classList.remove('nav-open');
    if (tgl) tgl.setAttribute('aria-expanded', 'false');
    var dd = nav.querySelector('.has-dd.sub-open');
    if (dd) dd.classList.remove('sub-open');
  }

  if (tgl && nav) {
    tgl.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      document.body.classList.toggle('nav-open', open);
      tgl.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (!open) closeMenu();
    });

    // alt menü (Tedavi Yöntemleri) — mobilde dokununca aç/kapat
    var ddParent = nav.querySelector('.has-dd');
    if (ddParent) {
      var ddLink = ddParent.querySelector(':scope > a');
      if (ddLink) {
        ddLink.addEventListener('click', function (ev) {
          if (MOBILE()) {
            ev.preventDefault();
            ddParent.classList.toggle('sub-open');
          }
        });
      }
    }

    // menü içindeki gerçek bir bağlantıya dokununca menüyü kapat
    nav.addEventListener('click', function (ev) {
      var a = ev.target.closest('a');
      if (!a) return;
      if (a.closest('.has-dd') && a === a.closest('.has-dd').querySelector(':scope > a')) return; // alt menü başlığı
      closeMenu();
    });

    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') closeMenu();
    });
    window.addEventListener('resize', function () {
      if (!MOBILE()) closeMenu();
    });
  }

  // ---- scroll ile fade-in (reveal) ----------------------------------
  (function () {
    if (!('IntersectionObserver' in window)) return;
    if (window.matchMedia('(prefers-reduced-motion:reduce)').matches) return;

    var SEL = [
      '.band-head', '.mtiles > *', '.ctiles > *', '.cards > *', '.pills > .pill',
      '.strip-grid > *', '.cta-in > *', '.hero-copy > *',
      '.subsec', '.side-card', '.ci-row', '.map-card',
      '.post-feat', '.prose > h2', '.post-cta', '.pn-wrap',
      '.page-head > *', '.linklist'
    ].join(',');

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add('in');
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -6% 0px' });

    var vh = window.innerHeight || document.documentElement.clientHeight;
    var main = document.getElementById('main') || document;
    var perParent = new WeakMap();
    Array.prototype.forEach.call(main.querySelectorAll(SEL), function (el) {
      // ekranda görünen (above-the-fold) öğeler animasyonsuz kalsın
      if (el.getBoundingClientRect().top < vh * 0.88) return;
      el.classList.add('reveal');
      // aynı ebeveyn içinde hafif kademeli gecikme
      var p = el.parentNode;
      var i = perParent.get(p) || 0;
      perParent.set(p, i + 1);
      if (i > 0) el.style.transitionDelay = Math.min(i * 70, 350) + 'ms';
      io.observe(el);
    });
  })();

  // ---- tüm yazılar: arama + kategori süzme ----------------------------
  var q = document.getElementById('q');
  var catf = document.getElementById('catf');
  var list = document.getElementById('plist');
  var nores = document.getElementById('nores');
  if (list && (q || catf)) {
    var rows = Array.prototype.slice.call(list.children);
    function apply() {
      var term = (q && q.value || '').trim().toLowerCase();
      var cat = (catf && catf.value) || '';
      var shown = 0;
      rows.forEach(function (li) {
        var okT = !term || li.getAttribute('data-t').indexOf(term) > -1;
        var okC = !cat || li.getAttribute('data-cat') === cat;
        var vis = okT && okC;
        li.hidden = !vis;
        if (vis) shown++;
      });
      if (nores) nores.hidden = shown > 0;
    }
    if (q) q.addEventListener('input', apply);
    if (catf) catf.addEventListener('change', apply);
  }
})();
