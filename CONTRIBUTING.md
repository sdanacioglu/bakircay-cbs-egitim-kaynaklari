# Katkı rehberi

## Kaynak önermek ya da üye kanalını bildirmek
[Kaynak öner](https://github.com/sdanacioglu/bakircay-cbs-egitim-kaynaklari/issues/new?template=kaynak-oner.yml) formunu doldurun
ya da **bakircaycbs@gmail.com** adresine yazın. BakırçayCBS üyelerinin kanalları ve içerikleri listenin en üstünde ayrıca gösterilir.

## Listeyi doğrudan güncellemek (bakımcılar)
1. Tek doğruluk kaynağı **`data/kaynaklar.csv`** dosyasıdır (UTF-8). GitHub'da ✏️ ile düzenleyebilir ya da Excel'de açıp **UTF-8 CSV** olarak kaydedebilirsiniz.
2. Zorunlu alanlar: `id`, `ad`, `url`, `tur`, `konu`, `dil`. Topluluk üyesinin içeriği için `uye_kanali` = `Evet`.
3. `son_kontrol`, `durum`, `http_kodu`, `hata_sayisi` alanlarını boş bırakın; otomatik doldurulur.
4. Kaydettiğinizde GitHub Actions README'yi, JSON'u ve arama sayfasını yeniden üretir.

| Alan | Değerler |
|---|---|
| `tur` | Video kanalı · Video listesi · Öğrenme yolu · Eğitim platformu · Kitap · Kılavuz · Makale · Katalog |
| `konu` | QGIS · ArcGIS · R · Python · Kartografya · Uzaktan algılama · Web haritalama · 3B görselleştirme · Genel CBS |
| `dil` | Türkçe · İngilizce · Türkçe ve İngilizce |
| `seviye` | Başlangıç · Orta · İleri · Her seviye |
| `ucretsiz` | Evet · Kısmen · Hayır |
| `uye_kanali` | Evet (BakırçayCBS üyesinin içeriği) ya da boş |
