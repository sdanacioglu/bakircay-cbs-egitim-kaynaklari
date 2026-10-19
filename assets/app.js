/* Bakırçay CBS Eğitim Kaynakları — arama ve filtreleme */
(async function () {
  const $ = id => document.getElementById(id);
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fold = s => String(s || "").toLocaleLowerCase("tr").normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/ı/g, "i");

  let veri;
  try { veri = await (await fetch("data/kaynaklar.json", { cache: "no-cache" })).json(); }
  catch { $("liste").innerHTML = `<div class="card empty">Liste yüklenemedi. <a href="data/kaynaklar.csv">CSV dosyasını</a> indirebilirsin.</div>`; return; }
  const m = veri.meta;
  const kayitlar = veri.kaynaklar.map(k => ({ ...k, _ara: fold([k.ad, k.aciklama, k.konu, k.tur, k.hazirlayan, k.dil].join(" ")) }));

  $("stats").innerHTML = `
    <div><strong>${m.toplam}</strong><span>kaynak</span></div>
    <div><strong>${m.uye}</strong><span>üye kanalı</span></div>
    <div><strong>${m.turkce}</strong><span>Türkçe kaynak</span></div>
    <div><strong>${esc(m.son_baglanti_kontrolu)}</strong><span>son bağlantı kontrolü</span></div>`;
  $("guncelleme").textContent = `Liste güncellemesi: ${m.uretim_tarihi}`;

  const kart = (k, uye = false) => `
    <article class="card kaynak${uye ? " uye" : ""}">
      <div class="ust"><h3><a href="${esc(k.url)}" target="_blank" rel="noopener">${esc(k.ad)}</a></h3>
        ${k.uye_kanali === "Evet" ? '<span class="badge uye-rozet">BakırçayCBS üyesi</span>' : ""}
        ${k.durum === "erişilemiyor" ? '<span class="badge bad">erişilemiyor</span>' : k.durum === "kontrol edilemedi" ? '<span class="badge warn">kontrol edilemedi</span>' : ""}</div>
      ${k.aciklama ? `<p>${esc(k.aciklama)}</p>` : ""}
      <div class="etiketler">
        <span class="et kapsam">${esc(k.konu)}</span><span class="et">${esc(k.tur)}</span>
        <span class="et">${esc(k.dil)}</span>${k.seviye ? `<span class="et">${esc(k.seviye)}</span>` : ""}
        ${k.ucretsiz && k.ucretsiz !== "Evet" ? `<span class="et">Ücretsiz: ${esc(k.ucretsiz)}</span>` : ""}
      </div>
      <div class="alt"><span class="url">${esc(k.hazirlayan)}</span><span>${esc(k.url.replace(/^https?:\/\/(www\.)?/, "").split("/")[0])}</span></div>
    </article>`;

  const uyeler = kayitlar.filter(k => k.uye_kanali === "Evet" && k.durum !== "erişilemiyor");
  $("uyeler").innerHTML = uyeler.length ? uyeler.map(k => kart(k, true)).join("")
    : `<div class="card empty">İlk üye kanalı sen ol!</div>`;

  const say = alan => { const c = new Map(); kayitlar.forEach(k => { if (k[alan]) c.set(k[alan], (c.get(k[alan]) || 0) + 1); }); return [...c.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "tr")); };
  ["konu", "tur", "dil", "seviye"].forEach(a => { $(a).innerHTML = `<option value="">Tümü</option>` + say(a).map(([v, n]) => `<option value="${esc(v)}">${esc(v)} (${n})</option>`).join(""); });

  const alanlar = ["q", "konu", "tur", "dil", "seviye"], kutular = ["ucretsiz", "erisilemeyen"];
  const params = new URLSearchParams(location.search);
  alanlar.forEach(a => { if (params.has(a)) $(a).value = params.get(a); });
  kutular.forEach(a => { $(a).checked = params.get(a) === "1"; });

  const filtrele = () => {
    const q = fold($("q").value.trim()).split(/\s+/).filter(Boolean);
    const sonuc = kayitlar.filter(k =>
      ($("erisilemeyen").checked || k.durum !== "erişilemiyor") &&
      ["konu", "tur", "dil", "seviye"].every(a => !$(a).value || k[a] === $(a).value) &&
      (!$("ucretsiz").checked || k.ucretsiz === "Evet") && q.every(t => k._ara.includes(t)));
    $("sayac").textContent = `${sonuc.length} kaynak`;
    $("liste").innerHTML = sonuc.length ? sonuc.map(k => kart(k)).join("") : `<div class="card empty">Bu filtrelerle kaynak bulunamadı.</div>`;
    const p = new URLSearchParams();
    alanlar.forEach(a => { if ($(a).value) p.set(a, $(a).value); });
    kutular.forEach(a => { if ($(a).checked) p.set(a, "1"); });
    history.replaceState(null, "", p.toString() ? `?${p}` : location.pathname);
  };
  $("filters").addEventListener("input", filtrele);
  $("filters").addEventListener("change", filtrele);
  $("temizle").addEventListener("click", () => { alanlar.forEach(a => $(a).value = ""); kutular.forEach(a => $(a).checked = false); filtrele(); });
  $("paylas").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(location.href); $("paylas").textContent = "✅ Bağlantı kopyalandı"; } catch { prompt("Bağlantı:", location.href); }
    setTimeout(() => { $("paylas").textContent = "🔗 Bu listeyi paylaş"; }, 2000);
  });
  filtrele();
})();
