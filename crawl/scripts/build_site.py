#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hayru Şifa — statik site üreticisi.
Girdi:  content/ , taksonomi/ , crawl/wp-api/ , media/
Çıktı:  site/  (düz HTML/CSS/JS)
Tasarım: Wix "Pilates Studio (Refined)" şablonundan esinlenen sakin wellness estetiği.
"""
import json, os, re, shutil, html, datetime, unicodedata
from urllib.parse import unquote
from collections import defaultdict, OrderedDict
from bs4 import BeautifulSoup

ROOT = "/Users/crea/Desktop/hayrusifa"
SITE = f"{ROOT}/site"
POSTS = json.load(open(f"{ROOT}/crawl/wp-api/posts.json", encoding="utf-8"))
PAGES = json.load(open(f"{ROOT}/crawl/wp-api/pages.json", encoding="utf-8"))
CLS = json.load(open(f"{ROOT}/taksonomi/yazi-siniflandirma.json", encoding="utf-8"))
IDX = {r["slug"]: r for r in json.load(open(f"{ROOT}/crawl/icerik-index.json", encoding="utf-8"))}
MANIFEST = json.load(open(f"{ROOT}/media/gorsel-manifest.json", encoding="utf-8"))
PAGES_HTML = json.load(open(f"{ROOT}/crawl/pages-html-extract.json", encoding="utf-8"))

SITE_NAME = "Hayru Şifa"
SITE_TAG = "Doğal ve Tamamlayıcı Tedaviler"
# anasayfa hero görseli (istenirse başka bir /assets/img/ dosyasıyla değiştirilebilir)
HERO_IMAGE = "/assets/img/0723d748__akupunktur-ile-stres-ve-anksiyete-yonetimi.jpg"
BASE_URL = "https://hayrusifa.com.tr"
CONTACT = {
    "adres_satirlar": ["Bulgurlu Mahallesi", "Ünlü Sokak No:5, Kat:2, Ofis:2",
                       "34696 Üsküdar / İstanbul"],
    "adres": "Bulgurlu Mahallesi, Ünlü Sokak No:5 Kat:2 Ofis:2, 34696 Üsküdar / İstanbul",
    "tel": "0216 316 00 64",
    "tel_raw": "+902163160064",
    "wa": "+90 532 470 97 67",
    "wa_raw": "905324709767",
    "mail": "hayrusifa@gmail.com",
    "saatler": [("Pazartesi", "09:00 – 18:30"), ("Salı", "09:00 – 18:30"),
                ("Çarşamba", "09:00 – 18:30"), ("Perşembe", "09:00 – 18:30"),
                ("Cuma", "Kapalı"), ("Cumartesi", "Kapalı"), ("Pazar", "09:00 – 18:30")],
    "saat": "Pazartesi–Perşembe ve Pazar: 09:00 – 18:30 · Cuma, Cumartesi: Kapalı",
    "maps": "https://maps.app.goo.gl/eBBBSeUwsq3PuK1CA",
    "maps_embed": ("https://www.openstreetmap.org/export/embed.html?"
                   "bbox=29.0655%2C41.0101%2C29.0855%2C41.0221&layer=mapnik&"
                   "marker=41.016104%2C29.0754943"),
}

# --------------------------------------------------------------------------- #
#  Yöntem tanımları (menü sırası + açıklamalar)                              #
# --------------------------------------------------------------------------- #
METHODS = OrderedDict([
    ("hacamat", dict(
        label="Hacamat (Kupa Terapisi)", menu="Hacamat",
        short="Vakumlama ve kontrollü kan alma ile dolaşımı ve arınmayı destekleyen geleneksel uygulama.",
        intro="Hacamat; cilt üzerinde oluşturulan vakum ve ince çiziklerle bölgesel kan akışını "
              "artırmayı, vücudun kendini onarma yanıtını uyarmayı amaçlayan geleneksel bir "
              "yöntemdir. Hayru Şifa'da hekim gözetiminde, tek kullanımlık steril malzemelerle uygulanır.")),
    ("suluk-tedavisi", dict(
        label="Sülük Tedavisi (Hirudoterapi)", menu="Sülük Tedavisi",
        short="Tıbbi sülük salgısıyla kan dolaşımı, ödem ve ağrı yönetiminde tamamlayıcı destek.",
        intro="Hirudoterapi, tıbbi sülüklerin salgısındaki biyoaktif bileşiklerden yararlanarak "
              "mikro dolaşımı desteklemeyi ve bölgesel iltihabı azaltmayı hedefler. Yalnızca "
              "sertifikalı tıbbi sülük kullanılır ve her sülük tek seferliktir.")),
    ("ozon-terapisi", dict(
        label="Ozon Terapisi", menu="Ozon Terapisi",
        short="Ozon–oksijen karışımıyla doku oksijenlenmesi ve bağışıklık desteği.",
        intro="Ozon terapisi, kontrollü dozda ozon–oksijen karışımının çeşitli yöntemlerle "
              "uygulanmasıyla hücresel oksijen kullanımını ve antioksidan savunmayı desteklemeyi "
              "amaçlayan tamamlayıcı bir uygulamadır.")),
    ("mezoterapi", dict(
        label="Mezoterapi", menu="Mezoterapi",
        short="Cilde ve saçlı deriye mikroenjeksiyonlarla bölgesel bakım ve canlandırma.",
        intro="Mezoterapi; vitamin, mineral ve hyalüronik asit gibi bileşenlerin cildin orta "
              "katmanına küçük enjeksiyonlarla verilmesidir. Cilt canlandırma, saç dökülmesi ve "
              "bölgesel incelme desteğinde kullanılır.")),
    ("akupunktur", dict(
        label="Akupunktur", menu="Akupunktur",
        short="Belirli noktalara ince iğnelerle ağrı, stres ve uyku düzeninde tamamlayıcı yaklaşım.",
        intro="Akupunktur, geleneksel Çin tıbbının meridyen anlayışına dayanarak belirli "
              "noktalara ince, steril iğnelerin yerleştirilmesidir. En sık ağrı yönetimi, stres "
              "ve uyku sorunlarında tamamlayıcı olarak tercih edilir.")),
    ("prp-tedavisi", dict(
        label="PRP Tedavisi", menu="PRP",
        short="Kişinin kendi trombositten zengin plazmasıyla doku yenilenmesi desteği.",
        intro="PRP; kişinin kendi kanından ayrıştırılan trombositten zengin plazmanın hedef "
              "bölgeye uygulanmasıdır. Cilt yenileme, saç ve eklem sağlığı desteğinde kullanılır.")),
    ("fonksiyonel-tip", dict(
        label="Fonksiyonel Tıp", menu="Fonksiyonel Tıp",
        short="Şikâyetin kök nedenine odaklanan, kişiye özel değerlendirme yaklaşımı.",
        intro="Fonksiyonel tıp; beslenme, yaşam tarzı ve laboratuvar verilerini bir arada "
              "değerlendirerek kronik şikâyetlerin altında yatan nedenleri anlamaya çalışan "
              "bütüncül bir yaklaşımdır.")),
    ("noral-terapi", dict(
        label="Nöral Terapi", menu="Nöral Terapi",
        short="Lokal anesteziklerle sinir sistemi regülasyonuna dayalı ağrı yaklaşımı.",
        intro="Nöral terapi, düşük doz lokal anesteziklerin belirli noktalara uygulanmasıyla "
              "vejetatif sinir sistemindeki dengesizlikleri hedefleyen tamamlayıcı bir yöntemdir.")),
    ("glutatyon", dict(
        label="Glutatyon Tedavisi", menu="Glutatyon",
        short="Antioksidan ve detoks desteği amaçlı glutatyon uygulaması.",
        intro="Glutatyon, vücudun temel antioksidanlarından biridir. Takviye uygulamaları "
              "oksidatif stresi azaltma, detoksifikasyon ve cilt aydınlatma desteği amacıyla tercih edilir.")),
    ("proloterapi", dict(
        label="Proloterapi", menu="Proloterapi",
        short="Bağ dokusu ve eklem ağrılarında rejeneratif enjeksiyon uygulaması.",
        intro="Proloterapi; zayıflamış bağ, tendon ve eklem bölgelerine irritan solüsyonların "
              "enjeksiyonuyla yerel onarım yanıtını uyarmayı amaçlayan bir yöntemdir.")),
    ("mizac-analizi", dict(
        label="Mizaç Analizi", menu="Mizaç Analizi",
        short="Kişinin mizacına göre beslenme, yaşam ve tedavi planlaması.",
        intro="Mizaç analizi; geleneksel tıp anlayışında kişinin baskın mizacını belirleyerek "
              "beslenme ve yaşam önerilerini kişiselleştirmeyi amaçlar.")),
    ("manuel-terapi", dict(
        label="Manuel Terapi", menu="Manuel Terapi",
        short="Omurga ve eklem kaynaklı ağrılarda elle uygulama teknikleri.",
        intro="Manuel terapi; eklem ve yumuşak dokulara yönelik elle uygulanan mobilizasyon ve "
              "gevşetme teknikleriyle hareket açıklığını ve ağrıyı iyileştirmeyi hedefler.")),
    ("aromaterapi", dict(
        label="Aromaterapi", menu="Aromaterapi",
        short="Esansiyel yağlarla ruhsal ve bedensel denge desteği.",
        intro="Aromaterapi, bitkilerden elde edilen esansiyel yağların koklama veya cilde "
              "uygulanması yoluyla rahatlama ve iyilik hâli desteği sağlamayı amaçlar.")),
    ("hicri-hacamat-gunleri", dict(
        label="Hicri Hacamat Günleri", menu="Hicri Hacamat Günleri",
        short="Hacamat için geleneksel olarak önerilen günler ve takvim.",
        intro="Geleneksel kaynaklarda hacamat için ayın belirli günleri önerilir. Bu bölümde "
              "güncel takvim ve sık sorulanlar yer alır.")),
])
SUPPORT = OrderedDict([
    ("kolon-hidroterapi", dict(label="Kolon Hidroterapi", menu="Kolon Hidroterapi",
        short="Kalın bağırsağın su ile nazikçe temizlenmesi uygulaması.", intro="")),
    ("myers-kokteyl", dict(label="Myers Kokteyl", menu="Myers Kokteyl",
        short="Damar yoluyla vitamin–mineral desteği.", intro="")),
    ("alfa-lipoik-asit", dict(label="Alfa Lipoik Asit", menu="Alfa Lipoik Asit",
        short="Antioksidan alfa lipoik asit uygulaması.", intro="")),
    ("fitoterapi", dict(label="Fitoterapi", menu="Fitoterapi",
        short="Bitkisel destek ürünleriyle tamamlayıcı yaklaşım.", intro="")),
    ("refleksoloji", dict(label="Refleksoloji", menu="Refleksoloji",
        short="Ayak ve el refleks noktalarına baskı uygulaması.", intro="")),
    ("medikal-masaj", dict(label="Medikal Masaj", menu="Medikal Masaj",
        short="Kas–iskelet şikâyetlerine yönelik terapötik masaj.", intro="")),
    ("genel", dict(label="Genel / Doğal Tedavi", menu="Genel",
        short="Doğal tedavi üzerine genel yazılar.", intro="")),
])
ALL_CATS = OrderedDict(list(METHODS.items()) + list(SUPPORT.items()))

SUBTOPICS = OrderedDict([
    ("nedir-genel", "Nedir? Genel Bilgi"),
    ("faydalari", "Faydaları"),
    ("hangi-hastaliklar", "Hangi Durumlarda"),
    ("uygulama-surec", "Nasıl Uygulanır"),
    ("oncesi-hazirlik", "Öncesi / Hazırlık"),
    ("sonrasi-bakim", "Sonrası / Bakım"),
    ("kimler-icin-uygun", "Kimler İçin Uygun"),
    ("yan-etkiler-riskler", "Yan Etkiler & Güvenlik"),
    ("bilimsel-tarihce", "Bilimsel Temeller & Tarihçe"),
    ("sss", "Sık Sorulan Sorular"),
    ("fiyat", "Fiyat Bilgisi"),
    ("yorumlar", "Hasta Yorumları"),
    ("genel-yazi", "Diğer Yazılar"),
])

MENU_MAIN = ["hacamat", "suluk-tedavisi", "ozon-terapisi", "mezoterapi", "akupunktur",
             "prp-tedavisi", "fonksiyonel-tip", "noral-terapi", "glutatyon", "proloterapi",
             "mizac-analizi", "manuel-terapi", "aromaterapi"]

# --------------------------------------------------------------------------- #
#  Yardımcılar                                                               #
# --------------------------------------------------------------------------- #
def e(s):
    return html.escape(s or "", quote=True)

def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()

def clean_title(raw):
    t = strip_tags(raw)
    return (t.replace("&#8217;", "’").replace("&#8211;", "–").replace("&#8220;", "“")
             .replace("&#8221;", "”").replace("&amp;", "&").replace("&#8230;", "…")
             .replace("&nbsp;", " ").strip())

TR = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
def slugify(s):
    s = strip_tags(s).translate(TR).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "yazi"

MONTHS = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
          "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
def fmt_date(iso):
    try:
        d = datetime.date.fromisoformat(iso[:10])
        return f"{d.day} {MONTHS[d.month]} {d.year}"
    except Exception:
        return ""

# image url -> local /assets/img/..
BASENAME2FILE = {}
for u, fn in MANIFEST.items():
    if not fn:
        continue
    b = unquote(u.split("/wp-content/uploads/")[-1].split("/")[-1])
    BASENAME2FILE.setdefault(b, fn)
    b2 = re.sub(r"-\d+x\d+(\.\w+)$", r"\1", b)
    BASENAME2FILE.setdefault(b2, fn)

USED_IMAGES = set()
def local_img(url):
    if not url:
        return None
    b = unquote(url.split("/wp-content/uploads/")[-1].split("/")[-1].split("?")[0])
    for key in (b, re.sub(r"-\d+x\d+(\.\w+)$", r"\1", b)):
        if key in BASENAME2FILE:
            fn = BASENAME2FILE[key]
            USED_IMAGES.add(fn)
            return f"/assets/img/{fn}"
    return url  # uzak URL'e düş

def clean_body(html_raw, page_title):
    soup = BeautifulSoup(html_raw or "", "lxml")
    for sel in ["script", "style", "iframe", "form", "ins", "noscript",
                ".sharedaddy", ".jp-relatedposts", ".addtoany_share_save_container",
                ".wp-block-buttons", ".rll-youtube-player", ".code-block", ".adsbygoogle"]:
        for x in soup.select(sel):
            x.decompose()
    # ilk h1/h2 başlık tekrarıysa at
    first = soup.find(["h1", "h2"])
    if first and slugify(first.get_text()) == slugify(page_title):
        first.decompose()
    for h1 in soup.find_all("h1"):
        h1.name = "h2"
    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        img["src"] = local_img(src)
        img["loading"] = "lazy"
        img.attrs.pop("srcset", None); img.attrs.pop("data-srcset", None)
        img.attrs.pop("sizes", None); img.attrs.pop("data-src", None)
        if not img.get("alt"):
            img["alt"] = page_title
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if h.startswith(BASE_URL):
            a["href"] = h  # dahili linkler build sonrası düzeltilebilir
    body = (soup.body.decode_contents() if soup.body else str(soup)).strip()
    body = re.sub(r"(\s*<p>(&nbsp;|\s)*</p>\s*)+", "\n", body)
    # ►/▶/• ile yazılmış sözde maddeleri gerçek <ul><li> listesine çevir
    body = re.sub(r"<br\s*/?>", "\n", body)
    BULLET = "►▶•‣◦·"

    def _fix_p(m):
        inner = m.group(1).strip()
        if not inner or inner.lstrip()[:1] not in BULLET:
            return m.group(0)
        parts = [p.strip(" \n ") for p in re.split(rf"\s*[{BULLET}]\s*", inner)]
        parts = [p for p in parts if p]
        if not parts:
            return ""
        if len(parts) == 1:
            return f"<p>{parts[0]}</p>"
        return "<ul>" + "".join(f"<li>{p}</li>" for p in parts) + "</ul>"

    body = re.sub(r"<p>(.*?)</p>", _fix_p, body, flags=re.S)
    # ardışık tek maddelik <ul>'leri birleştir
    body = re.sub(r"</ul>\s*<ul>", "", body)
    return body

# --------------------------------------------------------------------------- #
#  Veri modeli                                                               #
# --------------------------------------------------------------------------- #
POST_BY_SLUG = {p["slug"]: p for p in POSTS}
items = []
for c in CLS:
    p = POST_BY_SLUG.get(c["slug"])
    if not p:
        continue
    rec = IDX.get(c["slug"], {})
    title = clean_title(p["title"]["rendered"])
    cat = c["ana_kategori"] if c["ana_kategori"] in ALL_CATS else "genel"
    sub = c["alt_konu"] if c["alt_konu"] in SUBTOPICS else "genel-yazi"
    body = clean_body(p.get("content", {}).get("rendered", ""), title)
    # öne çıkan görsel: Yoast og_image → içerikteki ilk <img>
    feat_raw = ""
    og = (p.get("yoast_head_json") or {}).get("og_image") or []
    if og and isinstance(og[0], dict) and og[0].get("url"):
        feat_raw = og[0]["url"]
    if not feat_raw:
        m_img = re.search(r'<img[^>]+src="([^"]+)"', body)
        if m_img:
            feat_raw = m_img.group(1)
    feat = local_img(feat_raw) if feat_raw else None
    if feat and not feat.startswith("/assets"):
        feat = None  # yerelde yoksa kart placeholder kullansın
    desc = ((p.get("yoast_head_json") or {}).get("og_description")
            or rec.get("meta_aciklama") or "").strip() or strip_tags(body)[:180]
    wc = rec.get("kelime_sayisi") or len(re.findall(r"\w+", strip_tags(body)))
    items.append(dict(
        slug=c["slug"], title=title, cat=cat, sub=sub, body=body,
        date=(p.get("date") or "")[:10], date_h=fmt_date(p.get("date") or ""),
        feat=feat, desc=re.sub(r"\s+", " ", desc)[:200],
        read=max(1, round(int(wc) / 200)),
        conds=[x for x in (c.get("hastaliklar") or "").split("; ") if x],
        locs=[x for x in (c.get("lokasyon") or "").split("; ") if x],
        url=f"/blog/{cat}/{c['slug']}.html",
    ))

BY_CAT = defaultdict(list)
for it in items:
    BY_CAT[it["cat"]].append(it)
for k in BY_CAT:
    BY_CAT[k].sort(key=lambda x: x["date"], reverse=True)
LATEST = sorted(items, key=lambda x: x["date"], reverse=True)

# --------------------------------------------------------------------------- #
#  Şablon parçaları                                                          #
# --------------------------------------------------------------------------- #
def head(title, desc, path, og_img=None):
    canon = BASE_URL + path
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="tr_TR">
{f'<meta property="og:image" content="{e(og_img)}">' if og_img else ''}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
"""

