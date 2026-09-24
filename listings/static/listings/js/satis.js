var _seciliFotolar = new DataTransfer();

/* ── Tramer auto-compute (Item 15) ── */
var _TRAMER_LABEL = { bilinmiyor: 'Bilinmiyor', yok: 'Yok', dusuk: 'Düşük', orta: 'Orta', yuksek: 'Yüksek' };
var _TRAMER_STYLE = {
  bilinmiyor: 'background:#e2e8f0;color:#475569',
  yok:        'background:#dcfce7;color:#166534',
  dusuk:      'background:#fef9c3;color:#854d0e',
  orta:       'background:#fed7aa;color:#9a3412',
  yuksek:     'background:#fee2e2;color:#991b1b'
};
function _tramiKategori(tutar) {
  if (tutar === '' || tutar === null) return 'bilinmiyor';
  tutar = parseFloat(tutar);
  if (isNaN(tutar)) return 'bilinmiyor';
  if (tutar === 0)   return 'yok';
  if (tutar <= 5000) return 'dusuk';
  if (tutar <= 25000) return 'orta';
  return 'yuksek';
}
function _tramiGuncelle() {
  var inp    = document.getElementById('s_tramer_tutari');
  var hidden = document.getElementById('s_tramer_kategori');
  var badge  = document.getElementById('tramer-badge');
  if (!inp || !hidden || !badge) return;
  var kat = _tramiKategori(inp.value);
  hidden.value = kat;
  badge.textContent = _TRAMER_LABEL[kat];
  badge.style.cssText = 'padding:4px 14px;border-radius:20px;font-size:.72rem;font-weight:700;white-space:nowrap;' + _TRAMER_STYLE[kat];
}
document.addEventListener('DOMContentLoaded', function() {
  var tramerInp = document.getElementById('s_tramer_tutari');
  if (tramerInp) {
    tramerInp.addEventListener('input', _tramiGuncelle);
    tramerInp.addEventListener('change', _tramiGuncelle);
    _tramiGuncelle();
  }

  /* ── Photo required (Item 16) ── */
  var satisForm = document.querySelector('form[enctype="multipart/form-data"]');
  if (satisForm) {
    satisForm.addEventListener('submit', function(e) {
      var uyari = document.getElementById('foto-zorunlu-uyari');
      if (_seciliFotolar.files.length === 0) {
        e.preventDefault();
        if (uyari) uyari.style.display = 'block';
        var dropZone = document.getElementById('drop-zone');
        if (dropZone) { dropZone.style.borderColor = '#ef4444'; dropZone.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
      } else {
        if (uyari) uyari.style.display = 'none';
      }
    });
  }
});

function fotoGuncelle(files) {
  Array.from(files).forEach(function(f) { try { _seciliFotolar.items.add(f); } catch(e) {} });
  document.getElementById('foto-input').files = _seciliFotolar.files;
  _fotoOnizle();
}

function _fotoOnizle() {
  var files = _seciliFotolar.files;
  var grid  = document.getElementById('foto-grid');
  var prev  = document.getElementById('foto-preview');
  document.getElementById('foto-count').textContent = files.length;
  grid.innerHTML = '';
  if (files.length === 0) { prev.style.display = 'none'; return; }
  prev.style.display = 'block';
  Array.from(files).forEach(function(f, i) {
    var reader = new FileReader();
    reader.onload = function(e) {
      var wrap = document.createElement('div');
      wrap.style.cssText = 'position:relative;border-radius:8px;overflow:hidden;aspect-ratio:4/3;background:var(--gray-100)';
      var img = document.createElement('img');
      img.src = e.target.result;
      img.style.cssText = 'width:100%;height:100%;object-fit:cover';
      var badge = i === 0 ? '<span style="position:absolute;top:4px;left:4px;background:#2563eb;color:#fff;font-size:.6rem;font-weight:700;padding:2px 6px;border-radius:20px">KAPAK</span>' : '';
      var del = document.createElement('button');
      del.type = 'button';
      del.innerHTML = '<i class="bi bi-x"></i>';
      del.style.cssText = 'position:absolute;top:4px;right:4px;background:rgba(0,0,0,.55);color:#fff;border:none;border-radius:50%;width:22px;height:22px;font-size:.75rem;cursor:pointer;display:flex;align-items:center;justify-content:center;padding:0';
      (function(idx) {
        del.onclick = function(ev) { ev.stopPropagation(); _fotoSil(idx); };
      })(i);
      wrap.appendChild(img);
      if (i === 0) wrap.insertAdjacentHTML('beforeend', badge);
      wrap.appendChild(del);
      grid.appendChild(wrap);
    };
    reader.readAsDataURL(f);
  });
}

function _fotoSil(idx) {
  var dt = new DataTransfer();
  Array.from(_seciliFotolar.files).forEach(function(f, i) { if (i !== idx) dt.items.add(f); });
  _seciliFotolar = dt;
  document.getElementById('foto-input').files = _seciliFotolar.files;
  _fotoOnizle();
}

var fotoInp = document.getElementById('foto-input');
if (fotoInp) {
  fotoInp.addEventListener('change', function() {
    _seciliFotolar = new DataTransfer();
    fotoGuncelle(this.files);
  });
}

function fotoDropOver(e) {
  e.preventDefault();
  document.getElementById('drop-zone').style.borderColor = 'var(--blue)';
  document.getElementById('drop-zone').style.background  = 'var(--blue-light)';
}
function fotoDropLeave(e) {
  e.preventDefault();
  document.getElementById('drop-zone').style.borderColor = 'var(--gray-200)';
  document.getElementById('drop-zone').style.background  = 'var(--gray-50)';
}
function fotoDrop(e) {
  e.preventDefault();
  fotoDropLeave(e);
  fotoGuncelle(e.dataTransfer.files);
}

(function() {
  var cfg = window.SATIS_CFG;
  if (!cfg) return;

  var _msMap   = cfg.msMap;
  var _msmMap  = cfg.msmMap;
  var _msmkMap = cfg.msmkMap;
  var _tumKasa = cfg.tumKasa;

  function _s_kasaGuncelle(marka, seri, model) {
    var kasaSel = document.getElementById('s_kasa_tipi');
    if (!kasaSel) return;
    var kasalar = (marka && seri && model && _msmkMap[marka] && _msmkMap[marka][seri] && _msmkMap[marka][seri][model])
      ? _msmkMap[marka][seri][model] : _tumKasa;
    var secili = kasaSel.value;
    kasaSel.innerHTML = kasalar.map(function(k) {
      return '<option value="' + k + '"' + (k === secili ? ' selected' : '') + '>' + k + '</option>';
    }).join('');
  }

  var sMarka = document.getElementById('s_marka');
  if (sMarka) {
    sMarka.addEventListener('change', function() {
      var seriSel  = document.getElementById('s_seri');
      var modelSel = document.getElementById('s_model');
      var seriler  = _msMap[this.value] || [];
      seriSel.innerHTML  = '<option value="">Seçin...</option>' + seriler.map(function(s) { return '<option>' + s + '</option>'; }).join('');
      modelSel.innerHTML = '<option value="">Önce seri seçin</option>';
      _s_kasaGuncelle('', '', '');
    });
  }

  var sSeri = document.getElementById('s_seri');
  if (sSeri) {
    sSeri.addEventListener('change', function() {
      var marka    = document.getElementById('s_marka').value;
      var modelSel = document.getElementById('s_model');
      var modeller = (_msmMap[marka] && _msmMap[marka][this.value]) || [];
      modelSel.innerHTML = '<option value="">Seçin...</option>' + modeller.map(function(m) { return '<option>' + m + '</option>'; }).join('');
      _s_kasaGuncelle('', '', '');
    });
  }

  var sModel = document.getElementById('s_model');
  if (sModel) {
    sModel.addEventListener('change', function() {
      var marka = document.getElementById('s_marka').value;
      var seri  = document.getElementById('s_seri').value;
      _s_kasaGuncelle(marka, seri, this.value);
    });
  }

  if (cfg.formMarka) {
    var marka = cfg.formMarka;
    var seri  = cfg.formSeri;
    var model = cfg.formModel;
    var kasa  = cfg.formKasa;

    sMarka.value = marka;

    var seriler = _msMap[marka] || [];
    document.getElementById('s_seri').innerHTML =
      '<option value="">Seçin...</option>' +
      seriler.map(function(s) { return '<option' + (s === seri ? ' selected' : '') + '>' + s + '</option>'; }).join('');

    var modeller = (_msmMap[marka] && _msmMap[marka][seri]) || [];
    document.getElementById('s_model').innerHTML =
      '<option value="">Seçin...</option>' +
      modeller.map(function(m) { return '<option' + (m === model ? ' selected' : '') + '>' + m + '</option>'; }).join('');

    _s_kasaGuncelle(marka, seri, model);
    if (kasa) {
      var kasaSel = document.getElementById('s_kasa_tipi');
      if (kasaSel) kasaSel.value = kasa;
    }
  }
})();
