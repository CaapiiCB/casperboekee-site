"""Rendert alle previewpagina's op telefoon- en desktopbreedte en controleert links, overflow en fouten."""
import asyncio, sys, re
from pathlib import Path
from playwright.async_api import async_playwright
OUT = Path('out/preview').resolve()
SHOTS = Path('qa'); SHOTS.mkdir(exist_ok=True)
FONT_CSS = '''
@font-face{font-family:"Anton";src:local("DejaVu Sans Condensed Bold"),local("DejaVuSansCondensed-Bold");size-adjust:70%;}
@font-face{font-family:"Barlow";src:local("DejaVu Sans");size-adjust:88%;}
@font-face{font-family:"Barlow";font-weight:600;src:local("DejaVu Sans Bold");size-adjust:88%;}
@font-face{font-family:"Barlow Condensed";src:local("DejaVu Sans Condensed");size-adjust:86%;}
@font-face{font-family:"Barlow Condensed";font-weight:600;src:local("DejaVu Sans Condensed Bold");size-adjust:82%;}
'''
# De hoofdpagina is een fragment; zet er het skelet omheen zoals de viewer dat doet.
frag = (OUT/'index.html').read_text()
(OUT/'_main.html').write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><style>:root{color-scheme:light}body{margin:0;font:14px system-ui;background:#faf9f5}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'+frag+'</body></html>')
pages = ['_main.html'] + [str(p.relative_to(OUT)) for p in sorted(OUT.rglob('index.html')) if p != OUT/'index.html']
only = sys.argv[1:] 
async def main():
    problems = []
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        for vw, vh, tag in [(390, 844, 'm'), (1280, 800, 'd')]:
            ctx = await b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=1)
            await ctx.route(re.compile(r'^https?://'), lambda r: r.abort())
            for rel in pages:
                if only and not any(o in rel for o in only): continue
                pg = await ctx.new_page()
                errs = []
                pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'ERR_FAILED' not in m.text and 'net::' not in m.text else None)
                pg.on('pageerror', lambda e: errs.append(str(e)))
                await pg.goto((OUT/rel).as_uri())
                await pg.add_style_tag(content=FONT_CSS)
                await pg.wait_for_timeout(250)
                # lazy images laden
                await pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
                await pg.evaluate("async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){scrollTo(0,y);await new Promise(r=>setTimeout(r,60))} document.querySelectorAll('.gallery__scroller').forEach(s=>{s.scrollLeft=9999});await new Promise(r=>setTimeout(r,200));document.querySelectorAll('.gallery__scroller').forEach(s=>{s.scrollLeft=0});scrollTo(0,0)}")
                await pg.add_style_tag(content='.cta-bar{display:none!important}')
                await pg.wait_for_timeout(400)
                sw = await pg.evaluate('document.documentElement.scrollWidth')
                if sw > vw + 1: problems.append(f'{tag} {rel}: horizontale overflow {sw}>{vw}')
                broken = await pg.evaluate("[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.currentSrc||i.src)")
                if broken: problems.append(f'{tag} {rel}: kapotte afbeeldingen {broken}')
                if errs: problems.append(f'{tag} {rel}: console {errs}')
                name = rel.replace('/index.html','').replace('/','_').replace('.html','') or 'x'
                await pg.screenshot(path=str(SHOTS/f'{tag}-{name}.png'), full_page=True)
                await pg.close()
            await ctx.close()
        await b.close()
    # interne links
    for p in OUT.rglob('*.html'):
        if p.name == '_main.html': continue
        for href in re.findall(r'href="([^"#]+)(?:#[^"]*)?"', p.read_text()):
            if href.startswith(('http', 'mailto:', 'tel:')): continue
            if not (p.parent/href).resolve().exists(): problems.append(f'{p.relative_to(OUT)}: dode link {href}')
        for src in re.findall(r'(?:src|srcset)="([^"]+)"', p.read_text()):
            for s in [x.strip().split(' ')[0] for x in src.split(',')]:
                if s.startswith('http'): continue
                if not (p.parent/s).resolve().exists(): problems.append(f'{p.relative_to(OUT)}: ontbrekend bestand {s}')
    print('\n'.join(problems) if problems else 'geen problemen gevonden')
asyncio.run(main())