def rel(path, depth):
    return ("../" * depth) + path.lstrip("/") if depth else path.lstrip("/") or "index.html"

def header(active=""):
    dd = "\n".join(
        f'<a href="/blog/{s}/" role="menuitem">{e(ALL_CATS[s]["menu"])}</a>'
        for s in MENU_MAIN)
    dd += '\n<a href="/blog/" role="menuitem" class="dd-all">Tüm Yöntemler & Blog →</a>'
    return f"""<a class="skip" href="#main">İçeriğe geç</a>
<header class="site-head">
  <div class="wrap head-in">
    <a class="brand" href="/">Hayru&nbsp;Şifa<span>{e(SITE_TAG)}</span></a>
    <button class="nav-tgl" aria-expanded="false" aria-controls="nav">Menü</button>
    <nav id="nav" class="nav" aria-label="Ana menü">
      <a href="/"{' class="on"' if active=='home' else ''}>Anasayfa</a>
      <div class="has-dd">
        <a href="/blog/"{' class="on"' if active=='tedavi' else ''} aria-haspopup="true">Tedavi Yöntemleri</a>
        <div class="dd" role="menu">{dd}</div>
      </div>
      <a href="/blog/"{' class="on"' if active=='blog' else ''}>Blog</a>
      <a href="/hakkimizda.html"{' class="on"' if active=='hakkimizda' else ''}>Hakkımızda</a>
      <a href="/iletisim.html"{' class="on"' if active=='iletisim' else ''}>İletişim</a>
      <a class="btn btn-sm nav-cta" href="/iletisim.html#randevu">Randevu</a>
    </nav>
  </div>
</header>
"""

