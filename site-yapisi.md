# Yeni Site — Sayfa Haritası / Bilgi Mimarisi Önerisi

Düz HTML/CSS ile kurulacak. Tasarım henüz netleşmedi; bu belge **sayfa
yapısını ve URL şemasını** öneriyor. İçerik kaynağı: `content/`.

---

## 1. Üst Menü (önerilen)

```
Anasayfa
Tedavi Yöntemleri ▾        Şikayetler ▾           Kurumsal ▾         İletişim
  ├ Hacamat                  ├ Ağrı                  ├ Kliniğimiz        (+ Randevu butonu)
  ├ Sülük Tedavisi           ├ Migren               ├ Doktorumuz
  ├ Ozon Terapisi            ├ Cilt Sorunları       ├ Ekibimiz
  ├ Mezoterapi               ├ Saç Dökülmesi        ├ Terapistlerimiz
  ├ Akupunktur               ├ Kronik Yorgunluk     ├ Hasta Yorumları
  ├ PRP Tedavisi             ├ Stres & Uyku         ├ Blog
  ├ Fonksiyonel Tıp          ├ Diyabet              └ Hicri Hacamat Günleri
  ├ Nöral Terapi             ├ Kilo / Zayıflama
  ├ Glutatyon                ├ Bağışıklık & Detoks
  ├ Proloterapi              └ Eklem & Romatizma
  ├ Mizaç Analizi
  ├ Manuel Terapi
  ├ Aromaterapi
  └ Diğer Yöntemler ▾ (Kolon Hidroterapi, Myers Kokteyl,
      Alfa Lipoik Asit, Fitoterapi, Refleksoloji, Medikal Masaj)
```

---

## 2. URL Şeması

| Tip | URL | Kaynak |
|---|---|---|
| Anasayfa | `/` | `content/pages/sistem/anasayfa.md` (yeniden yazılacak) |
| Yöntem hub | `/tedavi/<slug>/` | `content/blog/<slug>/` + `content/pages/hizmet-sayfalari/` |
| Yöntem alt konu | `/tedavi/<slug>/<alt-konu>/` | `content/blog/<slug>/<alt-konu>/` |
| Blog yazısı | `/blog/<yazi-slug>/` | ilgili `.md` (kanonik URL burası) |
| Şikayet sayfası | `/sikayet/<slug>/` | `taksonomi/hastalik-index.json` |
| Kurumsal | `/kurumsal/<slug>/` | `content/pages/kurumsal/` |
| İletişim | `/iletisim/` | yeni |
| Randevu | `/randevu/` | yeni form |

> Not: Eski yazı URL'leri (`hayrusifa.com.tr/<slug>/`) tek düzey. SEO kaybı
> olmaması için ya aynı düz şema korunmalı ya da eski URL'lerden yenilere
> **301 yönlendirme** listesi çıkarılmalı. Tüm eski URL'ler
> `crawl/wp-api/posts.json` ve `crawl/sitemap-urls.json` içinde mevcut.

---

## 3. Yöntem Hub Sayfası Şablonu

Her yöntem için tek bir uzun sayfa; içindeki bölümler alt-konu kovalarından
beslenir:

```
<Yöntem> Nedir?              ← nedir-genel
Faydaları                    ← faydalari
Hangi Hastalıklarda Uygulanır ← hangi-hastaliklar  (+ ilgili şikayet sayfalarına link)
Nasıl Uygulanır / Süreç      ← uygulama-surec, oncesi-hazirlik
Uygulama Sonrası             ← sonrasi-bakim
Yan Etkiler & Güvenlik       ← yan-etkiler-riskler
Kimler İçin Uygundur         ← kimler-icin-uygun
Bilimsel Temeller & Tarihçe  ← bilimsel-tarihce
Sık Sorulan Sorular          ← sss
İlgili Yazılar               ← genel-yazi (liste)
Randevu / İletişim CTA
```

---

## 4. Kurumsal Sayfalar — Durum

`content/pages/_SAYFA-ENVANTERI.md` tam listeyi tutuyor. Özet:

| Sayfa | Durum | Aksiyon |
|---|---|---|
| `anasayfa` | dolu (placeholder) | Yeniden yazılacak — gerçek CTA, hizmet vitrini |
| `klinigimiz` | dolu (~900 krktr) | Redakte edilip kullanılabilir |
| `suluk-terapi`, `medikal-masaj`, `refleksoloji`, `mizaca-gore-tedavi` | dolu | Yöntem hub'larına taşınacak |
| `tam-kan-testi`, `kocaeli`, `trabzon` | kısa | Genişletilecek |
| `doktorumuz`, `ekibimiz`, `terapistlerimiz`, `hasta-yorumlari`, `iletisim`, `hacamat`, `hastaliklarda-tedaviler`, `blog`, `home-ver2` | **BOŞ** | Sıfırdan yazılacak — bilgi sahibinden alınacak |
| `magaza` | boş | Mağaza tutulacak mı? (karar) |

**Eski sitede bulunamayan, sahipten istenecek bilgiler:**
- Gerçek adres(ler), telefon, WhatsApp, e-posta (anasayfadaki `905551234567` sahte)
- Doktor adı, unvanı, özgeçmiş; ekip/terapist listesi
- Gerçek hasta yorumları / referanslar
- Çalışma saatleri, harita konumu

---

## 5. Lokasyonlar — Karar İçin

Durum:
- Yazı içinde geçen lokasyon etiketi: **Üsküdar 206**, **Ümraniye 127**
  (`lokasyon_etiketleri`).
- Sayfa olarak: `istanbul`, `kocaeli`, `trabzon` (hepsi kısa/placeholder).
- Eski sitede **40+ "Üsküdar <hizmet>" / "Ümraniye <hizmet>" SEO kategorisi**
  ve onlarca aynı amaçlı sayfa/etiket var — hepsi tekrar içerik.

**Öneri:** Tek bir **"Bölgeler / Şubeler"** yapısı:
```
/bolge/uskudar/    → klinik bilgisi + o bölgede sunulan yöntemler listesi
/bolge/umraniye/
```
Yöntem sayfalarında "Üsküdar ve Ümraniye'de hizmet veriyoruz" notu yeterli;
her yöntem × her ilçe için ayrı sayfa **üretilmeyecek**. Bu, 45 zayıf sayfayı
2 güçlü sayfaya indirir.

> Kesin karar kullanıcıya ait. Alternatif: SEO trafiği önemliyse en çok
> aranan 4-5 kombinasyon (`Üsküdar Hacamat`, `Üsküdar Mezoterapi`,
> `Ümraniye Hacamat`, `Üsküdar Akupunktur`, `Üsküdar PRP`) için özel sayfa
> tutulup gerisi konsolide edilir.

---

## 6. Ek Bileşenler

- **Hicri Hacamat Günleri** — güncel yıl için takvim sayfası + kısa açıklama.
  Eski içerik 2018 tarihli, güncellenmeli.
- **Blog** — tüm 588 yazı; yönteme + şikayete göre filtreli liste.
- **Arama** — statik site için basit client-side index (Lunr.js benzeri) veya
  yöntem/şikayet filtreleri.
- **301 yönlendirme haritası** — eski slug → yeni URL (build sırasında CSV'den).
