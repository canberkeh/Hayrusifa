#!/usr/bin/env python3
"""Classify all 588 posts into a clean new taxonomy and reorganize markdown."""
import json, os, re, csv, shutil
from collections import defaultdict, Counter

BASE = "/Users/crea/Desktop/hayrusifa"
HAM = f"{BASE}/content/blog/_ham"
NEW = f"{BASE}/content/blog"

posts = json.load(open(f"{BASE}/crawl/wp-api/posts.json", encoding="utf-8"))
cats = json.load(open(f"{BASE}/crawl/wp-api/categories.json", encoding="utf-8"))
idx = {r["slug"]: r for r in json.load(open(f"{BASE}/crawl/icerik-index.json", encoding="utf-8"))}
cat_by_id = {c["id"]: c for c in cats}
COND_PARENT = 119
cond_cat = {c["id"]: c["name"] for c in cats if c["parent"] == COND_PARENT}

# ---- method detection -------------------------------------------------------
# (slug, label, [keywords])  order = tie-break priority
METHODS = [
    ("hicri-hacamat-gunleri", "Hicri Hacamat Günleri", ["hicri hacamat", "hacamat günleri", "hacamat gunleri", "hacamat takvimi", "hicri gün"]),
    ("suluk-tedavisi", "Sülük Tedavisi (Hirudoterapi)", ["tıbbi sülük", "tibbi suluk", "sülük", "suluk", "hirudoterapi", "hirudo", "suluk"]),
    ("hacamat", "Hacamat (Kupa Terapisi)", ["hacamat", "kupa terapi", "kupa tedavi", "çördek", "cordek", "kuru kupa", "sülük" == "x" and "" or "kupalama"]),
    ("akupunktur", "Akupunktur", ["akupunktur", "akapunktur", "kulak akupunktur", "meridyen", "iğne tedavi"]),
    ("ozon-terapisi", "Ozon Terapisi", ["ozon"]),
    ("mezoterapi", "Mezoterapi", ["mezoterapi", "mikroenjeksiyon", "meso"]),
    ("prp-tedavisi", "PRP Tedavisi", ["prp"]),
    ("glutatyon", "Glutatyon Tedavisi", ["glutatyon", "glutatiyon"]),
    ("noral-terapi", "Nöral Terapi", ["nöral terapi", "noral terapi", "nöralterapi"]),
    ("proloterapi", "Proloterapi", ["proloterapi", "proloterapi"]),
    ("fonksiyonel-tip", "Fonksiyonel Tıp", ["fonksiyonel tıp", "fonksiyonel tip", "fonksiyonel tıbb", "fonksiyonel tibb"]),
    ("aromaterapi", "Aromaterapi", ["aromaterapi", "esansiyel yağ", "esansiyel yag", "uçucu yağ"]),
    ("mizac-analizi", "Mizaç Analizi", ["mizaç", "mizac"]),
    ("manuel-terapi", "Manuel Terapi", ["manuel terapi", "manuel terapı", "bel fıtığı", "boyun fıtığı", "omurga sağlığı", "fizik tedavi"]),
    ("kolon-hidroterapi", "Kolon Hidroterapi", ["kolon terapi", "kolon hidroterapi", "bağırsak temizli", "kolon temizli", "hidroterapi"]),
    ("myers-kokteyl", "Myers Kokteyl", ["myers kokteyl", "myers kokteyli", "vitamin kokteyl"]),
    ("alfa-lipoik-asit", "Alfa Lipoik Asit", ["alfa lipoik"]),
    ("fitoterapi", "Fitoterapi", ["fitoterapi", "bitkisel tedavi"]),
    ("refleksoloji", "Refleksoloji", ["refleksoloji"]),
    ("medikal-masaj", "Medikal Masaj", ["medikal masaj", "derin doku masaj", "tıbbi masaj"]),
    ("sunnet", "Sünnet Uygulaması", ["sünnet", "sunnet"]),
]
WPCAT_TO_METHOD = {
    "hacamat": "hacamat", "kupa-tedavisi": "hacamat", "hicri-hacamat-gunleri": "hicri-hacamat-gunleri",
    "suluk-tedavisi": "suluk-tedavisi", "hirudoterapi": "suluk-tedavisi",
    "akupunktur": "akupunktur", "ozon-terapisi": "ozon-terapisi", "mezoterapi": "mezoterapi",
    "prp-uygulamasi": "prp-tedavisi", "glutatyon": "glutatyon", "noral-terapi": "noral-terapi",
    "proloterapi": "proloterapi", "fonksiyonel-tip": "fonksiyonel-tip", "aromaterapi": "aromaterapi",
    "mizac-analizi": "mizac-analizi", "mizac": "mizac-analizi", "manuel-terapi": "manuel-terapi",
    "kolon-terapi": "kolon-hidroterapi", "hidroterapi": "kolon-hidroterapi",
    "myers-kokteyl": "myers-kokteyl", "alfa-lipoik-asit": "alfa-lipoik-asit",
    "fitoterapi": "fitoterapi", "refleksoloji": "refleksoloji", "sunnet-uygulama": "sunnet",
}
METHOD_LABEL = {s: l for s, l, _ in METHODS}
METHOD_LABEL["genel"] = "Genel / Doğal Tedavi"

