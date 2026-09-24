(function() {
  var cfg = window.ARABALAR_CFG;
  if (!cfg) return;

  var msMap  = cfg.msMap;
  var fMarka = document.getElementById('f_marka');
  var fSeri  = document.getElementById('f_seri');
  var fModel = document.getElementById('f_model');
  if (!fMarka) return;

  function buildOptions(sel, items, secili) {
    sel.innerHTML = '<option value="">Tümü</option>';
    items.forEach(function(v) {
      var o = document.createElement('option');
      o.value = o.textContent = v;
      if (v === secili) o.selected = true;
      sel.appendChild(o);
    });
    if (typeof CS !== 'undefined') CS.refresh(sel);
  }

  var initMarka = fMarka.value;
  var initSeri  = cfg.initSeri;
  var initModel = cfg.initModel;
  if (initMarka && msMap[initMarka]) {
    buildOptions(fSeri, Object.keys(msMap[initMarka]), initSeri);
    if (initSeri && msMap[initMarka][initSeri]) {
      buildOptions(fModel, msMap[initMarka][initSeri], initModel);
    }
  }

  fMarka.addEventListener('change', function() {
    var seriler = this.value && msMap[this.value] ? Object.keys(msMap[this.value]) : [];
    buildOptions(fSeri, seriler, '');
    buildOptions(fModel, [], '');
  });

  fSeri.addEventListener('change', function() {
    var marka    = fMarka.value;
    var modeller = (marka && msMap[marka] && this.value && msMap[marka][this.value]) ? msMap[marka][this.value] : [];
    buildOptions(fModel, modeller, '');
  });
})();

document.querySelectorAll('.fav-btn').forEach(function(btn) {
  btn.addEventListener('click', function(e) {
    e.preventDefault();
    var ilanId = this.dataset.ilan;
    var cfg = window.ARABALAR_CFG;
    fetch(cfg.favoriUrl, {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'X-CSRFToken': cfg.csrfToken},
      body: JSON.stringify({ilan_id: ilanId})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
      var icon = btn.querySelector('i');
      icon.className = d.favori ? 'bi bi-heart-fill' : 'bi bi-heart';
      btn.style.color = d.favori ? '#ef4444' : '';
    });
  });
});

(function() {
  try {
    var liste = JSON.parse(localStorage.getItem('son_goruntulenenler') || '[]');
    if (!liste.length) return;
    var container = document.getElementById('son-goruntulenenler-liste');
    if (!container) return;
    liste.forEach(function(ilan) {
      var card = document.createElement('a');
      card.href = '/ilan/' + ilan.slug + '/';
      card.className = 'text-decoration-none flex-shrink-0';
      card.style.cssText = 'width:120px';
      card.innerHTML =
        '<div style="background:var(--card-bg);border:1px solid var(--gray-200);border-radius:var(--radius-sm);overflow:hidden">' +
        (ilan.foto ? '<img src="' + ilan.foto + '" style="width:100%;height:64px;object-fit:cover" loading="lazy">' :
          '<div style="width:100%;height:64px;background:var(--gray-100);display:flex;align-items:center;justify-content:center"><i class="bi bi-car-front" style="color:var(--gray-300)"></i></div>') +
        '<div style="padding:.35rem .5rem">' +
        '<div style="font-size:.68rem;font-weight:600;color:var(--navy);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">' + ilan.marka + ' ' + ilan.yil + '</div>' +
        '<div style="font-size:.7rem;color:var(--blue);font-weight:700">' + ilan.fiyat + ' TL</div>' +
        '</div></div>';
      container.appendChild(card);
    });
    var wrap = document.getElementById('son-goruntulenenler-wrap');
    if (wrap) wrap.style.display = 'block';
  } catch(e) {}
})();
