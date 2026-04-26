function markaSecildi() {
  const marka = document.getElementById('marka').value;
  const sel   = document.getElementById('seri');
  sel.innerHTML = '<option value="">— Model Seçin —</option>';
  if (marka && window.markaseriMap[marka]) {
    window.markaseriMap[marka].forEach(m => {
      const opt = document.createElement('option');
      opt.value = opt.textContent = m;
      sel.appendChild(opt);
    });
  }
  // Dinamik olarak seriler eklendikten sonra Select2'yi yenile
  $('#seri').trigger('change');
}

function fmt(n) {
  return parseInt(n).toLocaleString('tr-TR') + ' ₺';
}

// Sayfa yüklendiğinde tüm <select> etiketlerini aranabilir Select2'ye dönüştür
$(document).ready(function() {
  // Select2'yi devre dışı bırak for the marka select to use native onchange
  $('#marka').select2({ width: '100%' });
  $('#seri').select2({ width: '100%' });
  $('#model').select2({ width: '100%' });
  
  // Select2 event handler for marka - native onchange doesn't work with Select2
  $('#marka').on('select2:select', function(e) {
    markaSecildi();
  });
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
    const res  = await fetch(window.TAHMIN_ET_URL, {
      method : 'POST',
      headers: {'Content-Type': 'application/json'},
      body   : JSON.stringify(payload),
    });

    // Eğer sunucudan JSON yerine HTML (hata sayfası) dönerse hatayı yakala
    if (!res.ok) {
      throw new Error(`Sunucu Hatası (${res.status}). Detaylar için backend loglarına bakın.`);
    }

    const data = await res.json();

    if (data.error) throw new Error(data.error);

    document.getElementById('result-panel').style.display = 'block';
    document.getElementById('res-fiyat').textContent  = parseInt(data.fiyat).toLocaleString('tr-TR');
    document.getElementById('res-dusuk').textContent  = fmt(data.dusuk);
    document.getElementById('res-yuksek').textContent = fmt(data.yuksek);
    document.getElementById('res-mae').textContent    = fmt(data.mae);
    document.getElementById('res-mape').textContent   = '%' + data.mape;
    document.getElementById('res-r2').textContent     = data.r2;
    document.getElementById('r2-fill').style.width    = (data.r2 * 100).toFixed(1) + '%';

    document.getElementById('result-panel').scrollIntoView({behavior:'smooth'});
  } catch (e) {
    errBox.style.display = 'flex';
    errBox.textContent   = '❌ Hata: ' + e.message;
  } finally {
    btn.disabled = false;
    spinner.style.display = 'none';
    btnTxt.textContent = '🔍 Fiyat Tahmin Et';
  }
}