def footer():
    cols = "".join(
        f'<li><a href="/blog/{s}/">{e(ALL_CATS[s]["menu"])}</a></li>' for s in MENU_MAIN[:10])
    return f"""<footer class="site-foot">
  <div class="wrap foot-grid">
    <div>
      <div class="brand foot-brand">Hayru Şifa</div>
      <p class="muted">{e(SITE_TAG)}. Uygulamalarımız hekim gözetiminde, steril ve tek kullanımlık malzemelerle yapılır.</p>
      <p class="muted sm">Bu sitedeki içerikler bilgilendirme amaçlıdır; tıbbi tanı ve tedavinin yerine geçmez.</p>
    </div>
    <div>
      <h4>Tedavi Yöntemleri</h4>
      <ul class="foot-links">{cols}</ul>
    </div>
    <div>
      <h4>Kurumsal</h4>
      <ul class="foot-links">
        <li><a href="/hakkimizda.html">Hakkımızda</a></li>
        <li><a href="/ekibimiz.html">Ekibimiz</a></li>
        <li><a href="/hasta-yorumlari.html">Hasta Yorumları</a></li>
        <li><a href="/hicri-hacamat-gunleri.html">Hicri Hacamat Günleri</a></li>
        <li><a href="/blog/">Blog</a></li>
      </ul>
    </div>
    <div>
      <h4>İletişim</h4>
      <ul class="foot-links plain">
        <li>{"<br>".join(e(x) for x in CONTACT['adres_satirlar'])}</li>
        <li><a href="tel:{e(CONTACT['tel_raw'])}">{e(CONTACT['tel'])}</a> ·
            <a href="https://wa.me/{e(CONTACT['wa_raw'])}">WhatsApp</a></li>
        <li><a href="mailto:{e(CONTACT['mail'])}">{e(CONTACT['mail'])}</a></li>
        <li>Pazartesi – Perşembe, Pazar: 09:00 – 18:30<br>Cuma, Cumartesi: Kapalı</li>
        <li><a href="{e(CONTACT['maps'])}">Haritada aç →</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap foot-bot"><span>© {datetime.date.today().year} Hayru Şifa</span><span>İstanbul · Üsküdar / Ümraniye</span></div>
</footer>
<a class="wa-fab" href="https://wa.me/{CONTACT['wa_raw']}" target="_blank" rel="noopener"
   aria-label="WhatsApp ile yazın">
  <svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3C9.4 3 4 8.4 4 15c0 2.1.6 4.2 1.6 6L4 29l8.2-1.6c1.8.9 3.7 1.4 5.8 1.4 6.6 0 12-5.4 12-12S22.6 3 16 3zm0 21.8c-1.8 0-3.6-.5-5.1-1.4l-.4-.2-4.9 1 1-4.7-.2-.4c-1-1.6-1.5-3.4-1.5-5.3 0-5.5 4.5-10 10-10s10 4.5 10 10-4.5 10-10 10zm5.5-7.5c-.3-.2-1.8-.9-2.1-1s-.5-.2-.7.2-.8 1-.9 1.2-.3.2-.6.1c-1.8-.9-3-1.6-4.2-3.6-.3-.5.3-.5.9-1.6.1-.2 0-.4 0-.6s-.7-1.6-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.4-1.2 1.2-1.2 2.9s1.2 3.4 1.4 3.6c.2.2 2.5 3.9 6.1 5.4 2.3.9 3.1.9 4.3.8.7-.1 1.8-.8 2.1-1.5.3-.7.3-1.4.2-1.5-.1-.2-.3-.3-.6-.4z"/></svg>
</a>
<script src="/assets/site.js" defer></script>
</body></html>"""

