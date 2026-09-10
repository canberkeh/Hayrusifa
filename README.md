# Hayru Şifa — Web Sitesi Yenileme Projesi

Eski site `https://hayrusifa.com.tr/` (WordPress) tamamen tarandı, tüm içerik
metin olarak toplandı ve yeni bir temiz kategori yapısına göre yeniden
düzenlendi. Bu klasör, yeni sitenin (düz HTML/CSS) içerik kaynağıdır.

> **Durum:** İçerik toplama + kategorilendirme + statik site tamam.
> **Yayında:** https://canberkeh.github.io/Hayrusifa/ (GitHub Pages, `gh-pages` branch).
> Repo: https://github.com/canberkeh/Hayrusifa (public).

## Yayın / Deploy

- **Kaynak:** `main` branch — proje kökü mutlak yollar (`/assets`, `/blog`) kullanır,
  hedef `hayrusifa.com.tr` kökü içindir.
- **GitHub Pages:** `gh-pages` branch — `crawl/scripts/deploy-ghpages.sh` çalıştırılır;
  site'ı yeniden üretir, yolları `/Hayrusifa/` ile önekler (proje-sitesi alt yolu),
  `gh-pages` branch'e force-push eder. Pages 1-2 dk'da güncellenir.
  ```
  bash crawl/scripts/deploy-ghpages.sh
  ```
- **Otomatik deploy (opsiyonel):** `.github/pages.yml.disabled` hazır bir GitHub
  Actions workflow'u. Aktifleştirmek için: `gh auth refresh -s workflow` çalıştır,
  sonra dosyayı `.github/workflows/pages.yml`e taşıyıp push et — her `main` push'ında
  `site/` otomatik yayınlanır (bu durumda Pages kaynağını "GitHub Actions" yap).
- **Gerçek alan adı (`hayrusifa.com.tr`):** `site/` klasörünün içeriği doğrudan
  domain köküne konur; yol öneki gerekmez.

## Üretilen Site (`site/`)

Düz HTML/CSS/JS. Framework yok. `crawl/scripts/build_site.py` ile üretilir.

| Sayfa türü | Adet | Yol |
|---|---|---|
| Anasayfa | 1 | `site/index.html` |
| Blog ana sayfası (kategori vitrini) | 1 | `site/blog/index.html` |
| Tüm yazılar (aranabilir/süzülebilir liste) | 1 | `site/blog/tum-yazilar.html` |
| Kategori sayfaları (yönteme göre, alt konu gruplu) | 21 | `site/blog/<yöntem>/index.html` |
| Blog yazısı | 588 | `site/blog/<yöntem>/<slug>.html` |
| Kurumsal (hakkımızda, ekibimiz, hasta-yorumları, iletişim) | 4 | `site/*.html` |
| Hicri Hacamat Günleri, 404 | 2 | `site/*.html` |
| + `sitemap.xml`, `robots.txt`, `_redirects` (eski slug → yeni URL 301) | | |

**Önizleme:** `cd site && python3 -m http.server 8000` → `http://localhost:8000`
(mutlak yollar kullanıldığı için `file://` ile açılmaz, sunucu gerekir).

