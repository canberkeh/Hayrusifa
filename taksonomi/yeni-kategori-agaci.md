# Yeni Kategori Ağacı — Öneri

Eski sitede içerik **129 kategori** ve **2.630 etikete** dağılmış durumda. Bu
kategorilerin çoğu ya çöp (`Genel` 279, `Hayru Şifa` 344, `Sağlık` 202,
`Tedavi` 153 — neredeyse her yazıda var, hiçbir şey ifade etmiyor) ya da
tek-yazılık SEO kategorileri (`Üsküdar akupunktur uzmanı`, `ozon tedavisi
randevu` vb. onlarca varyasyon).

Aşağıdaki yapı 588 yazının tamamını **tedavi yöntemine** göre bir ana başlığa,
sonra tutarlı bir **alt konuya** oturtuyor. Ayrıca her yazı bağımsız olarak
**hastalık/şikayet** ve **lokasyon** etiketleri taşıyor (çapraz filtreleme
için).

Uygulanmış hâli: `content/blog/<ana-kategori>/<alt-konu>/*.md`
Eşleme tablosu: `taksonomi/yazi-siniflandirma.csv`

---

## 1. Üst Seviye Bölümler

| # | Bölüm | Yazı | Açıklama |
|---|---|---:|---|
| 1 | **Tedavi Yöntemleri** | 569 | Kliniğin sunduğu ana yöntemler — her biri kendi hub sayfası |
| 2 | **Destekleyici Tedaviler** | 14 | Az içerikli tamamlayıcı yöntemler |
| 3 | **Diğer / Genel** | 5 | Sınıflandırılamayan genel doğal tedavi yazıları |

> Not: "Hastalıklar & Şikayetler" ayrı bir üst bölüm **değil** — her yazının
> birincil evi yöntemdir. Hastalık bazlı gezinme, `hastalik_etiketleri` ile
> kurulacak filtre/etiket sayfalarıyla sağlanır (bkz. bölüm 4).

---

## 2. Tedavi Yöntemleri (ana kategoriler)

| Ana kategori | slug | Yazı | Kısa tanım (hub sayfası için) |
|---|---|---:|---|
| **Hacamat (Kupa Terapisi)** | `hacamat` | 126 | Vakumlama + kontrollü kan alma ile detoks/dolaşım desteği |
| **Sülük Tedavisi (Hirudoterapi)** | `suluk-tedavisi` | 84 | Tıbbi sülük ile kan dolaşımı, ödem ve ağrı yönetimi |
| **Ozon Terapisi** | `ozon-terapisi` | 74 | Ozon-oksijen karışımıyla bağışıklık ve doku onarımı desteği |
| **Mezoterapi** | `mezoterapi` | 59 | Mikroenjeksiyonla cilt, saç ve bölgesel bakım |
| **Akupunktur** | `akupunktur` | 59 | Meridyen noktalarına iğne ile ağrı/stres/uyku düzenleme |
| **PRP Tedavisi** | `prp-tedavisi` | 41 | Kişinin kendi trombositten zengin plazmasıyla yenilenme |
| **Fonksiyonel Tıp** | `fonksiyonel-tip` | 25 | Kök-neden odaklı, kişiye özel kronik hastalık yönetimi |
| **Nöral Terapi** | `noral-terapi` | 21 | Lokal anestezikle vejetatif sinir sistemi regülasyonu |
| **Glutatyon Tedavisi** | `glutatyon` | 21 | Antioksidan / detoks / cilt aydınlatma amaçlı uygulama |
| **Proloterapi** | `proloterapi` | 20 | Bağ dokusu ve eklem ağrılarında rejeneratif enjeksiyon |
| **Mizaç Analizi** | `mizac-analizi` | 12 | Kişinin mizacına göre tedavi ve yaşam düzenlemesi |
| **Manuel Terapi** | `manuel-terapi` | 12 | Omurga/eklem kaynaklı ağrılarda elle uygulama teknikleri |
| **Aromaterapi** | `aromaterapi` | 10 | Esansiyel yağlarla ruhsal/bedensel destek |
| **Hicri Hacamat Günleri** | `hicri-hacamat-gunleri` | 5 | Hacamat için uygun günler takvimi (araç sayfası) |