def breadcrumb(parts):
    lis = []
    for i, (label, href) in enumerate(parts):
        if href and i < len(parts) - 1:
            lis.append(f'<a href="{e(href)}">{e(label)}</a>')
        else:
            lis.append(f'<span aria-current="page">{e(label)}</span>')
    return f'<nav class="crumb wrap" aria-label="Site haritası">{" › ".join(lis)}</nav>'

def card(it):
    img = (f'<img src="{e(it["feat"])}" alt="{e(it["title"])}" loading="lazy">'
           if it["feat"] else f'<span class="ph">{e(ALL_CATS[it["cat"]]["menu"])}</span>')
    return f"""<article class="card" data-cat="{it['cat']}" data-title="{e(it['title'].lower())}">
  <a class="card-media" href="{it['url']}">{img}</a>
  <div class="card-body">
    <a class="tag" href="/blog/{it['cat']}/">{e(ALL_CATS[it['cat']]['menu'])}</a>
    <h3><a href="{it['url']}">{e(it['title'])}</a></h3>
    <p>{e(it['desc'][:130])}…</p>
    <div class="card-meta">{e(it['date_h'])} · {it['read']} dk okuma</div>
  </div>
</article>"""

def write(path, content):
    full = os.path.join(SITE, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)

# --------------------------------------------------------------------------- #
#  Sayfalar                                                                  #
# --------------------------------------------------------------------------- #
def build_home():
    hero_img = None
    if os.path.exists(f"{ROOT}/media/images/{HERO_IMAGE.split('/')[-1]}"):
        hero_img = HERO_IMAGE
        USED_IMAGES.add(HERO_IMAGE.split("/")[-1])
    if not hero_img:
        for it in LATEST:
            if it["feat"] and it["feat"].startswith("/assets"):
                hero_img = it["feat"]; break
    tiles = "".join(f"""<a class="mtile" href="/blog/{s}/">
      <span class="mtile-k">{e(ALL_CATS[s]['menu'])}</span>
      <span class="mtile-d">{e(ALL_CATS[s]['short'])}</span>
      <span class="mtile-n">{len(BY_CAT.get(s, []))} yazı →</span></a>""" for s in MENU_MAIN[:8])
    latest_cards = "".join(card(it) for it in LATEST[:6])
    h = head(f"{SITE_NAME} — {SITE_TAG} | İstanbul",
             "İstanbul Üsküdar ve Ümraniye'de hacamat, sülük tedavisi, ozon terapisi, akupunktur ve "
             "daha fazlası. Hekim gözetiminde doğal ve tamamlayıcı tedavi yöntemleri.", "/")
    h += header("home")
    lotus = ('<svg class="hero-lotus" viewBox="0 0 100 100" fill="none" stroke="#e8f97f" stroke-width="1">'
             '<circle cx="50" cy="50" r="30"/><path d="M50 20c10 12 10 28 0 40-10-12-10-28 0-40z'
             'M50 80c-10-12-10-28 0-40 10 12 10 28 0 40zM20 50c12-10 28-10 40 0-12 10-28 10-40 0z'
             'M80 50c-12 10-28 10-40 0 12-10 28-10 40 0z"/></svg>')
    hero_pic = (f'<div class="hero-photo"><img src="{e(hero_img)}" alt="Hayru Şifa doğal tedavi uygulaması"></div>'
                if hero_img else '<div class="hero-photo"></div>')
    h += f"""<main id="main">
<section class="hero">
  <div class="hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">Geleneksel &amp; Tamamlayıcı Tıp · İstanbul</p>
      <h1>Bedeninizin dengesine doğal yollarla destek</h1>
      <p class="lead">Üsküdar ve Ümraniye'deki kliniğimizde hacamat, sülük tedavisi, ozon terapisi,
         akupunktur ve mezoterapi gibi uygulamaları hekim gözetiminde, steril koşullarda sunuyoruz.</p>
      <div class="hero-cta">
        <a class="btn" href="/iletisim.html#randevu">Randevu Oluştur</a>
        <a class="btn btn-ghost" href="/blog/">Tedavi Yöntemleri</a>
      </div>
      {lotus}
    </div>
    {hero_pic}
  </div>
</section>

<section class="wrap band">
  <div class="band-head"><p class="eyebrow">Uygulamalarımız</p><h2>Öne çıkan tedavi yöntemleri</h2></div>
  <div class="mtiles">{tiles}</div>
  <p class="center"><a class="btn btn-ghost" href="/blog/">Tüm yöntemleri ve blog yazılarını gör</a></p>
</section>

<section class="strip">
  <div class="wrap strip-grid">
    <div><span class="strip-n">20+</span><span class="strip-l">tamamlayıcı yöntem</span></div>
    <div><span class="strip-n">580+</span><span class="strip-l">bilgi yazısı</span></div>
    <div><span class="strip-n">Hekim</span><span class="strip-l">gözetiminde uygulama</span></div>
    <div><span class="strip-n">Tek kullanımlık</span><span class="strip-l">steril malzeme</span></div>
  </div>
</section>

<section class="wrap band">
  <div class="band-head"><p class="eyebrow">Blog</p><h2>Bilgi merkezinden son yazılar</h2></div>
  <div class="cards">{latest_cards}</div>
  <p class="center"><a class="btn btn-ghost" href="/blog/">Blog'un tamamına git</a></p>
</section>

<section class="cta">
  <div class="wrap cta-in">
    <h2>Size uygun yöntemi birlikte belirleyelim</h2>
    <p>Şikâyetinizi değerlendirip uygun uygulamayı öneren ön görüşme için bize ulaşın.</p>
    <a class="btn btn-light" href="/iletisim.html#randevu">İletişime Geç</a>
  </div>
</section>
</main>"""
    h += footer()
    write("index.html", h)

