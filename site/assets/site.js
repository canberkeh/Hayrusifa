// Hayru Şifa — arayüz etkileşimleri
(function () {
  // mobil menü
  var tgl = document.querySelector('.nav-tgl');
  var nav = document.getElementById('nav');
  if (tgl && nav) {
    tgl.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      tgl.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // tüm yazılar: arama + kategori süzme
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
