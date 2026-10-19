"""Bakırçay CBS Eğitim Kaynakları — ortak CSV okuma/yazma yardımcıları."""
import csv
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
CSV_YOLU = KOK / "data" / "kaynaklar.csv"

SUTUNLAR = [
    "id",               # benzersiz kısa ad (küçük harf, tire)
    "ad",               # kaynağın adı
    "url",              # bağlantı
    "aciklama",         # kısa Türkçe açıklama
    "tur",              # Video kanalı / Video listesi / Öğrenme yolu / Eğitim platformu / Kitap / Kılavuz / Makale / Katalog
    "konu",             # QGIS / ArcGIS / R / Python / Kartografya / Uzaktan algılama / Web haritalama / 3B görselleştirme / Genel CBS
    "dil",              # Türkçe / İngilizce / Türkçe ve İngilizce
    "seviye",           # Başlangıç / Orta / İleri / Her seviye
    "ucretsiz",         # Evet / Kısmen / Hayır
    "hazirlayan",       # kanal sahibi, yazar ya da kurum
    "uye_kanali",       # Evet → BakırçayCBS topluluk üyesinin içeriği (öne çıkarılır)
    "kaynak_listesi",   # BakırçayCBS / 30DayMapChallenge
    "eklenme_tarihi",   # YYYY-AA-GG
    "son_kontrol",      # otomatik
    "durum",            # otomatik: aktif / kontrol edilemedi / erişilemiyor / arşiv
    "http_kodu",        # otomatik
    "hata_sayisi",      # otomatik
    "kontrol_disi",     # Evet → otomatik bağlantı kontrolü yapılmaz
]

ZORUNLU = ["id", "ad", "url", "tur", "konu", "dil"]


def oku(yol=CSV_YOLU):
    with open(yol, newline="", encoding="utf-8-sig") as f:
        satirlar = list(csv.DictReader(f))
    for s in satirlar:
        for k in SUTUNLAR:
            s[k] = (s.get(k) or "").strip()
    return satirlar


def yaz(satirlar, yol=CSV_YOLU):
    yol.parent.mkdir(parents=True, exist_ok=True)
    with open(yol, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=SUTUNLAR, extrasaction="ignore")
        w.writeheader()
        for s in satirlar:
            w.writerow({k: s.get(k, "") for k in SUTUNLAR})