def build_blog_index():
    def cat_tile(s):
        n = len(BY_CAT.get(s, []))
        return f"""<a class="ctile" href="/blog/{s}/">
      <h3>{e(ALL_CATS[s]['label'])}</h3>
      <p>{e(ALL_CATS[s]['short'])}</p>
      <span class="ctile-n">{n} yazı</span></a>"""
    main_tiles = "".join(cat_tile(s) for s in MENU_MAIN)
    sup_tiles = "".join(
        f'<a class="pill" href="/blog/{s}/">{e(ALL_CATS[s]["menu"])} <b>{len(BY_CAT.get(s, []))}</b></a>'
        for s in SUPPORT if BY_CAT.get(s))
    latest_cards = "".join(card(it) for it in LATEST[:9])
    h = head("Blog — Doğal ve Tamamlayıcı Tedaviler | Hayru Şifa",
             "Hacamat, sülük tedavisi, ozon terapisi, akupunktur, mezoterapi ve diğer tamamlayıcı "
             "yöntemler üzerine 580+ bilgi yazısı; tedavi yöntemine göre kategorilenmiş.", "/blog/")
    h += header("blog")
    h += breadcrumb([("Anasayfa", "/"), ("Blog", None)])
    h += f"""<main id="main">
<section class="wrap page-head">
  <p class="eyebrow">Bilgi Merkezi</p>
  <h1>Blog</h1>
  <p class="lead">Tüm yazılar artık tek çatı altında ve <strong>tedavi yöntemine göre</strong> kategorilenmiş.
     Bir kategori seçin ya da <a href="/blog/tum-yazilar.html">tüm yazılarda arayın</a>.</p>
</section>

<section class="wrap band">
  <div class="band-head"><h2>Tedavi yöntemine göre</h2></div>
  <div class="ctiles">{main_tiles}</div>
  <div class="pills">{sup_tiles}</div>
</section>

<section class="wrap band">
  <div class="band-head"><h2>Son eklenen yazılar</h2>
    <a class="band-link" href="/blog/tum-yazilar.html">Tüm yazılar →</a></div>
  <div class="cards">{latest_cards}</div>
</section>
</main>"""
    h += footer()
    write("blog/index.html", h)