# grouping of methods into top-level sections
SECTION = {
    "hacamat": "Tedavi Yöntemleri", "hicri-hacamat-gunleri": "Tedavi Yöntemleri",
    "suluk-tedavisi": "Tedavi Yöntemleri", "akupunktur": "Tedavi Yöntemleri",
    "ozon-terapisi": "Tedavi Yöntemleri", "mezoterapi": "Tedavi Yöntemleri",
    "prp-tedavisi": "Tedavi Yöntemleri", "glutatyon": "Tedavi Yöntemleri",
    "noral-terapi": "Tedavi Yöntemleri", "proloterapi": "Tedavi Yöntemleri",
    "fonksiyonel-tip": "Tedavi Yöntemleri", "aromaterapi": "Tedavi Yöntemleri",
    "mizac-analizi": "Tedavi Yöntemleri", "manuel-terapi": "Tedavi Yöntemleri",
    "kolon-hidroterapi": "Destekleyici Tedaviler", "myers-kokteyl": "Destekleyici Tedaviler",
    "alfa-lipoik-asit": "Destekleyici Tedaviler", "fitoterapi": "Destekleyici Tedaviler",
    "refleksoloji": "Destekleyici Tedaviler", "medikal-masaj": "Destekleyici Tedaviler",
    "sunnet": "Diğer Uygulamalar", "genel": "Diğer Uygulamalar",
}

def detect_method(title, wpcats_slugs):
    tl = " " + title.lower() + " "
    best = None  # (pos, prio, slug)
    for prio, (slug, label, kws) in enumerate(METHODS):
        for kw in kws:
            if not kw:
                continue
            p = tl.find(kw)
            if p != -1:
                cand = (p, prio, slug)
                if best is None or cand < best:
                    best = cand
    if best:
        return best[2]
    for cs in wpcats_slugs:
        if cs in WPCAT_TO_METHOD:
            return WPCAT_TO_METHOD[cs]
    return "genel"

