"""Uso: pip install fonttools brotli && python scripts/build_hero.py

Gera assets/hero-light.svg e assets/hero-dark.svg — planta de loteamento.

Cada lote é um sistema. Fonte Archivo (OFL) instanciada, subsetada e embutida
em base64, porque o GitHub serve SVG como <img> e não carrega fonte externa.
"""
import base64, io, os, sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "assets")
os.makedirs(OUT, exist_ok=True)

# ---------- conteúdo ----------
NAME = ["Douglas", "Floriano"]
ROLE = "Engenheiro de software full-stack"
SUB = "Projeto, construo e mantenho SaaS em produção."
META = "Itirapuã, SP  /  desde 2018"

# (quadra-lote, nome, stack, estado)  estado: prod | obra | livre
LOTS_A = [
    ("A-01", "Lotemobile", "Laravel, React, AWS ECS", "prod"),
    ("A-02", "IB Ticket", "Laravel, React, Expo", "prod"),
    ("A-03", "IbPag", "Fastify, Kotlin, NFC", "prod"),
    ("A-04", "HRT Invest", "Laravel, Next.js", "prod"),
]
LOTS_B = [
    ("B-01", "MandaPedir", "Laravel 12, React, WhatsApp", "prod"),
    ("B-02", "Bolão Copa 2026", "Laravel, Next.js, WebSockets", "prod"),
    ("B-03", "HasGym", "Next.js, Expo, Gemini", "obra"),
    ("B-04", "Lote livre", "próximo projeto", "livre"),
]

THEMES = {
    "light": dict(text="#1F2328", muted="#59636E", line="#6F8C7A", contour="#E3EAE5",
                  road="#F2F4F2", prod_fill="#F8ECD0", prod_line="#A26A10",
                  accent="#8A560A", hatch="#B9C8BE"),
    "dark": dict(text="#E6EDF3", muted="#9198A1", line="#5B7A68", contour="#18241E",
                 road="#151B22", prod_fill="#33280F", prod_line="#D9A441",
                 accent="#E6B65C", hatch="#2C3D33"),
}

# ---------- fontes ----------
TEXT_ALL = "".join(NAME) + ROLE + SUB + META + "".join(
    "".join(l[:3]) for l in LOTS_A + LOTS_B) + \
    "Avenida Produção Quadra A B N em produção desenvolvimento livre 0 10 20 m 1:500 Planta de lotes folha 1/1 ,.-/:²"
SRC = os.path.join(HERE, ".fonts", "Archivo.ttf")
if not os.path.exists(SRC):
    import urllib.request
    os.makedirs(os.path.dirname(SRC), exist_ok=True)
    urllib.request.urlretrieve(
        "https://github.com/google/fonts/raw/main/ofl/archivo/Archivo%5Bwdth%2Cwght%5D.ttf", SRC)


def font_b64(wght, wdth):
    f = TTFont(SRC)
    instantiateVariableFont(f, {"wght": wght, "wdth": wdth}, inplace=True)
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["kern", "liga"]
    s = subset.Subsetter(opts); s.populate(text=TEXT_ALL); s.subset(f)
    buf = io.BytesIO(); f.flavor = "woff2"; f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


FONTS = {
    "ArchivoX": font_b64(760, 125),   # nome, expandida
    "ArchivoT": font_b64(430, 100),   # texto
    "ArchivoN": font_b64(560, 72),    # rótulos técnicos, estreita
}

# ---------- geometria ----------
W, H = 1200, 460
TOP, BOT = 36, 424
# eixo da avenida: borda esquerda e direita como retas levemente inclinadas
RL = lambda y: 846 - (y - TOP) * 0.11   # borda esquerda da rua
RR = lambda y: RL(y) + 46               # borda direita
AX0, BX1 = 600, 1164
# divisas entre lotes: (y na ponta externa, y na rua) — inclinadas como levantamento real
DIV_A = [(TOP, TOP), (128, 122), (222, 214), (318, 312), (BOT, BOT)]
DIV_B = [(TOP, TOP), (118, 126), (214, 220), (314, 318), (BOT, BOT)]


def quad_a(i):
    (yo0, yr0), (yo1, yr1) = DIV_A[i], DIV_A[i + 1]
    return [(AX0, yo0), (RL(yr0), yr0), (RL(yr1), yr1), (AX0, yo1)]


def quad_b(i):
    (yo0, yr0), (yo1, yr1) = DIV_B[i], DIV_B[i + 1]
    return [(RR(yr0), yr0), (BX1, yo0), (BX1, yo1), (RR(yr1), yr1)]


def pts(q):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in q)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def lot_svg(q, lot, idx, t):
    code, name, stack, state = lot
    fill = {"prod": t["prod_fill"], "obra": "url(#hatch)", "livre": "none"}[state]
    stroke = t["prod_line"] if state == "prod" else t["line"]
    dash = ' stroke-dasharray="5 5"' if state == "livre" else ""
    x = (AX0 if q[0][0] == AX0 else RR(TOP)) + 18
    y = min(p[1] for p in q) + 8
    name_col = t["text"] if state != "livre" else t["muted"]
    delay = 0.15 + idx * 0.09
    return f'''
  <g class="lot" style="animation-delay:{delay:.2f}s">
    <polygon points="{pts(q)}" fill="{fill}" stroke="{stroke}" stroke-width="1.4"{dash} stroke-linejoin="round"/>
    <text x="{x:.0f}" y="{y + 24:.0f}" class="n" fill="{t['accent'] if state == 'prod' else t['muted']}">{code}</text>
    <text x="{x:.0f}" y="{y + 56:.0f}" class="ln" fill="{name_col}">{esc(name)}</text>
  </g>'''