def build_all_posts():
    rows = "".join(
        f'<li data-cat="{it["cat"]}" data-t="{e(it["title"].lower())}">'
        f'<a href="{it["url"]}">{e(it["title"])}</a>'
        f'<span class="row-cat">{e(ALL_CATS[it["cat"]]["menu"])}</span>'
        f'<span class="row-date">{e(it["date_h"])}</span></li>'
        for it in sorted(items, key=lambda x: x["title"].lower()))
    opts = "".join(f'<option value="{s}">{e(ALL_CATS[s]["menu"])}</option>'
                   for s in ALL_CATS if BY_CAT.get(s))
    h = head("Tüm Yazılar | Hayru Şifa Blog",
             "Hayru Şifa blogundaki tüm yazıların aranabilir listesi.", "/blog/tum-yazilar.html")
    h += header("blog")
    h += breadcrumb([("Anasayfa", "/"), ("Blog", "/blog/"), ("Tüm Yazılar", None)])
    h += f"""<main id="main">
<section class="wrap page-head">
  <p class="eyebrow">Blog</p><h1>Tüm Yazılar</h1>
  <p class="lead">{len(items)} yazı. Başlıkta arayın veya kategoriye göre süzün.</p>
  <div class="filterbar">
    <input type="search" id="q" placeholder="Yazı ara…" aria-label="Yazı ara">
    <select id="catf" aria-label="Kategori">
      <option value="">Tüm kategoriler</option>{opts}
    </select>
  </div>
</section>
<section class="wrap">
  <ol class="postlist" id="plist">{rows}</ol>
  <p class="muted center" id="nores" hidden>Eşleşen yazı yok.</p>
</section>
</main>"""
    h += footer()
    write("blog/tum-yazilar.html", h)

def build_category(slug):
    meta = ALL_CATS[slug]
    posts = BY_CAT.get(slug, [])
    groups = OrderedDict((k, []) for k in SUBTOPICS)
    for it in posts:
        groups[it["sub"]].append(it)
    sections = ""
    for sub, lbl in SUBTOPICS.items():
        g = groups[sub]
        if not g:
            continue
        lis = "".join(
            f'<li><a href="{it["url"]}">{e(it["title"])}</a><span>{e(it["date_h"])}</span></li>'
            for it in g)
        sections += f'<div class="subsec"><h2>{e(lbl)} <span class="cnt">{len(g)}</span></h2><ul class="linklist">{lis}</ul></div>'
    feat_cards = "".join(card(it) for it in posts[:3])
    other = "".join(
        f'<a href="/blog/{s}/"{" class=on" if s==slug else ""}>{e(ALL_CATS[s]["menu"])}</a>'
        for s in ALL_CATS if BY_CAT.get(s))
    h = head(f"{meta['label']} — Bilgi Yazıları | Hayru Şifa",
             meta["short"], f"/blog/{slug}/",
             posts[0]["feat"] if posts and posts[0]["feat"] else None)
    h += header("tedavi")
    h += breadcrumb([("Anasayfa", "/"), ("Blog", "/blog/"), (meta["label"], None)])
    h += f"""<main id="main">
<section class="wrap page-head">
  <p class="eyebrow">Tedavi Yöntemi</p>
  <h1>{e(meta['label'])}</h1>
  <p class="lead">{e(meta.get('intro') or meta['short'])}</p>
  <div class="hero-cta"><a class="btn" href="/iletisim.html#randevu">Bu yöntem için randevu</a>
    <a class="btn btn-ghost" href="/blog/tum-yazilar.html">Tüm yazılar</a></div>
</section>
{f'<section class="wrap band"><div class="band-head"><h2>Öne çıkanlar</h2></div><div class="cards">{feat_cards}</div></section>' if feat_cards else ''}
<section class="wrap catbody">
  <div class="catmain">
    <div class="band-head"><h2>Bu kategorideki tüm yazılar <span class="cnt">{len(posts)}</span></h2></div>
    {sections or '<p class="muted">Bu kategoride henüz yazı yok.</p>'}
  </div>
  <aside class="catside">
    <div class="side-card"><h3>Diğer yöntemler</h3><nav class="side-nav">{other}</nav></div>
    <div class="side-card cta-card">
      <h3>Bilgi &amp; randevu</h3>
      <p>Şikâyetinize uygun yöntemi birlikte belirleyelim.</p>
      <a class="btn btn-sm" href="/iletisim.html#randevu">İletişime geç</a>
    </div>
  </aside>
</section>
</main>"""
    h += footer()
    write(f"blog/{slug}/index.html", h)

