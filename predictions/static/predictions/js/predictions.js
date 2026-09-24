/* predictions.js  v10 */

/* ── Segment MAE tablosu ────────────────────────────────────────
   Modelin fiyat aralığına göre ortalama mutlak hatası (TL).
   Eğitim seti analizinden elde edilmiştir.
   ────────────────────────────────────────────────────────────── */
var SEGMENT_MAE = [
  { limit: 300000,    mae: 34289,  label: '0–300K' },
  { limit: 600000,    mae: 44427,  label: '300K–600K' },
  { limit: 900000,    mae: 57479,  label: '600K–900K' },
  { limit: 1200000,   mae: 75693,  label: '900K–1.2M' },
  { limit: 1500000,   mae: 87306,  label: '1.2M–1.5M' },
  { limit: 1800000,   mae: 113692, label: '1.5M–1.8M' },
  { limit: 2100000,   mae: 139870, label: '1.8M–2.1M' },
  { limit: 2400000,   mae: 208115, label: '2.1M–2.4M' },
  { limit: Infinity,  mae: 279303, label: '2.4M+' },
];

function getSegmentMAE(fiyat) {
  for (var i = 0; i < SEGMENT_MAE.length; i++) {
    if (fiyat < SEGMENT_MAE[i].limit) return SEGMENT_MAE[i];
  }
  return SEGMENT_MAE[SEGMENT_MAE.length - 1];
}

function getCookie(name) {
  let v = null;
  document.cookie.split(';').forEach(function(c) {
    c = c.trim();
    if (c.startsWith(name + '=')) v = decodeURIComponent(c.slice(name.length + 1));
  });
  return v;
}

/* ── Segmented button groups ───────────────────────────────── */
function initSegGroups() {
  document.querySelectorAll('.seg-group').forEach(function(group) {
    group.querySelectorAll('.seg-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        group.querySelectorAll('.seg-btn').forEach(function(b) { b.classList.remove('active'); });
        btn.classList.add('active');
      });
    });
  });
}

function getSegValue(groupId) {
  var btn = document.querySelector('#' + groupId + ' .seg-btn.active');
  return btn ? btn.dataset.value : '';
}

function setSegValue(groupId, value) {
  var group = document.getElementById(groupId);
  if (!group) return;
  group.querySelectorAll('.seg-btn').forEach(function(b) {
    b.classList.toggle('active', b.dataset.value === value);
  });
}

/* ── Tramer kategori ────────────────────────────────────────── */
function tramiHesapla(rawVal) {
  var t = parseInt(rawVal);
  if (isNaN(t) || t === -1) return 'bilinmiyor';
  if (t === 0)              return 'yok';
  if (t <= 5000)            return 'dusuk';
  if (t <= 25000)           return 'orta';
  return 'yuksek';
}

function tramiGuncelle() {
  var val     = document.getElementById('tramer').value;
  var kat     = tramiHesapla(val);
  var badge   = document.getElementById('tramer-badge');
  if (!badge) return;
  badge.className = 'tramer-badge tramer-' + kat;
  var labels = { yok: 'YOK', dusuk: 'DÜŞÜK', orta: 'ORTA', yuksek: 'YÜKSEK', bilinmiyor: 'BİLİNMİYOR' };
  badge.textContent = labels[kat] || kat.toUpperCase();
}

/* ── Marka / Seri / Model cascade ───────────────────────────── */
function markaSecildi() {
  var marka = document.getElementById('marka').value;
  var sel   = document.getElementById('seri');
  sel.innerHTML = '<option value="">— Önce Marka —</option>';
  if (marka && window.markaseriMap[marka]) {
    window.markaseriMap[marka].forEach(function(m) {
      var opt = document.createElement('option');
      opt.value = opt.textContent = m;
      sel.appendChild(opt);
    });
  }
  $('#seri').val('').trigger('change');
  document.getElementById('model').innerHTML = '<option value="">— Önce Seri —</option>';
  $('#model').val('').trigger('change');
}