### Destekleyici Tedaviler
`kolon-hidroterapi` (6) · `myers-kokteyl` (2) · `alfa-lipoik-asit` (2) ·
`fitoterapi` (2) · `medikal-masaj` (1) · `refleksoloji` (1)

### Diğer / Genel
`genel` (5) — "Alternatif Tıp: Doğal Şifa Yöntemleri", "Binlerce Yıllık Etkili
Tedavi Yöntemi" gibi tek bir yönteme bağlanamayan yazılar.

---

## 3. Alt Konular (her ana kategori içinde aynı şablon)

Yeni içeriğin büyük kısmı zaten şu kalıpları izliyor; bu yüzden her yöntem
sayfası aynı alt bölümlerle kurgulanabilir:

| Alt konu | slug | Ne içerir |
|---|---|---|
| Nedir / Genel Bilgi | `nedir-genel` | Tanım, temel prensipler, kapsamlı rehber |
| Faydaları | `faydalari` | Yararlar, katkılar, avantajlar, olumlu etkiler |
| Nasıl Uygulanır / Süreç | `uygulama-surec` | Adım adım, seans sayısı, teknikler, aşamalar |
| Hangi Hastalıklarda | `hangi-hastaliklar` | Endikasyonlar, "hangi durumlarda", "iyi gelir mi" |
| Kimler İçin Uygun | `kimler-icin-uygun` | Uygunluk, kontrendikasyonlar |
| Öncesi / Hazırlık | `oncesi-hazirlik` | Uygulama öncesi bilinmesi gerekenler |
| Sonrası / Bakım | `sonrasi-bakim` | Uygulama sonrası dikkat, iyileşme süreci |
| Yan Etkiler & Riskler | `yan-etkiler-riskler` | Güvenlik, komplikasyonlar |
| Bilimsel Temeller / Tarihçe | `bilimsel-tarihce` | Araştırmalar, geçmiş, modern tıpla ilişki |
| SSS | `sss` | Sık sorulan sorular |
| Fiyat | `fiyat` | Ücret/maliyet bilgisi |
| Yorumlar | `yorumlar` | Hasta deneyimleri |
| Genel Yazı | `genel-yazi` | Yukarıdaki kalıba tam oturmayan blog yazıları |

**Dolu alt konu dağılımı (başlıca yöntemler):**

```
hacamat (126)        genel-yazi 76 · faydalari 21 · bilimsel-tarihce 8 · sonrasi-bakim 6 · hangi-hastaliklar 5 · yan-etkiler 3 · nedir 3 · uygulama 2 · oncesi 2
suluk-tedavisi (84)  genel-yazi 35 · faydalari 16 · bilimsel-tarihce 7 · sonrasi-bakim 7 · hangi-hastaliklar 6 · yan-etkiler 6 · uygulama 3 · sss 2 · nedir 1 · kimler 1
ozon-terapisi (74)   genel-yazi 38 · faydalari 16 · yan-etkiler 7 · hangi-hastaliklar 4 · uygulama 4 · sonrasi-bakim 2 · bilimsel 2 · nedir 1
mezoterapi (59)      genel-yazi 29 · faydalari 8 · sonrasi-bakim 6 · yan-etkiler 5 · uygulama 4 · bilimsel 3 · nedir 2 · hangi-hastaliklar 1 · fiyat 1
akupunktur (59)      genel-yazi 32 · faydalari 10 · bilimsel-tarihce 9 · uygulama 3 · nedir 1 · oncesi 1 · sonrasi 1 · hangi-hastaliklar 1 · yan-etkiler 1
prp-tedavisi (41)    genel-yazi 24 · faydalari 5 · sonrasi-bakim 5 · fiyat 2 · uygulama 1 · bilimsel 1 · hangi-hastaliklar 1 · yan-etkiler 1 · nedir 1
```