def build_post(it):
    meta = ALL_CATS[it["cat"]]
    same = [x for x in BY_CAT[it["cat"]] if x["slug"] != it["slug"]][:5]
    rel_lis = "".join(f'<li><a href="{x["url"]}">{e(x["title"])}</a></li>' for x in same)
    idxlist = BY_CAT[it["cat"]]
    pos = next((i for i, x in enumerate(idxlist) if x["slug"] == it["slug"]), 0)
    prevn = idxlist[pos + 1] if pos + 1 < len(idxlist) else None
    nextn = idxlist[pos - 1] if pos > 0 else None
    pn = ""
    if prevn:
        pn += f'<a class="pn prev" href="{prevn["url"]}"><span>← Önceki</span>{e(prevn["title"])}</a>'
    if nextn:
        pn += f'<a class="pn next" href="{nextn["url"]}"><span>Sonraki →</span>{e(nextn["title"])}</a>'
    feat = (f'<figure class="post-feat"><img src="{e(it["feat"])}" alt="{e(it["title"])}"></figure>'
            if it["feat"] else "")
    tags = "".join(f'<a class="chip" href="/blog/tum-yazilar.html">{e(c)}</a>' for c in it["conds"][:6])
    h = head(f"{it['title']} | Hayru Şifa",
             it["desc"], it["url"], it["feat"] if it["feat"] and it["feat"].startswith("/assets") else None)
    h += header("blog")
    h += breadcrumb([("Anasayfa", "/"), ("Blog", "/blog/"),
                     (meta["menu"], f"/blog/{it['cat']}/"), (it["title"], None)])
    h += f"""<main id="main">
<article class="wrap post">
  <div class="postmain">
    <p class="eyebrow"><a href="/blog/{it['cat']}/">{e(meta['label'])}</a></p>
    <h1>{e(it['title'])}</h1>
    <div class="post-meta">{e(it['date_h'])} · {it['read']} dk okuma</div>
    {feat}
    <div class="prose">{it['body']}</div>
    {f'<div class="chips"><span>İlgili konular:</span>{tags}</div>' if tags else ''}
    <div class="post-cta">
      <div>
        <strong>{e(meta['label'])} hakkında görüşmek ister misiniz?</strong>
        <p class="muted sm">Değerlendirme ve randevu için bize yazın.</p>
      </div>
      <a class="btn btn-sm" href="/iletisim.html#randevu">Randevu</a>
    </div>
    <nav class="pn-wrap">{pn}</nav>
  </div>
  <aside class="postside">
    <div class="side-card"><h3>{e(meta['menu'])} — diğer yazılar</h3><ul class="side-list">{rel_lis}</ul>
      <a class="side-more" href="/blog/{it['cat']}/">Tümünü gör →</a></div>
    <div class="side-card cta-card"><h3>Randevu</h3>
      <p>Hekim gözetiminde, steril uygulama.</p>
      <a class="btn btn-sm" href="/iletisim.html#randevu">İletişime geç</a></div>
  </aside>
</article>
</main>"""
    h += footer()
    write(it["url"], h)

def _page_md(slug):
    for folder in ("kurumsal", "hizmet-sayfalari", "sistem", "lokasyon"):
        p = f"{ROOT}/content/pages/{folder}/{slug}.md"
        if os.path.exists(p):
            t = open(p, encoding="utf-8").read().split("---", 2)
            return t[2].strip() if len(t) > 2 else ""
    return ""

def _md_min(md):
    import markdown as _m
    return _m.markdown(md, extensions=["extra", "sane_lists"])

def simple_page(slug, title, active, intro, body_html, note=None):
    h = head(f"{title} | Hayru Şifa", intro[:180], f"/{slug}.html")
    h += header(active)
    h += breadcrumb([("Anasayfa", "/"), (title, None)])
    h += f"""<main id="main">
<section class="wrap page-head"><p class="eyebrow">Kurumsal</p><h1>{e(title)}</h1>
<p class="lead">{e(intro)}</p></section>
<section class="wrap narrow prose">
{f'<p class="note">{e(note)}</p>' if note else ''}
{body_html}
</section>
</main>"""
    h += footer()
    write(f"{slug}.html", h)

