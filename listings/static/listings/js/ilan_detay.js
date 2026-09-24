(function() {
  var cfg = window.ILAN_CFG;
  if (!cfg) return;

  // Son görüntülenenler kaydı
  try {
    var liste = JSON.parse(localStorage.getItem('son_goruntulenenler') || '[]');
    liste = liste.filter(function(x) { return x.slug !== cfg.slug; });
    liste.unshift({
      slug:   cfg.slug,
      baslik: cfg.baslik,
      marka:  cfg.marka,
      yil:    cfg.yil,
      fiyat:  cfg.fiyat,
      km:     cfg.km,
      foto:   cfg.foto
    });
    if (liste.length > 6) liste = liste.slice(0, 6);
    localStorage.setItem('son_goruntulenenler', JSON.stringify(liste));
  } catch(e) {}

  // Thumbnail aktif gösterimi
  var carousel = document.getElementById('ilanCarousel');
  if (carousel) {
    carousel.addEventListener('slide.bs.carousel', function(e) {
      document.querySelectorAll('.thumb-img').forEach(function(t, i) {
        t.style.opacity = i === e.to ? '1' : '.55';
      });
    });
  }

  // Favori toggle
  var favBtn = document.getElementById('favBtn');
  if (favBtn) {
    favBtn.addEventListener('click', function() {
      fetch(cfg.favoriUrl, {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': cfg.csrfToken},
        body: JSON.stringify({ilan_id: cfg.pk})
      })
      .then(function(r) { return r.json(); })
      .then(function(d) {
        var icon = favBtn.querySelector('i');
        icon.className = d.favori ? 'bi bi-heart-fill' : 'bi bi-heart';
        favBtn.style.color = d.favori ? '#ef4444' : '';
        favBtn.style.borderColor = d.favori ? '#fecaca' : '';
      });
    });
  }

  // Lightbox
  document.querySelectorAll('[data-lightbox]').forEach(function(img) {
    img.addEventListener('click', function() {
      document.getElementById('lightbox-img').src = img.dataset.lightbox;
      document.getElementById('lightbox-overlay').classList.add('open');
    });
  });
  var lbClose = document.getElementById('lightbox-close');
  if (lbClose) {
    lbClose.addEventListener('click', function() {
      document.getElementById('lightbox-overlay').classList.remove('open');
    });
  }
  var lbOverlay = document.getElementById('lightbox-overlay');
  if (lbOverlay) {
    lbOverlay.addEventListener('click', function(e) {
      if (e.target === e.currentTarget) e.currentTarget.classList.remove('open');
    });
  }
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      var o = document.getElementById('lightbox-overlay');
      if (o) o.classList.remove('open');
    }
  });

  // WhatsApp + Kopyala
  var url   = encodeURIComponent(window.location.href);
  var title = encodeURIComponent(cfg.baslik + ' — OtoNova');
  var wpEl  = document.getElementById('share-whatsapp');
  if (wpEl) wpEl.href = 'https://api.whatsapp.com/send?text=' + title + '%20' + url;
})();

function copyIlanLink() {
  navigator.clipboard.writeText(window.location.href).then(function() {
    showToast('Link panoya kopyalandı!', 'success');
  });
}

function telGoster(btn) {
  if (btn.dataset.acildi) return true;
  var numara = btn.dataset.tel;
  btn.dataset.acildi = '1';
  btn.innerHTML = '<i class="bi bi-telephone-fill me-1"></i>' + numara;
  btn.href = 'tel:' + numara.replace(/\s/g, '');
  var wp = document.getElementById('wp-btn');
  if (wp) {
    var digits = numara.replace(/\D/g, '');
    var intl   = '90' + digits.slice(1);
    wp.href = 'https://wa.me/' + intl;
    wp.style.display = 'flex';
  }
  return false;
}

