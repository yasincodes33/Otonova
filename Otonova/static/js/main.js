function getCookie(name) {
  let v = null;
  document.cookie.split(';').forEach(function(c) {
    c = c.trim();
    if (c.startsWith(name + '=')) v = decodeURIComponent(c.slice(name.length + 1));
  });
  return v;
}

function formSifirla() {
  // Teknik Özellikler — önce bunları sıfırla (Select2 işlemleri sonraya bırak)
  document.getElementById('vites_tipi').selectedIndex  = 0;
  document.getElementById('yakit_tipi').selectedIndex  = 0;
  document.getElementById('cekis').selectedIndex       = 0;
  document.getElementById('motor_hacmi').selectedIndex = 0;
  document.getElementById('motor_gucu').value          = 120;
  document.getElementById('yil').value                 = 2016;
  document.getElementById('kilometre').value           = 120000;

  // Araç Kimliği
  document.getElementById('kasa_tipi').selectedIndex = 0;
  document.getElementById('renk').selectedIndex      = 0;

  // İlan Bilgileri
  document.getElementById('sehir').selectedIndex          = 0;
  document.getElementById('kimden').selectedIndex         = 0;
  document.getElementById('tramer_kategori').selectedIndex = 0;
  document.getElementById('boyali_sayisi').value          = 0;
  document.getElementById('degisen_sayisi').value         = 0;
  document.getElementById('tramer').value                 = 0;

  try {
    $('#marka').val('').trigger('change');
    document.getElementById('seri').innerHTML = '<option value="">— Önce Marka —</option>';
    $('#seri').val('').trigger('change');
    document.getElementById('model').innerHTML = '<option value="">— Önce Seri —</option>';
    $('#model').val('').trigger('change');
    _kasaGuncelle('');
  } catch(e) {}

  document.getElementById('result-panel').style.display = 'none';
  document.getElementById('error-box').style.display    = 'none';
  var shareWrap = document.getElementById('share-tahmin-wrap');
  if (shareWrap) shareWrap.style.display = 'none';
}

function markaSecildi() {
  const marka = document.getElementById('marka').value;
  const sel   = document.getElementById('seri');
  sel.innerHTML = '<option value="">— Önce Marka —</option>';
  if (marka && window.markaseriMap[marka]) {
    window.markaseriMap[marka].forEach(m => {
      const opt = document.createElement('option');
      opt.value = opt.textContent = m;
      sel.appendChild(opt);
    });
  }
  $('#seri').val('').trigger('change');
  // Seri sıfırlandığında modeli de sıfırla
  document.getElementById('model').innerHTML = '<option value="">— Önce Seri —</option>';
  $('#model').val('').trigger('change');
}

function seriSecildi() {
  const marka = document.getElementById('marka').value;
  const seri  = document.getElementById('seri').value;
  const sel   = document.getElementById('model');
  sel.innerHTML = '<option value="">— Model Seçin —</option>';
  const harita = window.markaseriModelMap || {};
  if (marka && seri && harita[marka] && harita[marka][seri]) {
    harita[marka][seri].forEach(m => {
      const opt = document.createElement('option');
      opt.value = opt.textContent = m;
      sel.appendChild(opt);
    });
  }
  $('#model').val('').trigger('change');
  // Kasa tipini de sıfırla
  _kasaGuncelle('');
}

function modelSecildi() {
  const marka = document.getElementById('marka').value;
  const seri  = document.getElementById('seri').value;
  const model = document.getElementById('model').value;
  _kasaGuncelle(model, marka, seri);
}

