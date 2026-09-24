import json

from django.shortcuts import render

from listings.models import IlanModel


def index(request):
    from predictions.services import MLService
    one_cikan = IlanModel.objects.filter(is_active=True, durum='aktif') \
        .prefetch_related('fotolar').order_by('-olusturuldu')[:4]
    toplam_ilan   = IlanModel.objects.filter(is_active=True, durum='aktif').count()
    firsat_sayisi = IlanModel.objects.filter(is_active=True, durum='aktif', firsat_skoru__gte=70).count()
    ai_hesaplanan = IlanModel.objects.filter(is_active=True, durum='aktif', ai_tahmin_fiyat__isnull=False).count()
    meta = MLService.get_meta()
    return render(request, 'pages/anasayfa.html', {
        'one_cikan_ilanlar': one_cikan,
        'toplam_ilan':       toplam_ilan,
        'firsat_sayisi':     firsat_sayisi,
        'ai_hesaplanan':     ai_hesaplanan,
        'marka_seri_json':   json.dumps(meta.get('marka_seri_map', {})),
    })


def hakkimizda(request):
    toplam = IlanModel.objects.filter(is_active=True, durum='aktif').count()
    if toplam >= 1000:
        ilan_gosterim = f"{toplam // 1000}K+"
    elif toplam > 0:
        ilan_gosterim = f"{toplam}+"
    else:
        ilan_gosterim = "0"
    stats = [
        (ilan_gosterim, 'İLAN', 'Aktif araç ilanı'),
        ('98%', 'MEMNUNİYET', 'Kullanıcı memnuniyeti'),
        ('0.96', 'R² SKORU', 'AI model doğruluğu'),
        ('2026', 'KURULUŞ', 'Yılından bu yana'),
    ]
    ozellikler = [
        ('cpu', 'AI Fiyat Tahmini', 'Binlerce ilanı analiz ederek anlık ve doğru fiyat tahminleri üretir.'),
        ('shield-check', 'Güvenli Alışveriş', 'Doğrulanmış satıcılar ve şeffaf ilan sistemi ile güvenli deneyim.'),
        ('graph-up-arrow', 'Piyasa Analizi', 'Gerçek zamanlı verilerle araç değerini ve piyasa trendlerini takip edin.'),
        ('people', 'Geniş Topluluk', 'Binlerce alıcı ve satıcıdan oluşan aktif bir kullanıcı ağı.'),
    ]
    adimlar = [
        ('1', 'Veri Toplama', 'Türkiye genelinde yüz binlerce araç ilanından özellik ve fiyat verisi toplanır.'),
        ('2', 'Model Eğitimi', 'Random Forest ve Gradient Boosting algoritmaları log-fiyat hedefiyle eğitilir; %96 R² doğruluk elde edilir.'),
        ('3', 'Anlık Tahmin', 'Aracınızın bilgilerini girin; model saniyeler içinde tahmini piyasa değerini ve güven aralığını hesaplar.'),
    ]
    return render(request, 'pages/hakkimizda.html', {
        'stats':       stats,
        'ozellikler':  ozellikler,
        'adimlar':     adimlar,
    })
