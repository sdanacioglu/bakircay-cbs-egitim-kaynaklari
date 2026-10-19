"""data/kaynaklar.csv dosyasından data/kaynaklar.json ve README.md üretir.

Kullanım:  python scripts/build.py
Hata varsa (eksik zorunlu alan, tekrar eden id/URL) çıkış kodu 1 olur ve hiçbir dosya yazılmaz.
"""
import datetime as dt
import json
import sys
from collections import Counter

from ortak import KOK, SUTUNLAR, ZORUNLU, oku

BASLIK = "Bakırçay CBS Eğitim Kaynakları"
SITE = "https://sdanacioglu.github.io/bakircay-cbs-egitim-kaynaklari/"
DEPO = "https://github.com/sdanacioglu/bakircay-cbs-egitim-kaynaklari"
YIL = "2026"
ATIF = (f"Danacıoğlu, Ş. ({YIL}). *{BASLIK}* [Çevrim içi kaynak listesi]. "
        f"İzmir Bakırçay Üniversitesi Coğrafi Bilgi Sistemleri Topluluğu. {DEPO}")


def norm_url(u):
    u = u.lower().strip()
    for p in ("https://", "http://"):
        if u.startswith(p):
            u = u[len(p):]
    return u.removeprefix("www.").rstrip("/")


def dogrula(satirlar):
    hatalar = []
    for i, s in enumerate(satirlar, start=2):
        hatalar += [f"{i}. satır: '{k}' boş ({s['ad'] or s['url']})" for k in ZORUNLU if not s[k]]
    for alan, f in (("id", lambda s: s["id"]), ("url", lambda s: norm_url(s["url"]))):
        c = Counter(f(s) for s in satirlar if s[alan])
        hatalar += [f"Tekrar eden {alan}: {k}" for k, n in c.items() if n > 1]
    return hatalar


def md(t):
    return t.replace("|", "\\|").replace("\n", " ")


def tablo(satirlar):
    sat = [f"| [{md(s['ad'])}]({s['url']}) | {md(s['tur'])} | {md(s['konu'])} | {md(s['dil'])} | {md(s['seviye'])} | {md(s['aciklama'])} |"
           for s in satirlar]
    return "\n".join(["| Ad | Tür | Konu | Dil | Seviye | Açıklama |", "|---|---|---|---|---|---|", *sat])


def main():
    satirlar = oku()
    hatalar = dogrula(satirlar)
    if hatalar:
        print("❌ Doğrulama hataları:\n  " + "\n  ".join(hatalar))
        sys.exit(1)

    satirlar.sort(key=lambda s: (s["uye_kanali"] != "Evet", s["dil"] != "Türkçe", s["konu"], s["ad"].lower()))
    bugun = dt.date.today().isoformat()
    gorunen = [s for s in satirlar if s["durum"] != "erişilemiyor"]
    uye = [s for s in gorunen if s["uye_kanali"] == "Evet"]
    diger = [s for s in gorunen if s["uye_kanali"] != "Evet"]
    son_kontrol = max((s["son_kontrol"] for s in satirlar if s["son_kontrol"]), default="—")
    meta = {
        "baslik": BASLIK, "uretim_tarihi": bugun, "son_baglanti_kontrolu": son_kontrol,
        "toplam": len(satirlar), "aktif": sum(s["durum"] == "aktif" for s in satirlar),
        "uye": len(uye), "turkce": sum("Türkçe" in s["dil"] for s in gorunen), "sutunlar": SUTUNLAR,
    }
    (KOK / "data" / "kaynaklar.json").write_text(
        json.dumps({"meta": meta, "kaynaklar": satirlar}, ensure_ascii=False, indent=1), encoding="utf-8")

    readme = f"""# {BASLIK}

**Hazırlayan:** Dr. Şevki Danacıoğlu · İzmir Bakırçay Üniversitesi Coğrafi Bilgi Sistemleri Topluluğu (BakırçayCBS), {YIL}

CBS, kartografya ve uzaktan algılama öğrenmek isteyenler için sürekli güncellenen eğitim kaynakları listesi.

### 🔎 [Listede ara ve filtrele →]({SITE})

| | |
|---|---|
| Toplam kaynak | **{len(satirlar)}** |
| Topluluk üyelerimizin kanalları | **{len(uye)}** |
| Türkçe kaynak | **{meta['turkce']}** |
| Son bağlantı kontrolü | {son_kontrol} |

**Veriyi indir:** [CSV](data/kaynaklar.csv) · [JSON](data/kaynaklar.json)

## 🎓 Topluluk üyelerimizin kanalları

BakırçayCBS üyelerinin hazırladığı içerikler. Kanal açan üyelerimizi desteklemek için bu bölüm her zaman en üstte yer alır.
Sen de içerik üretiyorsan [buradan bildir]({DEPO}/issues/new?template=kaynak-oner.yml).

{tablo(uye) if uye else "_Henüz kayıt yok._"}

## 📚 Diğer kaynaklar

{tablo(diger)}
"""
    (KOK / "README.md").write_text(readme, encoding="utf-8")
    print(f"✅ {len(satirlar)} kayıt · üye {len(uye)} · Türkçe {meta['turkce']}")


if __name__ == "__main__":
    main()
