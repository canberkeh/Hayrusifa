#!/usr/bin/env python3
"""Pull all content from hayrusifa.com.tr via the WordPress REST API."""
import json, os, time, sys, ssl, urllib.request, urllib.error

SSLCTX = ssl._create_unverified_context()

BASE = "https://hayrusifa.com.tr/wp-json/wp/v2"
OUT = "/Users/crea/Desktop/hayrusifa/crawl/wp-api"
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

def get(url):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60, context=SSLCTX) as r:
                return json.loads(r.read().decode("utf-8")), r.headers
        except Exception as e:
            print(f"  retry {attempt+1} {url} -> {e}", file=sys.stderr)
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"failed: {url}")

def pull_all(kind, extra=""):
    page = 1
    items = []
    while True:
        url = f"{BASE}/{kind}?per_page=100&page={page}{extra}"
        try:
            data, hdr = get(url)
        except RuntimeError:
            break
        if not isinstance(data, list) or not data:
            break
        items.extend(data)
        total_pages = int(hdr.get("X-WP-TotalPages", "1"))
        print(f"{kind}: page {page}/{total_pages} (+{len(data)}, total {len(items)})")
        if page >= total_pages:
            break
        page += 1
        time.sleep(1.0)
    json.dump(items, open(f"{OUT}/{kind}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  saved {OUT}/{kind}.json ({len(items)})")
    return items

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "posts"):
        pull_all("posts")
    if which in ("all", "pages"):
        pull_all("pages")
    if which in ("all", "categories"):
        pull_all("categories")
    if which in ("all", "tags"):
        pull_all("tags")
    if which in ("all", "media"):
        pull_all("media")
    if which in ("all", "users"):
        pull_all("users")