function seriSecildi() {
  var marka = document.getElementById('marka').value;
  var seri  = document.getElementById('seri').value;
  var sel   = document.getElementById('model');
  sel.innerHTML = '<option value="">— Model Seçin —</option>';
  var harita = window.markaseriModelMap || {};
  if (marka && seri && harita[marka] && harita[marka][seri]) {
    harita[marka][seri].forEach(function(m) {
      var opt = document.createElement('option');
      opt.value = opt.textContent = m;
      sel.appendChild(opt);
    });
  }
  $('#model').val('').trigger('change');
  _kasaGuncelle('');
}

function modelSecildi() {
  var marka = document.getElementById('marka').value;
  var seri  = document.getElementById('seri').value;
  var model = document.getElementById('model').value;
  _kasaGuncelle(model, marka, seri);
}

function _kasaGuncelle(model, marka, seri) {
  var kasaSel  = document.getElementById('kasa_tipi');
  if (!kasaSel) return;
  var kasaHarita = window.markaseriModelKasaMap || {};
  var kasalar = (marka && seri && model &&
                 kasaHarita[marka] && kasaHarita[marka][seri] && kasaHarita[marka][seri][model])
    ? kasaHarita[marka][seri][model] : null;
  if (kasalar && kasalar.length > 0) {
    kasaSel.innerHTML = kasalar.map(function(k) { return '<option value="'+k+'">'+k+'</option>'; }).join('');
  } else {
    var tumKasalar = window.tumKasaTipleri || [];
    kasaSel.innerHTML = tumKasalar.map(function(k) { return '<option value="'+k+'">'+k+'</option>'; }).join('');
  }
  try { $('#kasa_tipi').trigger('change'); } catch(e) {}
}

/* ── Form sıfırla ───────────────────────────────────────────── */
function formSifirla() {
  document.getElementById('motor_gucu').value    = '';
  document.getElementById('yil').value           = '';
  document.getElementById('kilometre').value     = '';
  document.getElementById('boyali_sayisi').value = 0;
  document.getElementById('degisen_sayisi').value= 0;
  document.getElementById('tramer').value        = 0;

  // Segmented defaults
  setSegValue('vites_group', 'Düz');
  setSegValue('yakit_group', 'Benzin');
  setSegValue('cekis_group', 'Önden Çekiş');

  // Tramer badge
  tramiGuncelle();

  // Select2 fields
  try {
    $('#marka').val('').trigger('change');
    document.getElementById('seri').innerHTML  = '<option value="">— Önce Marka —</option>';
    $('#seri').val('').trigger('change');
    document.getElementById('model').innerHTML = '<option value="">— Önce Seri —</option>';
    $('#model').val('').trigger('change');
    _kasaGuncelle('');
    var sehirFirst = $('#sehir option:first').val();
    $('#sehir').val(sehirFirst).trigger('change');
    var motorFirst = $('#motor_hacmi option:first').val();
    $('#motor_hacmi').val(motorFirst).trigger('change');
    $('#renk').val('Beyaz').trigger('change');
  } catch(e) {}

  document.getElementById('result-panel').style.display    = 'none';
  var preCard = document.getElementById('pre-result-card');
  if (preCard) preCard.style.display = 'block';
  var explainWrap = document.getElementById('explain-wrap');
  if (explainWrap) explainWrap.style.display = 'none';
  document.getElementById('error-box').style.display       = 'none';
  var shareWrap = document.getElementById('share-tahmin-wrap');
  if (shareWrap) shareWrap.style.display = 'none';
}

/* ── Formatters ─────────────────────────────────────────────── */
function fmt(n) {
  return parseInt(n).toLocaleString('tr-TR') + ' ₺';
}