# ---- subtopic detection ---------------------------------------------------
SUByeni = [
    ("sss", ["sık sorulan", "sikca sorulan", "sıkça sorulan", "sss", "merak edilenler", "sorular ve cevap", "soru cevap"]),
    ("fiyat", ["fiyat", "ücret", "ucret", "maliyet", "ne kadar", "kaç para"]),
    ("yorumlar", ["yorum", "hasta deneyim", "kullanıcı deneyim", "başarı hikaye"]),
    ("yan-etkiler-riskler", ["yan etki", "yan etkiler", "risk", "zararl", "güvenli mi", "guvenli mi", "güvenlik", "komplikasyon"]),
    ("sonrasi-bakim", ["sonrası", "sonrasi", "sonra nelere", "sonra ne", "bakım", "bakim", "iyileşme sürec", "iyilesme surec", "toparlanma"]),
    ("oncesi-hazirlik", ["öncesi", "oncesi", "önce bilmeniz", "once bilmeniz", "yaptırmadan önce", "hazırlık", "hazirlik", "önce dikkat"]),
    ("uygulama-surec", ["nasıl uygulan", "nasil uygulan", "nasıl yapıl", "nasil yapil", "adım adım", "adim adim", "aşamalar", "asamalar", "uygulama sürec", "seans", "teknik", "nasıl gerçekleş", "prosedür", "kaç seans"]),
    ("kimler-icin-uygun", ["kimler için", "kimler icin", "kimlere uygun", "uygun mudur", "uygun değildir", "uygun degildir", "kimler yaptır", "kimlere yapıl"]),
    ("hangi-hastaliklar", ["hangi hastalık", "hangi hastalik", "hangi durumlar", "hangi sağlık", "hangi saglik", "iyi gelir", "işe yarar mı", "ne işe yarar", "kullanım alan", "kullanim alan", "uygulama alan", "hangi rahatsızlık"]),
    ("bilimsel-tarihce", ["bilimsel", "araştırma", "arastirma", "tarihçe", "tarihce", "tarihi", "geçmişten", "gecmisten", "modern tıp", "modern tip", "geleneksel", "çin tıbb", "cin tibb", "antik", "kanıt"]),
    ("faydalari", ["fayda", "yarar", "avantaj", "katkı", "katki", "olumlu etki", "etkiler", "işe yarıyor", "ise yariyor", "gücü", "mucize", "destek"]),
    ("nedir-genel", ["nedir", "ne demek", "tanım", "hakkında bilinmesi", "rehber", "kapsamlı rehber", "temel prensip", "giriş"]),
]

def detect_subtopic(title):
    tl = title.lower()
    for slug, kws in SUByeni:
        if any(k in tl for k in kws):
            return slug
    return "genel-yazi"

# ---- condition tags -----------------------------------------------------
COND_KW = {
    "Ağrı": ["ağrı", "agri", "sırt ağrısı", "bel ağrısı", "eklem ağrısı", "kronik ağrı"],
    "Migren": ["migren", "baş ağrısı", "bas agrisi"],
    "Bel / Boyun Fıtığı": ["bel fıtığı", "boyun fıtığı", "disk hernisi", "fıtık"],
    "Varis": ["varis"],
    "Cilt": ["cilt", "akne", "sivilce", "leke", "kırışıklık", "kirisiklik", "cilt genç", "gözenek"],
    "Selülit": ["selülit", "selulit"],
    "Egzama / Sedef": ["egzama", "egzema", "sedef", "psoriasis"],
    "Saç Dökülmesi": ["saç dökül", "sac dokul", "saç ekim", "kellik"],
    "Diyabet": ["diyabet", "şeker hastalığı", "seker hastaligi", "insülin"],
    "Tiroid": ["tiroid", "troid", "hashimoto", "guatr"],
    "Kalp / Dolaşım": ["kalp", "kan dolaşım", "kan dolasim", "tansiyon", "hipertansiyon", "damar"],
    "Kolesterol": ["kolesterol"],
    "Depresyon / Anksiyete": ["depresyon", "anksiyete", "kaygı", "panik atak"],
    "Stres": ["stres", "stresten"],
    "Uyku Bozuklukları": ["uyku", "uykusuzluk", "insomnia"],
    "Kronik Yorgunluk": ["kronik yorgunluk", "halsizlik", "yorgunluk"],
    "Kısırlık / Üreme": ["kısırlık", "kisirlik", "infertilite", "tüp bebek", "üreme", "gebe kal"],
    "Hormonal Denge": ["hormon", "hormonal", "adet düzensiz", "menopoz", "regl"],
    "Obezite / Zayıflama": ["obezite", "zayıfla", "zayifla", "kilo verme", "kilo kayb", "bölgesel incelme"],
    "Bağışıklık": ["bağışıklık", "bagisiklik", "immün", "immun"],
    "Detoks": ["detoks", "toksin", "arınma", "arinma"],
    "Romatizma / Eklem": ["romatizma", "romatoid", "kireçlenme", "kireclenme", "artrit", "osteoartrit", "eklem iltihab"],
    "Karpal Tünel": ["karpal tünel", "karpal tunel"],
    "Karaciğer": ["karaciğer", "karaciger", "hepatit"],
    "Sindirim": ["sindirim", "mide", "reflü", "reflu", "gastrit", "bağırsak", "kabızlık"],
    "Nörolojik": ["nörolojik", "norolojik", "felç", "ms hastalığı", "parkinson", "alzheimer", "yüz felci"],
    "Spor Yaralanmaları": ["spor yaralan", "sporcu", "kas gücü", "tendon"],
    "İdrar Kaçırma": ["idrar kaçır", "idrar kacir", "mesane"],
    "Göz": ["göz sağlığı", "goz sagligi", "göz hastalık"],
    "Diş / Diş Eti": ["diş eti", "dis eti", "diş sağlığı"],
    "Alt Islatma": ["alt ıslat", "alt islat", "gece işeme"],
}