// Piyasa Fiyat Dağılımı Grafiği
(function() {
  var cfg = window.ILAN_CFG;
  if (!cfg || !cfg.benzerFiyatlar || !cfg.benzerFiyatlar.length) return;
  var canvas = document.getElementById('fiyat-chart');
  if (!canvas) return;

  var fiyatlar = cfg.benzerFiyatlar;
  var ilanF    = cfg.ilanFiyat;
  if (!fiyatlar.length) return;

  var tumFiyatlar = fiyatlar.concat([ilanF]);
  var mn = Math.min.apply(null, tumFiyatlar);
  var mx = Math.max.apply(null, tumFiyatlar);
  var n  = Math.min(8, Math.max(4, Math.ceil(fiyatlar.length / 3)));
  var aralik = (mx - mn) / n || 1;

  var sayilar = Array(n).fill(0);
  fiyatlar.forEach(function(f) {
    var i = Math.min(Math.floor((f - mn) / aralik), n - 1);
    sayilar[i]++;
  });
  var ilanBin = Math.min(Math.floor((ilanF - mn) / aralik), n - 1);

  var ortalama   = fiyatlar.reduce(function(a,b){return a+b;},0) / fiyatlar.length;
  var dahaFazla  = fiyatlar.filter(function(f){return f > ilanF;}).length;
  var yuzde      = Math.round(dahaFazla / fiyatlar.length * 100);
  function fmt(v) { return Math.round(v/1000) + 'K ₺'; }

  var statsEl = document.getElementById('chart-stats');
  if (statsEl) {
    var chipBase = 'display:inline-flex;align-items:center;gap:.3rem;padding:.25rem .6rem;border-radius:20px;font-size:.67rem;font-weight:600;font-family:"JetBrains Mono",monospace;';
    statsEl.innerHTML =
      '<span style="' + chipBase + 'background:rgba(255,255,255,.07);color:rgba(255,255,255,.5)">' +
        '<i class="bi bi-collection" style="font-size:.75rem"></i> ' + fiyatlar.length + ' araç' +
      '</span>' +
      '<span style="' + chipBase + 'background:rgba(165,180,252,.1);color:#a5b4fc;border:1px solid rgba(165,180,252,.2)">' +
        '<i class="bi bi-graph-up" style="font-size:.75rem"></i> Ort. ' + fmt(ortalama) +
      '</span>' +
      (yuzde > 0
        ? '<span style="' + chipBase + 'background:rgba(52,211,153,.12);color:#6ee7b7;border:1px solid rgba(52,211,153,.2)">' +
            '<i class="bi bi-arrow-down-short" style="font-size:.85rem"></i> %' + yuzde + '\'inden ucuz</span>'
        : '<span style="' + chipBase + 'background:rgba(251,191,36,.1);color:#fbbf24;border:1px solid rgba(251,191,36,.2)">' +
            '<i class="bi bi-arrow-up-short" style="font-size:.85rem"></i> En pahalılar arasında</span>'
      );
  }

  var ctx2d = canvas.getContext('2d');
  var gradNormal = ctx2d.createLinearGradient(0, 0, 0, canvas.height * 2);
  gradNormal.addColorStop(0, 'rgba(99,102,241,.65)');
  gradNormal.addColorStop(1, 'rgba(99,102,241,.15)');
  var gradAktif = ctx2d.createLinearGradient(0, 0, 0, canvas.height * 2);
  gradAktif.addColorStop(0, 'rgba(59,130,246,1)');
  gradAktif.addColorStop(1, 'rgba(59,130,246,.4)');

  var renkler  = sayilar.map(function(_, i) { return i === ilanBin ? gradAktif : gradNormal; });
  var kenarlar = sayilar.map(function(_, i) { return i === ilanBin ? '#60a5fa' : 'rgba(99,102,241,.5)'; });
  var etiketler = sayilar.map(function(_, i) {
    return Math.round((mn + i * aralik) / 1000) + 'K';
  });

  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: etiketler,
      datasets: [{
        data: sayilar,
        backgroundColor: renkler,
        borderColor: kenarlar,
        borderWidth: 1.5,
        borderRadius: 6,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      animation: { duration: 600, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1e293b',
          titleColor: '#a5b4fc',
          bodyColor: '#cbd5e1',
          borderColor: 'rgba(99,102,241,.3)',
          borderWidth: 1,
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            title: function(ctx) {
              var i = ctx[0].dataIndex;
              var bas = Math.round((mn + i * aralik) / 1000);
              var bit = Math.round((mn + (i + 1) * aralik) / 1000);
              return bas + 'K – ' + bit + 'K ₺';
            },
            label: function(ctx) {
              var msg = '  ' + ctx.raw + ' araç bu aralıkta';
              if (ctx.dataIndex === ilanBin) msg += '  ← Bu ilan';
              return msg;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 9, family: "'JetBrains Mono', monospace" }, color: 'rgba(255,255,255,.3)' },
          border: { display: false }
        },
        y: { display: false, grid: { display: false } }
      }
    }
  });
})();