function _kasaGuncelle(model, marka, seri) {
  const kasaSel = document.getElementById('kasa_tipi');
  if (!kasaSel) return;
  const kasaHarita = window.markaseriModelKasaMap || {};
  const kasalar = (marka && seri && model && kasaHarita[marka] && kasaHarita[marka][seri] && kasaHarita[marka][seri][model])
    ? kasaHarita[marka][seri][model] : null;
  if (kasalar && kasalar.length > 0) {
    kasaSel.innerHTML = kasalar.map(k => `<option value="${k}">${k}</option>`).join('');
  } else {
    // Haritada yoksa tüm kasa tiplerini geri yükle
    const tumKasalar = window.tumKasaTipleri || [];
    kasaSel.innerHTML = tumKasalar.map(k => `<option value="${k}">${k}</option>`).join('');
  }
}

function fmt(n) {
  return parseInt(n).toLocaleString('tr-TR') + ' ₺';
}

function animatePriceCounter(elId, from, to, durationMs) {
  const el = document.getElementById(elId);
  if (!el) return;
  const start = performance.now();
  function step(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / durationMs, 1);
    // ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(from + (to - from) * eased);
    el.textContent = current.toLocaleString('tr-TR') + ' ₺';
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

$(document).ready(function() {
  $('#marka').select2({ width: '100%' });
  $('#seri').select2({ width: '100%' });
  $('#model').select2({ width: '100%' });

  $('#marka').on('select2:select select2:unselect', function() { markaSecildi(); });
  $('#seri').on('select2:select select2:unselect', function() { seriSecildi(); });
  $('#model').on('select2:select select2:unselect', function() { modelSecildi(); });
});

async function tahminEt() {
  const btn     = document.getElementById('btn');
  const spinner = document.getElementById('spinner');
  const btnTxt  = document.getElementById('btn-text');
  const errBox  = document.getElementById('error-box');

  const marka    = document.getElementById('marka').value;
  const seri     = document.getElementById('seri').value;
  const model    = document.getElementById('model').value;
  if (!marka || !seri || !model) {
    errBox.style.display = 'flex';
    errBox.textContent   = '⚠️ Lütfen marka, seri ve model seçin.';
    return;
  }

  const km  = parseInt(document.getElementById('kilometre').value);
  const hp  = parseInt(document.getElementById('motor_gucu').value);
  const yil = parseInt(document.getElementById('yil').value);
  if (km < 6000 || km > 500000) {
    errBox.style.display = 'flex';
    errBox.textContent = '⚠️ Kilometre 6.000 ile 500.000 arasında olmalıdır.';
    return;
  }
  if (hp < 30 || hp > 1000) {
    errBox.style.display = 'flex';
    errBox.textContent = '⚠️ Motor gücü 30 ile 1000 HP arasında olmalıdır.';
    return;
  }
  if (yil < 1974 || yil > 2026) {
    errBox.style.display = 'flex';
    errBox.textContent = '⚠️ Trafiğe çıkış yılı 1974 ile 2026 arasında olmalıdır.';
    return;
  }

  errBox.style.display = 'none';
  btn.disabled = true;
  spinner.style.display = 'block';
  btnTxt.textContent = 'Hesaplanıyor...';

  // Model arabanın yaşını bekliyor. Biz "Mevcut Yıl - Girilen Yıl" yaparak yaşı hesaplıyoruz.
  const guncelYil = new Date().getFullYear();
  const girilenYil = parseInt(document.getElementById('yil').value) || guncelYil;
  const hesaplananYas = Math.max(0, guncelYil - girilenYil); // Negatif yaş olmasını engelle

  const payload = {
    marka        : marka,
    seri         : seri,
    model        : model,
    kilometre    : document.getElementById('kilometre').value,
    motor_hacmi  : document.getElementById('motor_hacmi').value,
    motor_gucu   : document.getElementById('motor_gucu').value,
    yas          : hesaplananYas,
    vites_tipi   : document.getElementById('vites_tipi').value,
    yakit_tipi   : document.getElementById('yakit_tipi').value,
    kasa_tipi    : document.getElementById('kasa_tipi').value,
    renk         : document.getElementById('renk').value,
    cekis        : document.getElementById('cekis').value,
    kimden       : document.getElementById('kimden').value,
    tramer_kategori: document.getElementById('tramer_kategori').value,
    sehir        : document.getElementById('sehir').value,
    boyali_sayisi: document.getElementById('boyali_sayisi').value,
    degisen_sayisi: document.getElementById('degisen_sayisi').value,
    tramer       : document.getElementById('tramer').value,
  };

  try {
    const csrfToken = window.CSRF_TOKEN || getCookie('csrftoken');
    const res  = await fetch(window.TAHMIN_ET_URL, {
      method : 'POST',
      headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken},
      body   : JSON.stringify(payload),
    });

    // Eğer sunucudan JSON yerine HTML (hata sayfası) dönerse hatayı yakala
    if (!res.ok) {
      throw new Error(`Sunucu Hatası (${res.status}). Detaylar için backend loglarına bakın.`);
    }

    const data = await res.json();

    if (data.error) throw new Error(data.error);

    // Araç adı
    const arabaAdi = [marka, seri, model].filter(Boolean).join(' · ');
    document.getElementById('res-araba-adi').textContent = arabaAdi;

    // Araç yaşı
    const guncelYilSonuc = new Date().getFullYear();
    const seciliYil = parseInt(document.getElementById('yil').value) || guncelYilSonuc;
    const yas = Math.max(0, guncelYilSonuc - seciliYil);
    document.getElementById('res-yas').textContent = yas + ' yıl';

    // Statik metrikler
    document.getElementById('res-dusuk').textContent  = fmt(data.dusuk);
    document.getElementById('res-yuksek').textContent = fmt(data.yuksek);
    document.getElementById('res-mae').textContent    = fmt(data.mae);
    document.getElementById('res-mape').textContent   = '%' + data.mape;
    document.getElementById('res-r2').textContent     = data.r2;

    // Güven aralığı çubuğu
    const rangeBar = document.getElementById('range-bar');
    const rangeDot = document.getElementById('range-dot');
    if (rangeBar && rangeDot) {
      const d = Math.round(data.dusuk), f = Math.round(data.fiyat), y = Math.round(data.yuksek);
      const span = y - d || 1;
      const leftPct  = 0;
      const rightPct = 100;
      const dotPct   = ((f - d) / span * 100).toFixed(1);
      rangeBar.style.left  = leftPct + '%';
      rangeBar.style.right = (100 - rightPct) + '%';
      rangeDot.style.left  = dotPct + '%';
    }

    // R² bar
    document.getElementById('r2-fill').style.width = (data.r2 * 100).toFixed(1) + '%';

    // Panel göster
    document.getElementById('result-panel').style.display = 'block';

    // Fiyat animasyonu
    animatePriceCounter('res-fiyat', 0, Math.round(data.fiyat), 900);

    document.getElementById('result-panel').scrollIntoView({behavior:'smooth'});

    // Paylaşım butonlarını aktif et
    var araba = document.getElementById('res-araba-adi').textContent;
    var fiyatTxt = document.getElementById('res-fiyat').textContent;
    var shareText = encodeURIComponent('OtoNova AI Tahmini — ' + araba + ': ' + fiyatTxt + ' TL\n' + window.location.href);
    document.getElementById('share-tahmin-wa').href = 'https://api.whatsapp.com/send?text=' + shareText;
    document.getElementById('share-tahmin-wrap').style.display = 'block';
  } catch (e) {
    errBox.style.display = 'flex';
    errBox.textContent   = '❌ Hata: ' + e.message;
  } finally {
    btn.disabled = false;
    spinner.style.display = 'none';
    btnTxt.textContent = '🔍 Fiyat Tahmin Et';
  }
}

function copyTahmin() {
  var araba = document.getElementById('res-araba-adi').textContent;
  var fiyatTxt = document.getElementById('res-fiyat').textContent;
  navigator.clipboard.writeText('OtoNova AI Tahmini — ' + araba + ': ' + fiyatTxt + ' TL\n' + window.location.href)
    .then(function() { if (typeof showToast === 'function') showToast('Tahmin sonucu kopyalandı!', 'success'); });
}