function animatePriceCounter(elId, from, to, durationMs) {
  var el = document.getElementById(elId);
  if (!el) return;
  var start = performance.now();
  function step(now) {
    var elapsed  = now - start;
    var progress = Math.min(elapsed / durationMs, 1);
    var eased    = 1 - Math.pow(1 - progress, 3);
    var current  = Math.round(from + (to - from) * eased);
    el.textContent = current.toLocaleString('tr-TR') + ' ₺';
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ── Document ready ─────────────────────────────────────────── */
$(document).ready(function() {
  // Select2: marka / seri / model (search inside dropdown)
  $('#marka').select2({ width: '100%', placeholder: '— Marka Seçin —' });
  $('#seri').select2({  width: '100%', placeholder: '— Önce Marka —' });
  $('#model').select2({ width: '100%', placeholder: '— Önce Seri —' });

  // Select2: şehir, motor hacmi, kasa, renk
  $('#sehir').select2({       width: '100%', placeholder: 'Şehir seçin...' });
  $('#motor_hacmi').select2({ width: '100%', placeholder: 'Motor hacmi...' });
  $('#kasa_tipi').select2({   width: '100%', placeholder: 'Kasa tipi...' });
  $('#renk').select2({         width: '100%', placeholder: 'Renk...' });

  // Cascade events
  $('#marka').on('select2:select select2:unselect', function() { markaSecildi(); });
  $('#seri').on('select2:select select2:unselect',  function() { seriSecildi(); });
  $('#model').on('select2:select select2:unselect', function() { modelSecildi(); });

  // Segmented buttons
  initSegGroups();

  // Initial tramer badge
  tramiGuncelle();

  // URL param auto-fill (item 14 — paylaşım linki)
  _urlParamAutoFill();
});

/* ── Tahmin et ──────────────────────────────────────────────── */
async function tahminEt() {
  var btn     = document.getElementById('btn');
  var spinner = document.getElementById('spinner');
  var btnIcon = document.getElementById('btn-icon');
  var btnTxt  = document.getElementById('btn-text');
  var errBox  = document.getElementById('error-box');

  var marka = document.getElementById('marka').value;
  var seri  = document.getElementById('seri').value;
  var model = document.getElementById('model').value;

  if (!marka || !seri || !model) {
    errBox.style.display  = 'flex';
    errBox.textContent    = '⚠️ Lütfen marka, seri ve model seçin.';
    return;
  }

  var kmRaw  = document.getElementById('kilometre').value.trim();
  var hpRaw  = document.getElementById('motor_gucu').value.trim();
  var yilRaw = document.getElementById('yil').value.trim();

  if (!kmRaw) {
    errBox.style.display = 'flex';
    errBox.textContent   = '⚠️ Lütfen kilometre değerini girin.';
    return;
  }
  if (!hpRaw) {
    errBox.style.display = 'flex';
    errBox.textContent   = '⚠️ Lütfen motor gücünü girin.';
    return;
  }
  if (!yilRaw) {
    errBox.style.display = 'flex';
    errBox.textContent   = '⚠️ Lütfen çıkış yılını girin.';
    return;
  }

  var km  = parseInt(kmRaw);
  var hp  = parseInt(hpRaw);
  var yil = parseInt(yilRaw);

  if (km < 0 || km > 1000000) {
    errBox.style.display = 'flex';
    errBox.textContent   = '⚠️ Kilometre 0 ile 1.000.000 arasında olmalıdır.';
    return;
  }
  if (hp < 30 || hp > 1000) {
    errBox.style.display = 'flex';
    errBox.textContent   = '⚠️ Motor gücü 30 ile 1000 HP arasında olmalıdır.';
    return;
  }
  if (yil < 1974 || yil > 2026) {
    errBox.style.display = 'flex';
    errBox.textContent   = '⚠️ Trafiğe çıkış yılı 1974 ile 2026 arasında olmalıdır.';
    return;
  }

  errBox.style.display = 'none';
  btn.disabled         = true;
  spinner.style.display = 'block';
  if (btnIcon) btnIcon.style.display = 'none';
  btnTxt.textContent   = 'Hesaplanıyor...';

  var guncelYil    = new Date().getFullYear();
  var girilenYil   = parseInt(document.getElementById('yil').value) || guncelYil;
  var hesaplananYas = Math.max(0, guncelYil - girilenYil);

  // Tramer: -1 → bilinmiyor, gönder 0
  var tramerRaw   = parseInt(document.getElementById('tramer').value);
  if (isNaN(tramerRaw)) tramerRaw = 0;
  var tramerKat   = tramiHesapla(tramerRaw);
  var tramerGonder = tramerRaw === -1 ? 0 : tramerRaw;

  var payload = {
    marka          : marka,
    seri           : seri,
    model          : model,
    kilometre      : document.getElementById('kilometre').value,
    motor_hacmi    : document.getElementById('motor_hacmi').value,
    motor_gucu     : document.getElementById('motor_gucu').value,
    yas            : hesaplananYas,
    vites_tipi     : getSegValue('vites_group'),
    yakit_tipi     : getSegValue('yakit_group'),
    kasa_tipi      : document.getElementById('kasa_tipi').value,
    renk           : document.getElementById('renk').value,
    cekis          : getSegValue('cekis_group'),
    kimden         : 'Galeriden',
    tramer_kategori: tramerKat,
    sehir          : document.getElementById('sehir').value,
    boyali_sayisi  : document.getElementById('boyali_sayisi').value,
    degisen_sayisi : document.getElementById('degisen_sayisi').value,
    tramer         : tramerGonder,
  };

  try {
    var csrfToken = window.CSRF_TOKEN || getCookie('csrftoken');
    var res = await fetch(window.TAHMIN_ET_URL, {
      method : 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
      body   : JSON.stringify(payload),
    });

    if (!res.ok) throw new Error('Sunucu Hatası (' + res.status + ')');

    var data = await res.json();
    if (data.error) throw new Error(data.error);

    // Araç adı
    var arabaAdi = [marka, seri, model].filter(Boolean).join(' · ');
    document.getElementById('res-araba-adi').textContent = arabaAdi;

    // Araç yaşı
    var yas = Math.max(0, new Date().getFullYear() - (parseInt(document.getElementById('yil').value) || new Date().getFullYear()));
    document.getElementById('res-yas').textContent = yas + ' yıl';

    // Sonuçlar
    document.getElementById('res-dusuk').textContent  = fmt(data.dusuk);
    document.getElementById('res-yuksek').textContent = fmt(data.yuksek);
    document.getElementById('res-r2').textContent     = data.r2;

    // Segment MAE — genel model MAE yerine bu fiyat aralığının MAE'si
    var seg = getSegmentMAE(Math.round(data.fiyat));
    document.getElementById('res-mae').textContent = fmt(seg.mae);

    // Kullanıcı dostu açıklama bölümünü doldur
    var dusuk  = Math.round(data.dusuk);
    var yuksek = Math.round(data.yuksek);
    var fiyat  = Math.round(data.fiyat);
    var maePct = Math.round(seg.mae / fiyat * 100);

    var altSinir = Math.max(0, fiyat - seg.mae);
    var ustSinir = fiyat + seg.mae;

    var maeEl = document.getElementById('explain-mae-range');
    if (maeEl) {
      maeEl.innerHTML =
        '<strong>' + seg.label + '</strong> segmentinde model ortalama ' +
        '<strong>±' + seg.mae.toLocaleString('tr-TR') + ' TL</strong> hata yapıyor.' +
        ' Yani bu araç için tahmin <strong>' + altSinir.toLocaleString('tr-TR') +
        ' – ' + ustSinir.toLocaleString('tr-TR') + ' TL</strong> arasında gerçekleşebilir.';
    }

    var intervalEl = document.getElementById('explain-interval');
    if (intervalEl) {
      intervalEl.innerHTML =
        'Benzer araçların <strong>%80\'i</strong> ' +
        '<strong>' + dusuk.toLocaleString('tr-TR') + ' ₺</strong> ile ' +
        '<strong>' + yuksek.toLocaleString('tr-TR') + ' ₺</strong> arasında fiyatlanmıştır.';
    }

    var r2El = document.getElementById('explain-r2');
    if (r2El) {
      var r2Pct = Math.round(data.r2 * 100);
      var guvLabel = r2Pct >= 95 ? 'Çok Yüksek' : r2Pct >= 90 ? 'Yüksek' : r2Pct >= 80 ? 'Orta' : 'Düşük';
      var guvColor = r2Pct >= 95 ? '#22c55e' : r2Pct >= 90 ? '#3b82f6' : '#d97706';
      r2El.innerHTML =
        'Model, gerçek satış fiyatlarının <strong>' + r2Pct + '%\'ini</strong> açıklıyor.' +
        ' Tahmin güvenilirliği: <strong style="color:' + guvColor + '">' + guvLabel + '</strong>.';
    }

    var explainWrap = document.getElementById('explain-wrap');
    if (explainWrap) explainWrap.style.display = 'block';

    // Güven aralığı çubuğu
    var rangeBar = document.getElementById('range-bar');
    var rangeDot = document.getElementById('range-dot');
    if (rangeBar && rangeDot) {
      var d    = Math.round(data.dusuk);
      var f    = Math.round(data.fiyat);
      var y    = Math.round(data.yuksek);
      var span = y - d || 1;
      var dotPct = ((f - d) / span * 100).toFixed(1);
      rangeBar.style.left  = '0%';
      rangeBar.style.right = '0%';
      rangeDot.style.left  = dotPct + '%';
    }

    // R² bar
    document.getElementById('r2-fill').style.width = (data.r2 * 100).toFixed(1) + '%';

    // Paneli göster, bilgi kartını gizle
    var preCard = document.getElementById('pre-result-card');
    if (preCard) preCard.style.display = 'none';
    document.getElementById('result-panel').style.display = 'block';

    // Fiyat animasyonu
    animatePriceCounter('res-fiyat', 0, Math.round(data.fiyat), 900);
    document.getElementById('result-panel').scrollIntoView({ behavior: 'smooth' });

    // Paylaşım butonları — URL parametreleriyle form otomatik doldurulsun
    var shareParams = new URLSearchParams({
      marka      : marka,
      seri       : seri,
      model      : model,
      yil        : document.getElementById('yil').value,
      km         : document.getElementById('kilometre').value,
      motor_gucu : document.getElementById('motor_gucu').value,
      vites      : getSegValue('vites_group'),
      yakit      : getSegValue('yakit_group'),
    });
    var shareUrl  = window.location.origin + window.location.pathname + '?' + shareParams.toString();
    var shareText = encodeURIComponent('OtoNova AI Tahmini — ' + arabaAdi + ': ' + fmt(data.fiyat) + '\n' + shareUrl);
    document.getElementById('share-tahmin-wa').href = 'https://api.whatsapp.com/send?text=' + shareText;
    document.getElementById('share-tahmin-wrap').style.display = 'block';

  } catch(e) {
    errBox.style.display = 'flex';
    errBox.textContent   = '❌ Hata: ' + e.message;
  } finally {
    btn.disabled = false;
    spinner.style.display = 'none';
    if (btnIcon) btnIcon.style.display = '';
    btnTxt.textContent = 'Fiyat Tahmin Et';
  }
}

function copyTahmin() {
  var araba    = document.getElementById('res-araba-adi').textContent;
  var fiyatTxt = document.getElementById('res-fiyat').textContent;
  navigator.clipboard.writeText('OtoNova AI Tahmini — ' + araba + ': ' + fiyatTxt + '\n' + window.location.href)
    .then(function() { if (typeof showToast === 'function') showToast('Tahmin sonucu kopyalandı!', 'success'); });
}

/* ── URL param auto-fill (item 14 — paylaşım linki) ─────────── */
function _urlParamAutoFill() {
  var p = new URLSearchParams(window.location.search);
  var marka = p.get('marka');
  if (!marka) return;

  try {
    $('#marka').val(marka).trigger('change');

    var seri = p.get('seri');
    if (seri) {
      markaSecildi();
      setTimeout(function() {
        $('#seri').val(seri).trigger('change');
        var model = p.get('model');
        if (model) {
          seriSecildi();
          setTimeout(function() {
            $('#model').val(model).trigger('change');
          }, 100);
        }
      }, 100);
    }
  } catch(e) {}

  var yil = p.get('yil');
  if (yil) document.getElementById('yil').value = yil;

  var km = p.get('km');
  if (km) document.getElementById('kilometre').value = km;

  var mg = p.get('motor_gucu');
  if (mg) document.getElementById('motor_gucu').value = mg;

  var vites = p.get('vites');
  if (vites) setSegValue('vites_group', vites);

  var yakit = p.get('yakit');
  if (yakit) setSegValue('yakit_group', yakit);

  if (marka || yil || km) {
    setTimeout(function() {
      tahminEt();
    }, 400);
  }
}
