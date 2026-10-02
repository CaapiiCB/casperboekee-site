#!/bin/sh
# Bouwt de site opnieuw vanuit bron/ en zet het resultaat in de hoofdmap (wat GitHub Pages toont).
# Gebruik:  sh publish.sh   daarna:  git add -A && git commit -m "..." && git push
set -e
cd "$(dirname "$0")"
python3 bron/build.py
cp -R bron/out/dist/. .
echo "Klaar. Controleer met: git status"
