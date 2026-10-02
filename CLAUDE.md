# casperboekee.com — werkinstructies voor Claude

Website van Casper Boekee Personal Training (personal trainer in Amsterdam; Muay Thai, strength & conditioning, functional training; traint bij Patrick's Gym). Casper is geen programmeur: leg alles kort en in gewoon Nederlands uit.

## Hoe het werkt
- Statische site, gebouwd met Python + Jinja2. Gehost op GitHub Pages vanuit de hoofdmap van deze repo (branch `main`).
- **Bron staat in `bron/`, de live site in de hoofdmap.** Bewerk nooit de HTML in de hoofdmap met de hand; pas de bron aan en bouw opnieuw.
  - `bron/content.py`: alle teksten (EN + NL), prijzen, contactgegevens, instellingen (`SITE`).
  - `bron/templates/`: Jinja-sjablonen (`base.html`, `macros.html`, pagina's).
  - `bron/static/`: CSS, JS, afbeeldingen (webp, korte namen), video.
  - `bron/build.py`: bouwt naar `bron/out/dist/`. Afbeeldingen krijgen bij het bouwen het voorvoegsel `casper-boekee-personal-trainer-` (voor Google Afbeeldingen). Maakt ook sitemap (met afbeeldingen), robots.txt, JSON-LD en redirects van oude Wix-URL's.
  - `bron/qa.py`: Playwright-check (screenshots desktop/mobiel).
- Publiceren: `sh publish.sh` → `git add -A && git commit && git push`. GitHub Pages is binnen ~1 minuut bijgewerkt.
- Vereist: `pip install jinja2` (en `pillow` voor make_images.py, `playwright` voor qa.py).

## Vaste afspraken
- Tweetalig: Engels op `/`, Nederlands op `/nl/`. Elke tekstwijziging in beide talen.
- Prijzen (één plek in `SITE`): €85 per sessie, €850 voor 10, Performance Scan €250. Benadruk dat intake/assessments inbegrepen zijn.
- Performance Scan staat op "binnenkort" (`scan_soon: True`). Pas op `False` zetten als Casper dat zegt.
- Casper is PT, geen arts: geen medische claims of diagnoses; de scan is screening, geen medisch onderzoek. Disclaimer-pagina bestaat (`/disclaimer/`).
- Huisstijl: zwart + oranje.
- Contactformulier: Web3Forms (`form_key` in `SITE`). Statistieken: GoatCounter (`casperboekee`), cookieloos.
- Reviews komen later via Google Bedrijfsprofiel (lijst `reviews` in `SITE`, sectie verschijnt vanzelf als die gevuld is).
- `credit_url` in `SITE`: Spotify-link van Mory (trainingsmaatje op de foto's, producer/DJ). Leeg = geen vermelding onder de foto's.
- Niet aankomen: `CNAME` (www.casperboekee.com), DNS (staat bij Wix; MX-records zijn Google Workspace-mail).

## Gerelateerd
- `CaapiiCB/muaythaiamsterdam`: stuurt muaythaiamsterdam.com door naar /muay-thai/.
- Google Search Console: domeineigendom `casperboekee.com`.
