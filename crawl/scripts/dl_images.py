#!/usr/bin/env python3
import os, ssl, sys, time, json, hashlib, urllib.request, urllib.parse

CTX = ssl._create_unverified_context()
BASE = "/Users/crea/Desktop/hayrusifa"
OUT = f"{BASE}/media/images"
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"

urls = [l.strip() for l in open(f"{BASE}/media/gorsel-url-listesi.txt", encoding="utf-8") if l.strip()]
manifest = {}
ok = fail = skip = 0
for i, u in enumerate(urls, 1):
    path = urllib.parse.urlsplit(u).path
    name = urllib.parse.unquote(os.path.basename(path)) or "img"
    name = name.replace("/", "_")
    h = hashlib.md5(u.encode()).hexdigest()[:8]
    fn = f"{h}__{name}"
    dest = os.path.join(OUT, fn)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        manifest[u] = fn; skip += 1; continue
    try:
        safe_u = urllib.parse.quote(u, safe=":/?#[]@!$&'()*+,;=~%")
        req = urllib.request.Request(safe_u, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
            data = r.read()
        with open(dest, "wb") as f:
            f.write(data)
        manifest[u] = fn; ok += 1
    except Exception as e:
        manifest[u] = None; fail += 1
        print(f"  FAIL {u} -> {e}", file=sys.stderr)
    if i % 50 == 0:
        print(f"{i}/{len(urls)}  ok={ok} skip={skip} fail={fail}")
    time.sleep(0.15)
json.dump(manifest, open(f"{BASE}/media/gorsel-manifest.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"DONE ok={ok} skip={skip} fail={fail} total={len(urls)}")
