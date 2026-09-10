#!/usr/bin/env python3
"""Convert WP API JSON dumps into categorized markdown + taxonomy files."""
import json, os, re, html, sys
from datetime import datetime
import html2text
from bs4 import BeautifulSoup

API = "/Users/crea/Desktop/hayrusifa/crawl/wp-api"
BASE = "/Users/crea/Desktop/hayrusifa"
CONTENT = f"{BASE}/content"

def load(name):
    p = f"{API}/{name}.json"
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []

posts = load("posts")
pages = load("pages")
cats = load("categories")
tags = load("tags")
users = load("users")

cat_by_id = {c["id"]: c for c in cats}
tag_by_id = {t["id"]: t for t in tags}
user_by_id = {u["id"]: u for u in users}

def cat_path(cid):
    parts = []
    seen = set()
    while cid and cid in cat_by_id and cid not in seen:
        seen.add(cid)
        c = cat_by_id[cid]
        parts.append(c["name"])
        cid = c["parent"]
    return " / ".join(reversed(parts))

def mk_md():
    h = html2text.HTML2Text()
    h.body_width = 0
    h.unicode_snob = True
    h.ignore_emphasis = False
    h.ignore_links = False
    h.ignore_images = False
    h.protect_links = True
    h.wrap_links = False
    return h

def clean_html(raw):
    soup = BeautifulSoup(raw or "", "lxml")
    for sel in ["script", "style", "iframe", "form", "ins",
                ".sharedaddy", ".jp-relatedposts", ".addtoany_share_save_container",
                ".wp-block-buttons", ".rll-youtube-player", "noscript"]:
        for el in soup.select(sel):
            el.decompose()
    return str(soup)

def collect_images(raw, yoast):
    urls = []
    og = (yoast or {}).get("og_image") or []
    for o in og:
        if isinstance(o, dict) and o.get("url"):
            urls.append(o["url"])
    soup = BeautifulSoup(raw or "", "lxml")
    for img in soup.find_all("img"):
        for attr in ("data-src", "src", "data-lazy-src"):
            if img.get(attr):
                urls.append(img[attr]); break
        ss = img.get("srcset") or img.get("data-srcset")
        if ss:
            first = ss.split(",")[0].strip().split(" ")[0]
            if first:
                urls.append(first)
    out, seen = [], set()
    for u in urls:
        u = u.strip()
        if u and u not in seen and not u.startswith("data:"):
            seen.add(u); out.append(u)
    return out

def yamls(v):
    if v is None:
        return '""'
    s = str(v).replace('"', "'").replace("\n", " ").strip()
    return f'"{s}"'

def frontmatter(d):
    lines = ["---"]
    for k, v in d.items():
        if isinstance(v, list):
            if not v:
                lines.append(f"{k}: []")
            else:
                lines.append(f"{k}:")
                for it in v:
                    lines.append(f"  - {yamls(it)}")
        else:
            lines.append(f"{k}: {yamls(v)}")
    lines.append("---\n")
    return "\n".join(lines)

all_img_urls = set()
index_rows = []

def process(item, kind, outdir):
    slug = item.get("slug") or f"id-{item['id']}"
    title = html.unescape(BeautifulSoup(item["title"]["rendered"], "lxml").get_text()).strip()
    raw = item.get("content", {}).get("rendered", "")
    excerpt = html.unescape(BeautifulSoup(item.get("excerpt", {}).get("rendered", ""), "lxml").get_text()).strip()
    excerpt = re.sub(r"\s+", " ", excerpt)
    yoast = item.get("yoast_head_json") or {}
    meta_desc = yoast.get("description") or yoast.get("og_description") or ""
    cids = item.get("categories", []) or []
    tids = item.get("tags", []) or []
    cat_names = [cat_by_id[c]["name"] for c in cids if c in cat_by_id]
    cat_paths = [cat_path(c) for c in cids if c in cat_by_id]
    tag_names = [tag_by_id[t]["name"] for t in tids if t in tag_by_id]
    imgs = collect_images(raw, yoast)
    all_img_urls.update(imgs)
    featured = imgs[0] if imgs else ""
    md_body = mk_md().handle(clean_html(raw)).strip()
    md_body = re.sub(r"\n{3,}", "\n\n", md_body)
    fm = frontmatter({
        "baslik": title,
        "slug": slug,
        "tur": kind,
        "kaynak_url": item.get("link", ""),
        "yayin_tarihi": item.get("date", ""),
        "guncelleme_tarihi": item.get("modified", ""),
        "wp_kategoriler": cat_names,
        "wp_kategori_yollari": cat_paths,
        "wp_etiketler": tag_names,
        "meta_aciklama": re.sub(r"\s+", " ", meta_desc).strip(),
        "ozet": excerpt,
        "one_cikan_gorsel": featured,
        "gorseller": imgs,
        "kelime_sayisi": len(re.findall(r"\w+", md_body)),
    })
    os.makedirs(outdir, exist_ok=True)
    open(f"{outdir}/{slug}.md", "w", encoding="utf-8").write(fm + "\n" + md_body + "\n")
    index_rows.append({
        "slug": slug, "baslik": title, "tur": kind, "url": item.get("link", ""),
        "tarih": item.get("date", "")[:10], "guncelleme": item.get("modified", "")[:10],
        "wp_kategoriler": cat_names, "wp_kategori_yollari": cat_paths,
        "wp_etiket_sayisi": len(tag_names), "kelime_sayisi": len(re.findall(r"\w+", md_body)),
        "gorsel_sayisi": len(imgs), "meta_aciklama": re.sub(r"\s+", " ", meta_desc).strip()[:300],
    })

for p in posts:
    process(p, "yazi", f"{CONTENT}/blog/_toplanan")
for p in pages:
    process(p, "sayfa", f"{CONTENT}/pages")

# taxonomy tree
tree = {}
post_cat_map = {}
for p in posts:
    for cid in p.get("categories", []):
        post_cat_map.setdefault(cid, []).append(p.get("slug"))
for c in cats:
    tree[c["id"]] = {
        "id": c["id"], "slug": c["slug"], "isim": c["name"], "parent": c["parent"],
        "wp_sayac": c["count"], "gercek_yazi_sayisi": len(post_cat_map.get(c["id"], [])),
        "yol": cat_path(c["id"]), "link": c.get("link", ""),
    }
json.dump(sorted(tree.values(), key=lambda x: (-x["gercek_yazi_sayisi"], x["isim"])),
          open(f"{BASE}/taksonomi/eski-kategoriler.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

json.dump(index_rows, open(f"{BASE}/crawl/icerik-index.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

# tag list
json.dump(sorted([{"slug": t["slug"], "isim": t["name"], "sayac": t["count"]} for t in tags],
                 key=lambda x: -x["sayac"]),
          open(f"{BASE}/taksonomi/eski-etiketler.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

open(f"{BASE}/media/gorsel-url-listesi.txt", "w", encoding="utf-8").write(
    "\n".join(sorted(all_img_urls)) + "\n")

print(f"posts: {len(posts)}  pages: {len(pages)}  cats: {len(cats)}  tags: {len(tags)}")
print(f"unique image urls: {len(all_img_urls)}")
print(f"index rows: {len(index_rows)}")