**Tasarım:** `crawl/scripts/site.css` (tek stylesheet) · `crawl/scripts/site.js`
(mobil menü + yazı süzme). Wix **"Pilates Studio (Refined)" (wh-1323)** şablonu
referans alındı (şablonun kendi header'ı — Wix editör sarmalayıcısı değil):
- **Header:** açık fıstık yeşili (lime `#e8f97f`) bar, ortada/sağda menü, sağda
  koyu lacivert "Randevu" butonu
- **Hero:** bölünmüş — koyu lacivert (`#1e2a38`) metin paneli + görsel, ince
  lime lotus motifi
- **Tipografi:** Space Grotesk (başlık, sıkı/kalın) + Inter (gövde), logo
  Cormorant Garamond
- **Palet:** lacivert + lime + sıcak kırık beyaz (`#f7f5ef`) + adaçayı
- Butonlar küçük köşe yarıçapı, koyu lacivert
- Anasayfa hero görseli: `HERO_IMAGE` sabiti (`build_site.py` içinde) —
  `/assets/img/` altındaki başka bir dosyayla değiştirilebilir

**Blog artık tek çatı altında:** `/blog/` sayfası 14 ana yöntemi kart olarak
gösteriyor (yazı sayısıyla); her `/blog/<yöntem>/` sayfası o yöntemin yazılarını
alt konulara (Nedir, Faydaları, Nasıl Uygulanır, Yan Etkiler, …) gruplanmış
listeliyor. Dağınık yapı bitti.

**İletişim bilgileri (gerçek, `build_site.py` içindeki `CONTACT`):**
Bulgurlu Mah. Ünlü Sokak No:5 Kat:2 Ofis:2, 34696 Üsküdar/İstanbul ·
Tel 0216 316 00 64 · WhatsApp +90 532 470 97 67 · hayrusifa@gmail.com ·
Pzt–Prş & Pazar 09:00–18:30, Cuma–Cmt kapalı ·
Harita: https://maps.app.goo.gl/eBBBSeUwsq3PuK1CA
İletişim sayfasında **form yok**; telefon/WhatsApp/e-posta + Google Maps embed
+ "Haritalar'da aç" linki var. (Harita embed karoları localhost'ta boş görünür,
yayına alınınca render olur; goo.gl linki her yerde çalışır.)

**Bilinen eksikler:** boş kurumsal sayfalar (doktorumuz/ekibimiz/hasta-yorumları)
"içerik hazırlanıyor" notlu; ~12 eski yazıda öne çıkan görsel yok (kategori
etiketli placeholder); yazı içi eski dahili linkler henüz yeni URL'lere
map'lenmedi.

---

## Özet Rakamlar

| Öğe | Adet |
|---|---|
| Blog yazısı (toplandı) | **588** |
| Kurumsal / hizmet sayfası | **24** |
| Eski WordPress kategorisi | 129 (118'i dolu) |
| Eski WordPress etiketi | 2.630 |
| İndirilen görsel | 639 / 707 URL (kalan 68 = zaten inen varyantın kopyası; kaynakta ölü tek görsel: 1) |
| İçerik tarih aralığı | 2002 – 2025 (yoğunluk: 2024'te 378, 2018'de 74, 2025'te 74 yazı) |

Eski sitenin **şu anki hâli zaten iskelet** (Elementor ile kurulu birçok sayfa
boş; anasayfadaki WhatsApp numarası `905551234567` gibi placeholder veriler
var). Bu yüzden asıl değerli içerik **588 blog yazısıdır**; kurumsal sayfaların
çoğu sıfırdan yazılacak.

---

## Klasör Yapısı

```
hayrusifa/
├── README.md                  ← bu dosya
├── site-yapisi.md             ← YENİ sitenin sayfa haritası / IA önerisi
│
├── content/
│   ├── blog/                  ← 588 yazı, YENİ kategori ağacına göre klasörlenmiş
│   │   ├── _ham/              ← tüm yazıların düz (kategorisiz) yedeği — 588 .md
│   │   ├── hacamat/
│   │   │   ├── faydalari/
│   │   │   ├── nedir-genel/
│   │   │   ├── uygulama-surec/
│   │   │   ├── yan-etkiler-riskler/
│   │   │   └── ...            ← alt konu klasörleri
│   │   ├── suluk-tedavisi/
│   │   ├── ozon-terapisi/
│   │   ├── mezoterapi/
│   │   ├── akupunktur/
│   │   ├── prp-tedavisi/
│   │   ├── fonksiyonel-tip/  · noral-terapi/ · glutatyon/ · proloterapi/
│   │   ├── mizac-analizi/    · manuel-terapi/ · aromaterapi/
│   │   ├── kolon-hidroterapi/ · myers-kokteyl/ · alfa-lipoik-asit/
│   │   ├── fitoterapi/ · refleksoloji/ · medikal-masaj/
│   │   ├── hicri-hacamat-gunleri/
│   │   └── genel/
│   ├── pages/                 ← 24 kurumsal/hizmet sayfası (.md) + _SAYFA-ENVANTERI.md
│   └── lokasyon/              ← (ayrılmış; lokasyon içeriği kararı bekliyor)
│
├── media/
│   ├── images/               ← indirilen görseller (md5-önekli dosya adları)
│   ├── gorsel-manifest.json  ← orijinal URL → yerel dosya eşlemesi
│   └── gorsel-url-listesi.txt
│
├── taksonomi/
│   ├── yeni-kategori-agaci.md      ← ÖNERİLEN temiz yapı (ana başlık > alt konu)
│   ├── yazi-siniflandirma.csv      ← her yazı → yeni bölüm / kategori / alt konu / hastalık / lokasyon
│   ├── yazi-siniflandirma.json
│   ├── hastalik-index.json         ← hastalık/şikayet → yazı slug listesi
│   ├── eski-kategoriler.json       ← eski WP kategori ağacı + gerçek yazı sayıları
│   └── eski-etiketler.json         ← 2.630 etiket + kullanım sayısı
│
└── crawl/                     ← ham veri (yeniden üretilebilir)
    ├── wp-api/                ← WordPress REST API JSON dökümleri (posts, pages, categories, tags)
    ├── raw-html/             ← Elementor sayfalarının ham HTML'i
    ├── icerik-index.json     ← tüm içeriğin düz indeksi (başlık, tarih, kelime sayısı, görsel sayısı)
    └── sitemap-urls.json
```

---

## Her Markdown Dosyasının Formatı

YAML frontmatter + Markdown gövde:

```yaml
---
baslik: "Hacamat Nedir Ve Hangi Hastalıklarda Uygulanır?"
slug: "hacamat-nedir-ve-hangi-hastaliklarda-uygulanir"
tur: "yazi"
kaynak_url: "https://hayrusifa.com.tr/hacamat-nedir-ve-hangi-hastaliklarda-uygulanir/"
yayin_tarihi: "2002-01-29T11:24:09"
guncelleme_tarihi: "2018-03-29T11:33:02"
wp_kategoriler: [...]            # eski WP kategorileri (referans)
wp_etiketler: [...]              # eski WP etiketleri (referans)
meta_aciklama: "..."             # Yoast meta description
ozet: "..."                      # WP excerpt
one_cikan_gorsel: "https://..."
gorseller: [...]                 # yazıdaki tüm görsel URL'leri
kelime_sayisi: 529
# --- yeniden düzenleme sırasında eklenen alanlar ---
yeni_bolum: "Tedavi Yöntemleri"
yeni_ana_kategori: "Hacamat (Kupa Terapisi)"
yeni_ana_kategori_slug: "hacamat"
yeni_alt_konu: "nedir-genel"
hastalik_etiketleri: [...]
lokasyon_etiketleri: [...]
---

## Hacamat Nasıl Bir Tedavidir?
... (temiz Markdown gövde) ...
```

---

## Nasıl Yeniden Üretilir

`scratchpad/` içindeki scriptler (bu klasöre kopyalanabilir):

1. `fetch_wp.py`        — REST API'den posts/pages/categories/tags/users çeker → `crawl/wp-api/`
2. `build_content.py`   — JSON → `content/blog/_ham/` + `content/pages/` markdown + `taksonomi/eski-*.json`
3. `fetch_pages_html.py`— Elementor sayfalarının HTML'ini çeker → `crawl/raw-html/`
4. `classify.py`        — yeni taksonomiyi uygular, `content/blog/<kategori>/<alt-konu>/` ağacını kurar
5. `dl_images.py`       — `media/gorsel-url-listesi.txt` içindeki görselleri indirir

---

## Sıradaki Adımlar (kullanıcı kararı bekleyen)

- [ ] Yeni kategori ağacının onayı → `taksonomi/yeni-kategori-agaci.md`
- [ ] Lokasyon/SEO sayfaları ne olacak? (Üsküdar 206, Ümraniye 127 yazı etiketli)
- [ ] Kurumsal bilgiler: gerçek adres, telefon, e-posta, doktor/ekip bilgileri (eski sitede yok)
- [ ] Tasarım yönü belirlenince düz HTML/CSS şablonları
