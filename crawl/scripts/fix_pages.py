#!/usr/bin/env python3
"""Merge HTML-extracted content into thin page markdowns; group pages; build inventory."""
import json, os, re

BASE = "/Users/crea/Desktop/hayrusifa"
PGDIR = f"{BASE}/content/pages"
ext = json.load(open(f"{BASE}/crawl/pages-html-extract.json", encoding="utf-8"))
idx = {r["slug"]: r for r in json.load(open(f"{BASE}/crawl/icerik-index.json", encoding="utf-8")) if r["tur"] == "sayfa"}

GROUPS = {
    "kurumsal": ["klinigimiz", "doktorumuz", "ekibimiz", "terapistlerimiz", "hasta-yorumlari", "iletisim", "hayru-sifa"],
    "hizmet-sayfalari": ["hacamat", "suluk-terapi", "akapunktur", "manuel-terapi", "medikal-masaj", "prp",
                          "mizaca-gore-tedavi", "refleksoloji", "tam-kan-testi", "hastaliklarda-tedaviler"],
    "lokasyon": ["istanbul", "kocaeli", "trabzon"],
    "sistem": ["anasayfa", "home-ver2", "blog", "online-randevu-al", "magaza"],
}
slug2group = {s: g for g, lst in GROUPS.items() for s in lst}

inv = []
for fn in sorted(os.listdir(PGDIR)):
    if not fn.endswith(".md"):
        continue
    slug = fn[:-3]
    path = f"{PGDIR}/{fn}"
    txt = open(path, encoding="utf-8").read()
    parts = txt.split("---", 2)
    fm, body = parts[1], parts[2].strip()
    html_body = (ext.get(slug) or "").strip()
    used = "api"
    # if API body thin but HTML extract richer, append it
    if len(body) < 200 and len(html_body) > len(body):
        body = (body + "\n\n" + html_body).strip() if body else html_body
        used = "html"
    status = "dolu" if len(body) > 200 else ("zayif" if body else "BOŞ")
    grp = slug2group.get(slug, "sistem")
    # rewrite file with group + status in frontmatter
    add = f'grup: "{grp}"\nicerik_durumu: "{status}"\nicerik_kaynagi: "{used}"\n'
    open(path, "w", encoding="utf-8").write("---" + fm + add + "---\n\n" + body + "\n")
    inv.append((grp, slug, status, len(body),
                re.search(r'baslik: "([^"]*)"', fm).group(1) if re.search(r'baslik: "([^"]*)"', fm) else slug))

# move into group subfolders
for grp, slug, *_ in inv:
    d = f"{PGDIR}/{grp}"
    os.makedirs(d, exist_ok=True)
    src = f"{PGDIR}/{slug}.md"
    if os.path.exists(src):
        os.rename(src, f"{d}/{slug}.md")

# inventory doc
lines = ["# Sayfa Envanteri (24 kurumsal/hizmet sayfası)\n",
         "Eski sitenin sayfaları. `BOŞ` = kaynak sayfada içerik yok (Elementor stub), sıfırdan yazılacak.\n",
         "`icerik_kaynagi: html` = REST API boş döndü, içerik render HTML'den çıkarıldı.\n",
         "| Grup | Sayfa | Durum | ~karakter | Başlık |", "|---|---|---|---:|---|"]
for grp in ["sistem", "kurumsal", "hizmet-sayfalari", "lokasyon"]:
    for g, slug, status, ln, title in sorted(inv):
        if g == grp:
            lines.append(f"| {g} | `{slug}` | {status} | {ln} | {title} |")
open(f"{PGDIR}/_SAYFA-ENVANTERI.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