def build_institutional():
    kli = _page_md("klinigimiz")
    body = _md_min(kli) if kli else ""
    simple_page("hakkimizda", "Hakkımızda", "hakkimizda",
                "Hayru Şifa; geleneksel ve tamamlayıcı tıp uygulamalarını hekim gözetiminde, "
                "hijyenik bir ortamda sunan bir kliniktir.",
                body or "<p>İçerik hazırlanıyor.</p>",
                None if kli else "Bu sayfanın içeriği eski siteden aktarılamadı; klinik tarafından güncellenecek.")

    yorum_note = "Hasta yorumları eski siteden aktarılamadı. Gerçek hasta geri bildirimleri buraya eklenecek."
    simple_page("hasta-yorumlari", "Hasta Yorumları", "",
                "Kliniğimizde uygulama yaptıran danışanlarımızın deneyimleri.",
                '<p class="muted">Yorumlar yakında yayımlanacak.</p>', yorum_note)

    simple_page("ekibimiz", "Ekibimiz", "",
                "Uygulamalarımız hekim ve sertifikalı terapist eşliğinde yürütülür.",
                "<ul><li>Sorumlu Hekim — [ad, unvan eklenecek]</li>"
                "<li>Terapist kadrosu — [eklenecek]</li></ul>",
                "Ekip bilgileri eski sitede bulunmuyordu; klinik tarafından doldurulacak.")

    # iletişim
    h = head("İletişim & Randevu | Hayru Şifa",
             "Hayru Şifa kliniği — Bulgurlu Mah. Ünlü Sokak No:5, Üsküdar / İstanbul. "
             "Telefon 0216 316 00 64, WhatsApp +90 532 470 97 67.", "/iletisim.html")
    h += header("iletisim")
    h += breadcrumb([("Anasayfa", "/"), ("İletişim", None)])
    h += f"""<main id="main">
<section class="wrap page-head" id="randevu"><p class="eyebrow">Bize Ulaşın</p><h1>İletişim &amp; Randevu</h1>
<p class="lead">Şikâyetinizi değerlendirip size uygun yöntemi öneren ön görüşme için telefon veya
WhatsApp'tan bize ulaşabilirsiniz.</p></section>
<section class="wrap contact-grid">
  <div class="side-card">
    <h3>Klinik Bilgileri</h3>
    <div class="contact-info">
      <div class="ci-row">
        <h4>Adres</h4>
        <p>{"<br>".join(e(x) for x in CONTACT['adres_satirlar'])}</p>
      </div>
      <div class="ci-row">
        <h4>Telefon</h4>
        <p><a href="tel:{e(CONTACT['tel_raw'])}">{e(CONTACT['tel'])}</a></p>
      </div>
      <div class="ci-row">
        <h4>WhatsApp</h4>
        <p><a href="https://wa.me/{e(CONTACT['wa_raw'])}">{e(CONTACT['wa'])}</a></p>
      </div>
      <div class="ci-row">
        <h4>E-posta</h4>
        <p><a href="mailto:{e(CONTACT['mail'])}">{e(CONTACT['mail'])}</a></p>
      </div>
      <div class="ci-row">
        <h4>Çalışma Saatleri</h4>
        <ul class="hours">
          {"".join(f'<li class="{"off" if v=="Kapalı" else ""}"><span>{e(g)}</span><span>{e(v)}</span></li>' for g, v in CONTACT['saatler'])}
        </ul>
      </div>
    </div>
    <div class="contact-cta">
      <a class="btn" href="https://wa.me/{e(CONTACT['wa_raw'])}">WhatsApp'tan Yazın</a>
      <a class="btn btn-ghost" href="tel:{e(CONTACT['tel_raw'])}">Telefonla Ara</a>
    </div>
  </div>
  <div class="side-card map-card">
    <iframe title="Hayru Şifa konum haritası" src="{e(CONTACT['maps_embed'])}"
      loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
    <a class="map-link" href="{e(CONTACT['maps'])}">Google Haritalar'da aç →</a>
  </div>
</section>
</main>"""
    h += footer()
    write("iletisim.html", h)

def build_hicri():
    posts = BY_CAT.get("hicri-hacamat-gunleri", [])
    lis = "".join(f'<li><a href="{it["url"]}">{e(it["title"])}</a><span>{e(it["date_h"])}</span></li>'
                  for it in posts)
    h = head("Hicri Hacamat Günleri | Hayru Şifa",
             "Geleneksel kaynaklarda hacamat için önerilen günler ve güncel takvim.",
             "/hicri-hacamat-gunleri.html")
    h += header("")
    h += breadcrumb([("Anasayfa", "/"), ("Hicri Hacamat Günleri", None)])
    h += f"""<main id="main">
<section class="wrap page-head"><p class="eyebrow">Takvim</p><h1>Hicri Hacamat Günleri</h1>
<p class="lead">Geleneksel kaynaklarda hacamat için ayın 17, 19 ve 21. günleri ve özellikle
Pazartesi, Salı ve Perşembe günleri önerilir. Güncel takvim ve arşiv yazıları aşağıdadır.</p>
<p class="note">Takvim tablosu klinik tarafından her yıl güncellenecek.</p></section>
<section class="wrap narrow"><ul class="linklist">{lis or '<li class=muted>Arşiv yazısı yok.</li>'}</ul></section>
</main>"""
    h += footer()
    write("hicri-hacamat-gunleri.html", h)

def build_404():
    h = head("Sayfa bulunamadı | Hayru Şifa", "Aradığınız sayfa taşınmış olabilir.", "/404.html")
    h += header("")
    h += """<main id="main"><section class="wrap page-head" style="text-align:center">
<h1>Sayfa bulunamadı</h1><p class="lead">Aradığınız sayfa taşınmış ya da kaldırılmış olabilir.</p>
<p><a class="btn" href="/">Anasayfa</a> <a class="btn btn-ghost" href="/blog/">Blog</a></p></section></main>"""
    h += footer()
    write("404.html", h)

# --------------------------------------------------------------------------- #
#  Statik varlıklar                                                          #
# --------------------------------------------------------------------------- #
CSS = open(f"{ROOT}/crawl/scripts/site.css", encoding="utf-8").read()
JS = open(f"{ROOT}/crawl/scripts/site.js", encoding="utf-8").read()

def build_assets():
    write("assets/site.css", CSS)
    write("assets/site.js", JS)
    dst = f"{SITE}/assets/img"
    os.makedirs(dst, exist_ok=True)
    src = f"{ROOT}/media/images"
    n = 0
    for fn in USED_IMAGES:
        s = os.path.join(src, fn)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(dst, fn)); n += 1
    print(f"  görsel kopyalandı: {n}")

def build_meta():
    urls = ["/", "/blog/", "/blog/tum-yazilar.html", "/hakkimizda.html", "/iletisim.html",
            "/ekibimiz.html", "/hasta-yorumlari.html", "/hicri-hacamat-gunleri.html"]
    urls += [f"/blog/{s}/" for s in ALL_CATS if BY_CAT.get(s)]
    urls += [it["url"] for it in items]
    body = "".join(f"<url><loc>{BASE_URL}{u}</loc></url>\n" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    # eski slug -> yeni url (301 haritası)
    red = "".join(f"/{it['slug']}/  {it['url']}  301\n" for it in items)
    write("_redirects", red)

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    if os.path.isdir(SITE):
        shutil.rmtree(SITE)
    os.makedirs(SITE)
    build_home()
    build_blog_index()
    build_all_posts()
    cats = [s for s in ALL_CATS if BY_CAT.get(s)]
    for s in cats:
        build_category(s)
    for it in items:
        build_post(it)
    build_institutional()
    build_hicri()
    build_404()
    build_assets()
    build_meta()
    print(f"OK · {len(items)} yazı · {len(cats)} kategori sayfası · site/ hazır")