> `genel-yazi` kovaları büyük; ikinci turda başlık + ilk paragraf okunarak
> daha ince ayrıştırılabilir. Şu hâliyle bile her yazı doğru **yöntem**
> altında.

---

## 4. Çapraz Etiketler

### Hastalık / Şikayet (`hastalik_etiketleri`) — `taksonomi/hastalik-index.json`

```
Ağrı 86 · Cilt 76 · Bağışıklık 23 · Depresyon/Anksiyete 23 · Kalp/Dolaşım 20 ·
Kronik Yorgunluk 20 · Migren 17 · Kronik Hastalıklar 16 · Saç Dökülmesi 15 ·
Stres 14 · Obezite/Zayıflama 13 · Diyabet 12 · Spor Yaralanmaları 11 ·
Detoks 9 · Hormon Bozukluğu 9 · Hormonal Denge 8 · Karaciğer 7 ·
Uyku Bozuklukları 6 · Varis 6 · Romatizma/Eklem 5 · Göz 4 · Kısırlık/Üreme 4 ·
Selülit 4 · Sindirim 4 · Otoimmün 3 · (+ ~12 tekil şikayet)
```

Öneri: bu etiketlerden **10-12 tanesi** için "Şikayetler" menüsünde landing
sayfası (örn. `/sikayet/agri/`, `/sikayet/migren/`) — içinde ilgili yazılar
yöntemden bağımsız listelenir.

### Lokasyon (`lokasyon_etiketleri`)

Yazı içinde geçen: **Üsküdar 206**, **Ümraniye 127**. (İstanbul/Kocaeli/Trabzon
sadece sayfa olarak var, yazı etiketi yok.) Lokasyon kararı `site-yapisi.md`
bölüm "Lokasyonlar"da tartışılıyor.

---

## 5. Eski → Yeni Eşleme Kuralları (özet)

| Eski WP kategorisi | Yeni karşılık |
|---|---|
| `Genel`, `Hayru Şifa`, `Sağlık`, `Tedavi` | **Atıldı** (sinyal yok) |
| `Hacamat`, `Kupa Tedavisi` | → `hacamat` |
| `Sülük Tedavisi`, `Hirudoterapi` | → `suluk-tedavisi` |
| `Ozon Terapisi` + `ozon tedavisi *` (10+ varyant) | → `ozon-terapisi` |
| `PRP Uygulaması` | → `prp-tedavisi` |
| `Mizaç Analizi`, `mizaç` | → `mizac-analizi` |
| `Hastalıklarda Tedavi / <alt>` (Ağrı, Cilt, Migren…) | → `hastalik_etiketleri` çapraz etiketi |
| `Üsküdar *`, `Ümraniye *` (40+ varyant) | → `lokasyon_etiketleri` çapraz etiketi |
| `Hicri Hacamat Günleri`, `Ağustos/Temmuz/Mayıs 2018` | → `hicri-hacamat-gunleri` |

Detaylı yazı-bazlı eşleme: **`taksonomi/yazi-siniflandirma.csv`**

---

## 6. Onay Bekleyen Kararlar

1. **Ana kategori isimleri** — yukarıdaki 14 + 6 + 1 liste onaylanıyor mu?
   Birleştirme isteği var mı? (örn. Glutatyon + Myers + Alfa Lipoik → "Serum /
   IV Tedaviler" tek başlık?)
2. **Alt konu şablonu** — 13 alt konu yeterli mi, yoksa sadeleştirilsin mi
   (örn. `oncesi-hazirlik` + `sonrasi-bakim` → tek "Hazırlık & Bakım")?
3. **`genel-yazi` kovaları** ikinci turda ayrıştırılsın mı?
4. **Hastalık landing sayfaları** — hangileri menüye girsin?
5. **Lokasyon** — bkz. `site-yapisi.md`.
