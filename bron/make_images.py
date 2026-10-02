"""Snijdt en verkleint de originele foto's naar webformaten (WebP)."""
from PIL import Image, ImageOps
import os
UP = '/root/.claude/uploads/4d42314b-e6cc-5e52-afd8-474af3723639/'
OUT = 'static/img/'
S = {  # korte naam -> bronbestand
 'ali': '08d050c7', 'smile': '94f94112', 'glovefg': '2550d323', 'elbowside': '3da89d94',
 'elbowcorner': '144f664f', 'kick': 'c6f609b2', 'gloveclose': 'ae12a776', 'clinch': '0d06f4a3',
 'clinchbw': '2747070b', 'face': '01adcabf', 'padsportrait': '1321dbb8', 'padsbw': '97f6fb4e',
 'belly': '2af4a9c0', 'belly2': '40ed5e8e', 'intense': 'fd6a4d3b',
}
# naam: (bron, (l,t,r,b) als fractie of None, [breedtes])
JOBS = {
 'hero-wide':   ('ali', (0.17, 0.0, 1.0, 1.0), [1800, 1100]),
 'hero-tall':   ('ali', (0.40, 0.0, 0.932, 1.0), [1000, 640]),
 'card-pt':     ('padsportrait', (0.0, 0.08, 1.0, 0.524), [1100, 640]),
 'card-mt':     ('kick', None, [1100, 640]),
 'band':        ('clinchbw', (0.0, 0.06, 1.0, 0.94), [1800, 900]),
 'about':       ('belly', (0.0, 0.03, 1.0, 0.868), [1000, 640]),
 'hero-pt':     ('smile', (0.0, 0.04, 1.0, 0.88), [1800, 900]),
 'hero-mt':     ('kick', (0.0, 0.0, 1.0, 0.84), [1800, 900]),
 'hero-scan':   ('glovefg', (0.0, 0.05, 1.0, 0.89), [1800, 900]),
 'pt-mid':      ('glovefg', None, [1400, 800]),
 'contact':     ('belly2', (0.0, 0.03, 1.0, 0.70), [900, 600]),
 'g-elbowside': ('elbowside', None, [1200, 700]),
 'g-gloveclose':('gloveclose', None, [1200, 700]),
 'g-elbowcorner':('elbowcorner', None, [1200, 700]),
 'g-clinch':    ('clinch', None, [1200, 700]),
 'g-intense':   ('intense', None, [800, 500]),
 'g-smile':     ('smile', None, [1200, 700]),
 'g-face':      ('face', (0.0, 0.0, 1.0, 0.80), [800, 500]),
}
def load(key):
    f = [x for x in os.listdir(UP) if x.startswith(S[key])][0]
    return ImageOps.exif_transpose(Image.open(UP + f)).convert('RGB')
cache = {}
meta = {}
BW = {'hero-scan'}  # in zwart-wit
for name, (src, box, widths) in JOBS.items():
    im = cache.get(src) or load(src); cache[src] = im
    if box:
        W, H = im.size
        im2 = im.crop((int(box[0]*W), int(box[1]*H), int(box[2]*W), int(box[3]*H)))
    else:
        im2 = im
    for w in widths:
        h = round(im2.height * w / im2.width)
        r = im2.resize((w, h), Image.LANCZOS)
        if name in BW: r = r.convert('L').convert('RGB')
        r.save(f'{OUT}{name}-{w}.webp', 'WEBP', quality=84, method=6)
    meta[name] = (widths, round(im2.width / im2.height, 4))
# Open Graph-afbeelding (JPEG, 1200x630)
im = cache['ali']; W, H = im.size
cw = W * 0.83; ch = cw * 630 / 1200
og = im.crop((int(W*0.17), int(H*0.02), W, int(H*0.02 + ch))).resize((1200, 630), Image.LANCZOS)
og.save(OUT + 'og.jpg', 'JPEG', quality=82, optimize=True, progressive=True)
import json; json.dump(meta, open('static/img/meta.json', 'w'), indent=1)
print(meta)