def detect_conditions(title, wpcats_slugs, wpcat_names):
    tags = set()
    for cid, name in cond_cat.items():
        pass
    for n in wpcat_names:
        # if a wp category is a child of Hastalıklarda Tedavi
        pass
    # from wp category ids
    return tags

LOC_KW = {
    "Üsküdar": ["üsküdar", "uskudar"],
    "Ümraniye": ["ümraniye", "umraniye"],
    "İstanbul": ["istanbul"],
    "Kocaeli": ["kocaeli", "izmit"],
    "Trabzon": ["trabzon"],
}

rows = []
sec_counts = Counter()
method_counts = Counter()
method_sub = defaultdict(Counter)
cond_index = defaultdict(list)

for p in posts:
    slug = p["slug"]
    title = re.sub(r"<[^>]+>", "", p["title"]["rendered"]).strip()
    title = title.replace("&#8217;", "'").replace("&amp;", "&").replace("&#8211;", "-")
    wpc_ids = p.get("categories", [])
    wpc_slugs = [cat_by_id[c]["slug"] for c in wpc_ids if c in cat_by_id]
    wpc_names = [cat_by_id[c]["name"] for c in wpc_ids if c in cat_by_id]

    method = detect_method(title, wpc_slugs)
    sub = detect_subtopic(title)
    section = SECTION.get(method, "Diğer Uygulamalar")

    # conditions
    COND_NORM = {
        "Kalp": "Kalp / Dolaşım", "Migren": "Migren", "Anksiyete": "Depresyon / Anksiyete",
        "Depresyon": "Depresyon / Anksiyete", "Ruhsal Hastalıklar": "Depresyon / Anksiyete",
        "Egzema": "Egzama / Sedef", "Troid": "Tiroid",
        "Karpal Tünel Sendromu": "Karpal Tünel",
        "Karaciğer Sorunları": "Karaciğer", "Hepatit": "Karaciğer",
        "Kısırlık": "Kısırlık / Üreme", "Üroloji": "Üroloji / İdrar",
        "İdrar Kaçırma Sorunu": "Üroloji / İdrar", "İktidarsızlık": "Cinsel Problemler",
        "Obezite": "Obezite / Zayıflama", "Kolesterol": "Kolesterol",
        "Diş ve Diş Eti": "Diş / Diş Eti", "Kireçlenme": "Romatizma / Eklem",
        "Nörolojik Hastalıklar": "Nörolojik", "Adet Bozuklukları": "Hormonal Denge",
        "Fıtık": "Bel / Boyun Fıtığı", "Boyun ve Sırt": "Ağrı", "Kas Spazmı": "Ağrı",
        "Derin Doku": "Ağrı", "Manevi Hastalıklar": "Manevi / Ruhsal",
        "Otoimmün Hastalıklar": "Otoimmün Hastalıklar", "Göz": "Göz",
    }
    conds = set()
    for c in wpc_ids:
        if c in cond_cat:
            nm = cond_cat[c]
            conds.add(COND_NORM.get(nm, nm))
    tl = title.lower()
    for label, kws in COND_KW.items():
        if any(k in tl for k in kws):
            conds.add(COND_NORM.get(label, label))

    # location
    hay = (tl + " " + " ".join(wpc_slugs)).lower()
    locs = [label for label, kws in LOC_KW.items() if any(k in hay for k in kws)]

    r = idx.get(slug, {})
    row = {
        "slug": slug,
        "baslik": title,
        "tarih": (p.get("date") or "")[:10],
        "bolum": section,
        "ana_kategori": method,
        "ana_kategori_adi": METHOD_LABEL.get(method, method),
        "alt_konu": sub,
        "hastaliklar": "; ".join(sorted(conds)),
        "lokasyon": "; ".join(locs),
        "kelime_sayisi": r.get("kelime_sayisi", ""),
        "gorsel_sayisi": r.get("gorsel_sayisi", ""),
        "wp_kategoriler": " | ".join(wpc_names),
        "kaynak_url": p.get("link", ""),
    }
    rows.append(row)
    sec_counts[section] += 1
    method_counts[method] += 1
    method_sub[method][sub] += 1
    for c in conds:
        cond_index[c].append(slug)

