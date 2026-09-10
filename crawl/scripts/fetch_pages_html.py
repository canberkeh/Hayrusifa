#!/usr/bin/env python3
"""Fetch rendered HTML for Elementor pages that return empty content via REST API."""
import os, re, ssl, time, json, urllib.request
import html2text
from bs4 import BeautifulSoup

CTX = ssl._create_unverified_context()
BASE = "/Users/crea/Desktop/hayrusifa"
RAW = f"{BASE}/crawl/raw-html"
os.makedirs(RAW, exist_ok=True)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

THIN = ["hastaliklarda-tedaviler", "hacamat", "terapistlerimiz", "doktorumuz", "ekibimiz",
        "iletisim", "blog", "hasta-yorumlari", "home-ver2", "akapunktur", "magaza",
        "online-randevu-al", "istanbul", "manuel-terapi", "prp", "trabzon", "kocaeli",
        "tam-kan-testi", "klinigimiz", "mizaca-gore-tedavi", "medikal-masaj", "suluk-terapi",
        "refleksoloji", "anasayfa"]

def md():
    h = html2text.HTML2Text(); h.body_width = 0; h.unicode_snob = True
    h.ignore_links = False; h.ignore_images = True; h.protect_links = True
    return h

def extract(htmls):
    soup = BeautifulSoup(htmls, "lxml")
    for sel in ["script", "style", "noscript", "svg", "form.search-form",
                "header#masthead", ".site-header", ".site-footer", "footer#colophon",
                ".elementor-location-header", ".elementor-location-footer",
                "nav", ".menu", "#site-navigation", ".breadcrumbs", ".breadcrumb",
                ".widget-area", "#secondary", ".sidebar", ".related-posts",
                ".elementor-widget-wp-widget-nav_menu", ".screen-reader-text"]:
        for el in soup.select(sel):
            el.decompose()
    root = (soup.select_one('div[data-elementor-type="wp-page"]')
            or soup.select_one('div[data-elementor-type="single-page"]')
            or soup.find("main")
            or soup.select_one(".article-content-outer-sidebar")
            or soup.find("article")
            or soup.body)
    text_md = md().handle(str(root)).strip()
    text_md = re.sub(r"\n{3,}", "\n\n", text_md)
    # drop leftover nav lines (short list items linking to menu)
    lines = [ln for ln in text_md.splitlines()
             if not re.match(r"^\s*\*\s*\[[^\]]{1,25}\]\(<https?://hayrusifa[^)]*>\)\s*$", ln)]
    return "\n".join(lines).strip()

out = {}
for slug in THIN:
    url = f"https://hayrusifa.com.tr/{slug}/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
            raw = r.read().decode("utf-8", "ignore")
        open(f"{RAW}/page-{slug}.html", "w", encoding="utf-8").write(raw)
        body = extract(raw)
        out[slug] = body
        print(f"{slug:26s} {len(body):6d} chars")
    except Exception as e:
        out[slug] = None
        print(f"{slug:26s} FAIL {e}")
    time.sleep(1.0)

json.dump(out, open(f"{BASE}/crawl/pages-html-extract.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("saved pages-html-extract.json")
