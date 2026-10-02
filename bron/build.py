#!/usr/bin/env python3
"""Bouwt casperboekee.com.

    python3 build.py            -> out/dist     (voor GitHub Pages)
    python3 build.py preview    -> out/preview  (voor de Claude-preview)

Teksten, prijzen en contactgegevens staan in content.py.
"""
import json
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from content import LANGS, SITE

HERE = Path(__file__).parent
PREVIEW = len(sys.argv) > 1 and sys.argv[1] == "preview"
OUT = HERE / "out" / ("preview" if PREVIEW else "dist")

PAGES = {  # pagina -> sjabloon
    "home": "home.html",
    "personal-training": "pt.html",
    "muay-thai": "mt.html",
    "performance-scan": "scan.html",
    "contact": "contact.html",
    "privacy": "privacy.html",
}

# Oude Wix-adressen -> nieuwe pagina (alleen in de echte site)
REDIRECTS = {
    "book-online": ("home", "prices"),
    "blank": ("muay-thai", ""),
    "service-page/muay-thai-technique": ("muay-thai", ""),
    "service-page/personal-training-functional-strength": ("personal-training", ""),
    "service-page/performance-scan": ("performance-scan", ""),
    "service-page/training-schedule": ("home", "prices"),
}

env = Environment(loader=FileSystemLoader(HERE / "templates"), undefined=StrictUndefined, autoescape=True,
                  trim_blocks=False, lstrip_blocks=False)
IMAGES = json.loads((HERE / "static/img/meta.json").read_text())


def parts(lang, page):
    return ([] if lang == "en" else ["nl"]) + ([] if page == "home" else [page])


def abs_url(lang, page):
    p = "/".join(parts(lang, page))
    return SITE["base_url"] + (p + "/" if p else "")


def make_href(cur_lang, cur_page, depth):
    root = "../" * depth

    def href(page, anchor="", lang=None):
        lang = lang or cur_lang
        frag = "#" + anchor if anchor else ""
        if page == cur_page and lang == cur_lang and anchor:
            return frag
        p = "/".join(parts(lang, page))
        path = root + (p + "/" if p else "")
        if PREVIEW:
            path += "index.html"
        elif not path:
            path = "./"
        return path + frag

    return href, root


def jsonld(lang, page, t):
    biz = {
        "@context": "https://schema.org",
        "@type": ["LocalBusiness", "SportsActivityLocation"],
        "@id": SITE["base_url"] + "#business",
        "name": SITE["name"],
        "url": abs_url(lang, "home"),
        "image": SITE["base_url"] + "assets/img/og.jpg",
        "telephone": SITE["phone_tel"],
        "email": SITE["email"],
        "priceRange": "€€",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": SITE["street"],
            "addressLocality": SITE["city"],
            "addressCountry": "NL",
        },
        "areaServed": "Amsterdam",
        "founder": {"@type": "Person", "name": SITE["person"], "jobTitle": "Personal Trainer"},
        "sameAs": [SITE["instagram"]],
    }
    if SITE["postcode"]:
        biz["address"]["postalCode"] = SITE["postcode"]
    graph = [biz]
    faq_keys = {
        "home": ["results", "one", "coaching", "mt", "mt_expect", "beginners", "where", "book", "pay"],
        "personal-training": t["pt"]["faq"],
        "muay-thai": t["mt"]["faq"],
    }.get(page)
    if faq_keys:
        graph.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": t["faq"]["items"][k][0],
                            "acceptedAnswer": {"@type": "Answer", "text": t["faq"]["items"][k][1]}} for k in faq_keys],
        })
    return json.dumps(graph, ensure_ascii=False)


def render(lang, page, template, out_rel, depth, extra=None):
    t = LANGS[lang]
    href, root = make_href(lang, page, depth)
    is_main_preview = PREVIEW and lang == "en" and page == "home"
    meta = t["meta"].get(page, {"title": t.get("notfound", {}).get("h1", ""), "desc": ""})
    ctx = {
        "t": t, "site": SITE, "page": page, "root": root, "href": href, "images": IMAGES,
        "preview": PREVIEW, "fragment": is_main_preview,
        "page_title": "Casper Boekee Website" if is_main_preview else meta["title"],
        "page_desc": meta["desc"],
        "abs_url": abs_url(lang, page) if page in PAGES else SITE["base_url"],
        "alternates": [("en", abs_url("en", page)), ("nl", abs_url("nl", page)), ("x-default", abs_url("en", page))] if page in PAGES else [],
        "lang_href": (lambda l: href(page if page in PAGES else "home", lang=l)),
        "cta_href": href("home", "contact") if page == "home" else href("contact", "contact"),
        "wa_href": SITE["whatsapp"] + "?text=" + quote(t["whatsapp_text"]),
        "jsonld": jsonld(lang, page, t) if page in PAGES else "",
        "noindex": False,
    }
    ctx.update(extra or {})
    html = env.get_template(template).render(**ctx)
    dest = OUT / out_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def redirect_page(out_rel, target_abs):
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Casper Boekee</title>
<link rel="canonical" href="{target_abs}">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={target_abs}">
<script>location.replace({json.dumps(target_abs)});</script>
</head><body><p><a href="{target_abs}">{target_abs}</a></p></body></html>
"""
    dest = OUT / out_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    # assets
    for sub in ("css", "js"):
        shutil.copytree(HERE / "static" / sub, OUT / "assets" / sub)
    if (HERE / "static/video").exists():
        shutil.copytree(HERE / "static/video", OUT / "assets/video")
    (OUT / "assets/img").mkdir(parents=True)
    for f in (HERE / "static/img").iterdir():
        if f.suffix in (".webp", ".jpg", ".svg", ".png"):
            shutil.copy(f, OUT / "assets/img" / f.name)

    urls = []
    for lang in LANGS:
        for page, template in PAGES.items():
            p = parts(lang, page)
            render(lang, page, template, "/".join(p + ["index.html"]), len(p))
            urls.append(abs_url(lang, page))

    if not PREVIEW:
        render("en", "404", "notfound.html", "404.html", 0,
               {"noindex": True, "root": "/", "href": lambda page, anchor="", lang=None: "/" + "/".join(parts(lang or "en", page)) + ("/" if parts(lang or "en", page) else "") + ("#" + anchor if anchor else ""),
                "lang_href": lambda l: "/" if l == "en" else "/nl/",
                "cta_href": "/contact/#contact"})
        for old, (page, anchor) in REDIRECTS.items():
            for lang in LANGS:
                prefix = "" if lang == "en" else "nl/"
                target = abs_url(lang, page) + ("#" + anchor if anchor else "")
                redirect_page(f"{prefix}{old}/index.html", target)
        (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE['base_url']}sitemap.xml\n")
        sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        sm += [f"  <url><loc>{u}</loc></url>" for u in urls]
        sm.append("</urlset>")
        (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n")
        (OUT / ".nojekyll").write_text("")
    n = sum(1 for _ in OUT.rglob("*") if _.is_file())
    print(f"{'preview' if PREVIEW else 'dist'}: {n} bestanden in {OUT}")


if __name__ == "__main__":
    main()