# ---- write CSV + JSON ----------------------------------------------------
os.makedirs(f"{BASE}/taksonomi", exist_ok=True)
fields = ["slug", "baslik", "tarih", "bolum", "ana_kategori", "ana_kategori_adi",
          "alt_konu", "hastaliklar", "lokasyon", "kelime_sayisi", "gorsel_sayisi",
          "wp_kategoriler", "kaynak_url"]
with open(f"{BASE}/taksonomi/yazi-siniflandirma.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(sorted(rows, key=lambda x: (x["bolum"], x["ana_kategori"], x["alt_konu"], x["slug"])))
json.dump(rows, open(f"{BASE}/taksonomi/yazi-siniflandirma.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump({k: sorted(v) for k, v in sorted(cond_index.items())},
          open(f"{BASE}/taksonomi/hastalik-index.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# ---- reorganize markdown ------------------------------------------------
if os.path.isdir(f"{BASE}/content/blog/_toplanan") and not os.path.isdir(HAM):
    os.rename(f"{BASE}/content/blog/_toplanan", HAM)
# wipe previously generated category folders (keep _ham)
for d in os.listdir(NEW):
    p = os.path.join(NEW, d)
    if os.path.isdir(p) and d != "_ham":
        shutil.rmtree(p)

def inject_fm(text, extra):
    if not text.startswith("---"):
        return text
    _, fm, body = text.split("---", 2)
    add = []
    for k, v in extra.items():
        if isinstance(v, list):
            if v:
                add.append(f"{k}:")
                add += [f'  - "{x}"' for x in v]
            else:
                add.append(f"{k}: []")
        else:
            add.append(f'{k}: "{v}"')
    return "---" + fm + "\n".join(add) + "\n---" + body

for r in rows:
    src = f"{HAM}/{r['slug']}.md"
    if not os.path.exists(src):
        continue
    dst_dir = f"{NEW}/{r['ana_kategori']}/{r['alt_konu']}"
    os.makedirs(dst_dir, exist_ok=True)
    txt = open(src, encoding="utf-8").read()
    txt = inject_fm(txt, {
        "yeni_bolum": r["bolum"],
        "yeni_ana_kategori": r["ana_kategori_adi"],
        "yeni_ana_kategori_slug": r["ana_kategori"],
        "yeni_alt_konu": r["alt_konu"],
        "hastalik_etiketleri": sorted(set(x for x in r["hastaliklar"].split("; ") if x)),
        "lokasyon_etiketleri": sorted(set(x for x in r["lokasyon"].split("; ") if x)),
    })
    open(f"{dst_dir}/{r['slug']}.md", "w", encoding="utf-8").write(txt)

# ---- report -----------------------------------------------------------
print("=== BÖLÜMLER ===")
for s, n in sec_counts.most_common():
    print(f"{n:4d}  {s}")
print("\n=== ANA KATEGORİLER ===")
for m, n in method_counts.most_common():
    print(f"{n:4d}  {m:24s} {METHOD_LABEL.get(m, m)}")
print("\n=== ALT KONU DAĞILIMI (ana kategori bazında) ===")
for m, n in method_counts.most_common():
    parts = ", ".join(f"{k}:{v}" for k, v in method_sub[m].most_common())
    print(f"  {m:24s} -> {parts}")
print("\n=== HASTALIK ETİKETLERİ ===")
for c, lst in sorted(cond_index.items(), key=lambda x: -len(x[1])):
    print(f"{len(lst):4d}  {c}")
loc_total = sum(1 for r in rows if r["lokasyon"])
print(f"\nLokasyon etiketli yazı: {loc_total}")
print(f"Toplam yazı: {len(rows)}")