def contours(t):
    out = []
    for k in range(9):
        y = 20 + k * 52
        out.append(f'<path d="M560 {y} C 700 {y - 30}, 820 {y + 40}, 960 {y + 6} S 1160 {y - 26}, 1200 {y + 8}" '
                   f'fill="none" stroke="{t["contour"]}" stroke-width="1.2"/>')
    return "\n  ".join(out)


def build(theme):
    t = THEMES[theme]
    lots = "".join(lot_svg(quad_a(i), l, i, t) for i, l in enumerate(LOTS_A))
    lots += "".join(lot_svg(quad_b(i), l, i + 4, t) for i, l in enumerate(LOTS_B))
    road = [(RL(TOP), TOP), (RR(TOP), TOP), (RR(BOT), BOT), (RL(BOT), BOT)]
    cx, cy = (RL(230) + RR(230)) / 2, 230
    font_css = "\n".join(
        f"@font-face{{font-family:{n};src:url(data:font/woff2;base64,{b}) format('woff2');}}"
        for n, b in FONTS.items())
    legend_y = 404
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Douglas Floriano, engenheiro de software full-stack. Planta de lotes onde cada lote é um sistema em produção.">
<defs>
  <style>
{font_css}
.x{{font-family:ArchivoX,sans-serif;font-size:80px;letter-spacing:-1.5px}}
.t{{font-family:ArchivoT,sans-serif}}
.n{{font-family:ArchivoN,sans-serif;font-size:16px;letter-spacing:.3px}}
.ln{{font-family:ArchivoX,sans-serif;font-size:23px}}
.lot{{animation:in .55s cubic-bezier(.2,.7,.2,1) backwards}}
@keyframes in{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.lot{{animation:none}}}}
  </style>
  <pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="7" stroke="{t['hatch']}" stroke-width="2"/>
  </pattern>
  <clipPath id="map"><rect x="560" y="0" width="640" height="{H}"/></clipPath>
</defs>

<g clip-path="url(#map)">
  {contours(t)}
</g>

<polygon points="{pts(road)}" fill="{t['road']}" stroke="{t['line']}" stroke-width="1.4"/>
<text transform="translate({cx + 5:.1f} {cy}) rotate({-90 - 6.3:.1f})" text-anchor="middle" class="n" fill="{t['muted']}" letter-spacing="2">Avenida Produção</text>
{lots}

<!-- norte e escala -->
<g transform="translate(540 392)" fill="none" stroke="{t['muted']}" stroke-width="1.2">
  <path d="M0 -14 L6 6 L0 2 L-6 6 Z" fill="{t['muted']}"/>
</g>
<text x="540" y="424" text-anchor="middle" class="n" fill="{t['muted']}">N</text>

<!-- identidade -->
<text x="40" y="118" class="x" fill="{t['text']}">{NAME[0]}</text>
<text x="40" y="196" class="x" fill="{t['text']}">{NAME[1]}</text>
<text x="42" y="254" class="t" font-size="27" fill="{t['text']}">{ROLE}</text>
<text x="42" y="292" class="t" font-size="22" fill="{t['muted']}">{SUB}</text>
<text x="42" y="330" class="n" style="font-size:18px" fill="{t['muted']}">{META}</text>

<!-- legenda -->
<g transform="translate(42 {legend_y - 26})">
  <rect width="14" height="14" fill="{t['prod_fill']}" stroke="{t['prod_line']}" stroke-width="1.2"/>
  <text x="22" y="12.5" class="n" fill="{t['muted']}">em produção</text>
  <rect x="148" width="14" height="14" fill="url(#hatch)" stroke="{t['line']}" stroke-width="1.2"/>
  <text x="170" y="12.5" class="n" fill="{t['muted']}">em desenvolvimento</text>
  <rect x="340" width="14" height="14" fill="none" stroke="{t['line']}" stroke-width="1.2" stroke-dasharray="3 3"/>
  <text x="362" y="12.5" class="n" fill="{t['muted']}">lote livre</text>
</g>
<line x1="42" y1="{legend_y}" x2="502" y2="{legend_y}" stroke="{t['contour']}" stroke-width="1"/>
<text x="42" y="{legend_y + 20}" class="n" fill="{t['muted']}">Planta de lotes, folha 1/1</text>
<text x="502" y="{legend_y + 20}" text-anchor="end" class="n" fill="{t['muted']}">1:500</text>
</svg>
'''


for th in THEMES:
    p = os.path.join(OUT, f"hero-{th}.svg")
    open(p, "w").write(build(th))
    print(p, os.path.getsize(p) // 1024, "KB")
