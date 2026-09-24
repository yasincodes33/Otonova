(function() {
  var cfg = window.ANASAYFA_CFG;
  var msMap = (cfg && cfg.msMap) ? cfg.msMap : {};
  var markalar = Object.keys(msMap).sort();

  /* ── Hero search marka/seri cascade (Item 5) ── */
  var heroMarka = document.getElementById('hero_marka');
  var heroSeri  = document.getElementById('hero_seri');
  if (heroMarka) {
    markalar.forEach(function(m) {
      heroMarka.insertAdjacentHTML('beforeend', '<option value="' + m + '">' + m + '</option>');
    });
    if (window.CS) CS.refresh(heroMarka);

    heroMarka.addEventListener('change', function() {
      var seriler = msMap[this.value] || [];
      heroSeri.innerHTML = '<option value="">Tüm seriler</option>' +
        seriler.map(function(s) { return '<option value="' + s + '">' + s + '</option>'; }).join('');
      if (window.CS) CS.refresh(heroSeri);
    });
  }

  /* ── Hero search submit ── */
  var form = document.getElementById('hero-search');
  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      var params = new URLSearchParams();
      ['marka','seri','sehir','vites','yakit','yil_min','km_max'].forEach(function(name) {
        var el = form.querySelector('[name="' + name + '"]');
        if (el && el.value.trim()) params.set(name, el.value.trim());
      });
      var fiyatEl = form.querySelector('[name="fiyat_aralik"]');
      if (fiyatEl && fiyatEl.value) {
        var parts = fiyatEl.value.split('-');
        if (parts[0]) params.set('fiyat_min', parts[0]);
        if (parts[1]) params.set('fiyat_max', parts[1]);
      }
      window.location.href = form.action + '?' + params.toString();
    });
  }

  /* ── AI mini form marka/seri cascade + navigate (Item 6) ── */
  var aiMarka = document.getElementById('ai_marka');
  var aiSeri  = document.getElementById('ai_seri');
  var aiYil   = document.getElementById('ai_yil');

  if (aiMarka) {
    markalar.forEach(function(m) {
      aiMarka.insertAdjacentHTML('beforeend', '<option value="' + m + '">' + m + '</option>');
    });
    aiMarka.addEventListener('change', function() {
      var seriler = msMap[this.value] || [];
      aiSeri.innerHTML = '<option value="">Seçin...</option>' +
        seriler.map(function(s) { return '<option value="' + s + '">' + s + '</option>'; }).join('');
    });
  }

  if (aiYil) {
    var opts = '';
    for (var y = 2026; y >= 2005; y--) opts += '<option value="' + y + '">' + y + '</option>';
    aiYil.innerHTML = opts;
  }

  var tahminBtn = document.getElementById('ai-tahmin-btn');
  if (tahminBtn) {
    tahminBtn.addEventListener('click', function() {
      var marka = aiMarka ? aiMarka.value : '';
      var seri  = aiSeri  ? aiSeri.value  : '';
      var yil   = aiYil   ? aiYil.value   : '';
      var kmEl  = document.getElementById('ai_km');
      var km    = kmEl    ? kmEl.value     : '';
      var params = new URLSearchParams();
      if (marka) params.set('marka', marka);
      if (seri)  params.set('seri',  seri);
      if (yil)   params.set('yil',   yil);
      if (km)    params.set('km',    km);
      var qs = params.toString();
      window.location.href = '/tahmin/' + (qs ? '?' + qs : '');
    });
  }
})();
