"""Tüm bağlantıları kontrol eder ve data/kaynaklar.csv içindeki durum sütunlarını günceller.

Kullanım:
    python scripts/check_links.py            # aylık otomatik kontrol (GitHub Actions)
    python scripts/check_links.py --kesin    # ilk kontrol: kesin hatayı hemen "erişilemiyor" say

Kurallar (yanlış alarmı azaltmak için temkinli):
  * 2xx/3xx, 401, 403, 405, 429 → aktif (site yanıt veriyor; bot korumaları 403 dönebilir)
  * 404, 410 ya da alan adı bulunamadı → kesin hata; art arda 2 kontrolde → "erişilemiyor"
  * zaman aşımı, 5xx, SSL vb. → geçici hata; art arda 3 kontrolde → "erişilemiyor", öncesinde "kontrol edilemedi"
  * .tr alan adları yurt dışından engellenebildiği için yalnızca kesin hata (404/410) ile düşer
  * kontrol_disi = Evet olan kayıtlar atlanır; durum = arşiv olanların durumu değiştirilmez
"""
import argparse
import datetime as dt
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from ortak import KOK, oku, yaz

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 BakircayCBS-LinkCheck")
ZAMAN_ASIMI = 25
AKTIF_KODLAR = {401, 403, 405, 429}
KESIN_KODLAR = {404, 410}


def _istek(url, yontem, dogrula=True):
    ctx = ssl.create_default_context() if dogrula else ssl._create_unverified_context()
    req = urllib.request.Request(url, method=yontem, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=ZAMAN_ASIMI, context=ctx) as r:
        return r.status


def kontrol(url):
    """(sınıf, kod) döndürür. sınıf: ok | kesin | gecici"""
    for dogrula in (True, False):
        for yontem in ("HEAD", "GET"):
            try:
                return "ok", str(_istek(url, yontem, dogrula))
            except urllib.error.HTTPError as e:
                if e.code in KESIN_KODLAR and yontem == "GET":
                    return "kesin", str(e.code)
                if e.code in AKTIF_KODLAR and yontem == "GET":
                    return "ok", str(e.code)
                son = ("gecici", str(e.code))
            except urllib.error.URLError as e:
                neden = e.reason
                if isinstance(neden, socket.gaierror):
                    return "kesin", "DNS"
                if isinstance(neden, ssl.SSLError) and dogrula:
                    son = ("gecici", "SSL")
                    break  # doğrulamasız dene
                son = ("gecici", type(neden).__name__ if not isinstance(neden, str) else neden[:20])
            except (TimeoutError, socket.timeout):
                son = ("gecici", "zaman aşımı")
            except Exception as e:  # noqa: BLE001
                son = ("gecici", type(e).__name__)
    return son


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kesin", action="store_true", help="kesin hatayı ilk seferde 'erişilemiyor' say")
    ap.add_argument("--is-parcacigi", type=int, default=24)
    args = ap.parse_args()

    satirlar = oku()
    bugun = dt.date.today().isoformat()
    hedef = [s for s in satirlar if s["kontrol_disi"].lower() != "evet"]
    with ThreadPoolExecutor(max_workers=args.is_parcacigi) as ex:
        sonuclar = list(ex.map(lambda s: kontrol(s["url"]), hedef))

    for s, (sinif, kod) in zip(hedef, sonuclar):
        s["son_kontrol"], s["http_kodu"] = bugun, kod
        arsiv = s["durum"] == "arşiv"
        if sinif == "ok":
            s["hata_sayisi"] = "0"
            if not arsiv:
                s["durum"] = "aktif"
            continue
        n = int(s["hata_sayisi"] or 0) + 1
        s["hata_sayisi"] = str(n)
        if arsiv:
            continue
        tr = urllib.parse.urlparse(s["url"]).hostname or ""
        tr = tr.endswith(".tr")
        if sinif == "kesin" and (args.kesin or n >= 2):
            s["durum"] = "erişilemiyor"
        elif sinif == "gecici" and n >= 3 and not tr:
            s["durum"] = "erişilemiyor"
        else:
            s["durum"] = s["durum"] if s["durum"] == "erişilemiyor" else "kontrol edilemedi"

    yaz(satirlar)

    sorunlu = [s for s in satirlar if s["durum"] in ("erişilemiyor", "kontrol edilemedi")]
    rapor = KOK / "reports" / "baglanti_raporu.md"
    rapor.parent.mkdir(exist_ok=True)
    with open(rapor, "w", encoding="utf-8") as f:
        f.write(f"# Bağlantı raporu ({bugun})\n\n")
        say = {}
        for s in satirlar:
            say[s["durum"]] = say.get(s["durum"], 0) + 1
        f.write("| Durum | Kayıt |\n|---|---|\n" + "".join(f"| {k} | {v} |\n" for k, v in sorted(say.items())))
        f.write("\n## Sorunlu bağlantılar\n\n| Ad | URL | Durum | Kod | Art arda hata |\n|---|---|---|---|---|\n")
        for s in sorted(sorunlu, key=lambda x: (x["durum"], x["ad"].lower())):
            f.write(f"| {s['ad']} | {s['url']} | {s['durum']} | {s['http_kodu']} | {s['hata_sayisi']} |\n")
    print(f"Kontrol edilen: {len(hedef)} · " + " · ".join(f"{k}: {v}" for k, v in sorted(say.items())))


if __name__ == "__main__":
    main()
