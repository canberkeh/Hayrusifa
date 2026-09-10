#!/usr/bin/env bash
# site/ klasörünü GitHub Pages'e (canberkeh.github.io/Hayrusifa) yayınlar.
# Proje kökü mutlak yollar (/assets, /blog ...) kullanır; Pages proje-sitesi
# /Hayrusifa/ alt yolunda çalıştığı için bu kopyada yollar /Hayrusifa/ ile öneklenir.
# main branch'teki site/ dokunulmadan kalır (o hayrusifa.com.tr kökü içindir).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REPO_URL="https://github.com/canberkeh/Hayrusifa.git"
PREFIX="/Hayrusifa"
TMP="$(mktemp -d)"

echo "→ site yeniden üretiliyor"
python3 "$ROOT/crawl/scripts/build_site.py" >/dev/null

echo "→ kopya + yol öneki ($PREFIX)"
cp -R "$ROOT/site/." "$TMP/"
find "$TMP" -name '*.html' -exec sed -i '' -E "s#(href|src)=\"/#\\1=\"$PREFIX/#g" {} +
touch "$TMP/.nojekyll"

echo "→ gh-pages force-push"
cd "$TMP"
git init -q
git checkout -q -b gh-pages
git add -A
git -c user.name="Can Berke Horozal" -c user.email="canberkehorozal@gmail.com" \
    commit -q -m "Deploy site $(date +%Y-%m-%d\ %H:%M)"
git push -q -f "$REPO_URL" gh-pages
cd - >/dev/null
rm -rf "$TMP"
echo "✓ https://canberkeh.github.io/Hayrusifa/ (1-2 dk içinde güncellenir)"
