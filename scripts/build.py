"""Gera os SVGs do perfil em assets/.

Uso: pip install fonttools brotli && python scripts/build.py

O GitHub serve SVG como <img>: sem JS, sem fonte externa. Por isso a Geist
(OFL) é instanciada, subsetada e embutida em base64 em cada arquivo.
Ícones: simple-icons (CC0) e lucide (ISC), em scripts/res/.
"""
import base64, io, os, re, urllib.request
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools import subset

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "res")
OUT = os.path.join(HERE, "..", "assets")
FONT_DIR = os.path.join(HERE, ".fonts")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- tokens
C = dict(
    bg="#0B0F1A", panel="#0F1526", line="#1E2742", grid="#141B30",
    text="#EDF0F7", soft="#B7C0D8", muted="#7D88A6",
    accent="#8B9DFF", accent2="#5EEAD4", ok="#4ADE80",
)

# ---------------------------------------------------------------- conteúdo
HERO = dict(
    name="Douglas Floriano",
    role="Senior Full-Stack Engineer",
    stack="Laravel  ·  React  ·  Node.js  ·  AWS",
    pill="Shipping SaaS since 2018",
    log=[("lotemobile", "ecs"), ("ib-ticket", "ec2"), ("ibpag", "pos"),
         ("hrt-invest", "web"), ("mandapedir", "api")],
)

PROJECTS = [
    dict(slug="lotemobile", name="Lotemobile", icon="map-pinned", owner="IB System",
         chips=["Laravel", "React", "AWS ECS"], state="prod",
         pt="SaaS para loteadoras: contratos, boletos,\nassinatura eletrônica e WhatsApp.",
         en="SaaS for land developers: contracts,\nbilling, e-signature and WhatsApp."),
    dict(slug="ibticket", name="IB Ticket", icon="ticket", owner="IB System",
         chips=["Laravel", "React", "Expo"], state="prod",
         pt="Venda e validação de ingressos para\nvárias organizações, PIX e cartão.",
         en="Multi-tenant ticketing: online sales,\ncheck-in app, PIX and card payments."),
    dict(slug="ibpag", name="IbPag", icon="smartphone-nfc", owner="IB System",
         chips=["Fastify", "Kotlin", "NFC"], state="prod",
         pt="Pagamento pré-pago por NFC em eventos,\nPDV rodando na maquininha Android.",
         en="Prepaid NFC payments for events,\nPOS running on Android terminals."),
    dict(slug="hrtinvest", name="HRT Invest", icon="trending-up", owner="IB System",
         chips=["Laravel", "Next.js", "Expo"], state="prod",
         pt="Investimento em debêntures tokenizadas,\ncom contratos e assinatura digital.",
         en="Tokenized debenture investing,\nwith digital contracts and signing."),
    dict(slug="mandapedir", name="MandaPedir", icon="utensils-crossed", owner="autoral",
         chips=["Laravel", "React", "WhatsApp"], state="prod",
         pt="Bar e restaurante: PDV, comandas,\ndelivery e pedido na mesa por QR code.",
         en="Bar and restaurant suite: POS, tabs,\ndelivery and QR code table ordering."),
    dict(slug="bolao", name="Bolão Copa 2026", icon="trophy", owner="autoral",
         chips=["Next.js", "PostgreSQL", "WebSockets"], state="prod",
         pt="Bolão da Copa do Mundo com palpites\ne ranking em tempo real.",
         en="World Cup prediction pool with\na real-time leaderboard."),
]
L10N = {
    "pt": dict(prod="Em produção", own="Projeto próprio"),
    "en": dict(prod="In production", own="Own product"),
}
STACK = ["laravel", "php", "nodedotjs", "typescript", "react", "nextdotjs", "tailwindcss",
         "expo", "kotlin", "mariadb", "postgresql", "redis", "docker", "amazonaws", "githubactions"]
CONTACT = [("linkedin", "LinkedIn"), ("mail", "E-mail"), ("globe", "Portfolio")]

# ---------------------------------------------------------------- fontes
FONT_URLS = {
    "Geist.ttf": "https://github.com/google/fonts/raw/main/ofl/geist/Geist%5Bwght%5D.ttf",
    "GeistMono.ttf": "https://github.com/google/fonts/raw/main/ofl/geistmono/GeistMono%5Bwght%5D.ttf",
}


def font_path(name):
    p = os.path.join(FONT_DIR, name)
    if not os.path.exists(p):
        os.makedirs(FONT_DIR, exist_ok=True)
        urllib.request.urlretrieve(FONT_URLS[name], p)
    return p


_cache = {}


def font_face(family, file, wght, text):
    key = (family, file, wght, text)
    if key not in _cache:
        f = TTFont(font_path(file))
        instantiateVariableFont(f, {"wght": wght}, inplace=True)
        o = subset.Options(); o.flavor = "woff2"; o.layout_features = ["kern"]; o.drop_tables += ["meta"]
        s = subset.Subsetter(o); s.populate(text=text + " "); s.subset(f)
        b = io.BytesIO(); f.flavor = "woff2"; f.save(b)
        _cache[key] = base64.b64encode(b.getvalue()).decode()
    return f"@font-face{{font-family:{family};src:url(data:font/woff2;base64,{_cache[key]}) format('woff2');}}"


def fonts(sans_bold="", sans="", mono=""):
    out = []
    if sans_bold: out.append(font_face("GB", "Geist.ttf", 620, sans_bold))
    if sans: out.append(font_face("G", "Geist.ttf", 420, sans))
    if mono: out.append(font_face("GM", "GeistMono.ttf", 450, mono))
    return "\n".join(out)


# ---------------------------------------------------------------- ícones
def lucide(name):
    raw = open(os.path.join(RES, "lu", f"{name}.svg")).read()
    return re.search(r">\s*(.*)</svg>", raw.split("-->")[-1], re.S).group(1).strip()


def simple(name):
    raw = open(os.path.join(RES, "si", f"{name}.svg")).read()
    return re.search(r'<path d="([^"]+)"', raw).group(1)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def svg(w, h, label, body, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(label)}"><title>{esc(label)}</title>\n'
            f'<defs><style>{style}</style></defs>\n{body}\n</svg>\n')


def write(name, content):
    open(os.path.join(OUT, name), "w").write(content)
    print(f"{name:28s} {len(content) // 1024:3d} KB")


# ---------------------------------------------------------------- hero
def hero():
    W, H = 1200, 440
    h = HERO
    log_lines = [f"✓ {n:<12} {t:<5} live" for n, t in h["log"]]
    mono_text = h["pill"] + h["stack"] + "".join(log_lines) + "$ deploy --all deploy.log 200 OK"
    style = fonts(sans_bold=h["name"], sans=h["role"], mono=mono_text) + f"""
.name{{font-family:GB,sans-serif;font-size:72px;letter-spacing:-2.6px;fill:{C['text']}}}
.role{{font-family:G,sans-serif;font-size:30px;letter-spacing:-.4px;fill:{C['soft']}}}
.m{{font-family:GM,monospace;font-size:19px;fill:{C['muted']}}}
.cur{{animation:b 1.1s steps(1) infinite}}
@keyframes b{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.cur{{animation:none}}}}"""
    grid = "".join(f'<path d="M{x} 0V{H}"/>' for x in range(0, W, 40)) + \
           "".join(f'<path d="M0 {y}H{W}"/>' for y in range(0, H, 40))
    tx, ty, tw, th = 728, 84, 420, 272
    rows = []
    for i, (n, t) in enumerate(h["log"]):
        y = ty + 112 + i * 30
        rows.append(f'<text x="{tx + 28}" y="{y}" class="m"><tspan fill="{C["ok"]}">✓</tspan>'
                    f'<tspan fill="{C["text"]}" dx="12">{n}</tspan></text>'
                    f'<text x="{tx + 232}" y="{y}" class="m">{t}</text>'
                    f'<text x="{tx + tw - 28}" y="{y}" class="m" text-anchor="end" fill="{C["accent2"]}">200 OK</text>')
    body = f"""
<defs>
  <radialGradient id="g1" cx="82%" cy="10%" r="60%"><stop offset="0" stop-color="{C['accent']}" stop-opacity=".30"/><stop offset="1" stop-color="{C['accent']}" stop-opacity="0"/></radialGradient>
  <radialGradient id="g2" cx="8%" cy="100%" r="55%"><stop offset="0" stop-color="{C['accent2']}" stop-opacity=".14"/><stop offset="1" stop-color="{C['accent2']}" stop-opacity="0"/></radialGradient>
  <radialGradient id="fade" cx="50%" cy="40%" r="75%"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <mask id="gm"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="28"/></clipPath>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C['accent']}" stop-opacity=".55"/><stop offset=".5" stop-color="{C['line']}"/><stop offset="1" stop-color="{C['accent2']}" stop-opacity=".35"/></linearGradient>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{C['bg']}"/>
  <g stroke="{C['grid']}" stroke-width="1" mask="url(#gm)">{grid}</g>
  <rect width="{W}" height="{H}" fill="url(#g1)"/>
  <rect width="{W}" height="{H}" fill="url(#g2)"/>
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="27.5" fill="none" stroke="url(#edge)" stroke-width="1.5"/>

<g transform="translate(64 92)">
  <rect width="302" height="38" rx="19" fill="{C['panel']}" stroke="{C['line']}"/>
  <circle cx="22" cy="19" r="5" fill="{C['ok']}"/><circle cx="22" cy="19" r="9" fill="{C['ok']}" opacity=".18"/>
  <text x="38" y="25.5" class="m" style="font-size:17px" fill="{C['soft']}">{h['pill']}</text>
</g>
<text x="60" y="218" class="name">{h['name']}</text>
<text x="64" y="272" class="role">{h['role']}</text>
<text x="64" y="330" class="m" fill="{C['accent']}">{esc(h['stack'])}</text>

<g>
  <rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="16" fill="{C['panel']}" fill-opacity=".92" stroke="{C['line']}"/>
  <path d="M{tx} {ty + 48}H{tx + tw}" stroke="{C['line']}"/>
  <circle cx="{tx + 26}" cy="{ty + 24}" r="6" fill="#3A4363"/><circle cx="{tx + 46}" cy="{ty + 24}" r="6" fill="#3A4363"/><circle cx="{tx + 66}" cy="{ty + 24}" r="6" fill="#3A4363"/>
  <text x="{tx + tw / 2}" y="{ty + 30}" class="m" style="font-size:16px" text-anchor="middle">deploy.log</text>
  <text x="{tx + 28}" y="{ty + 82}" class="m"><tspan fill="{C['accent']}">$</tspan><tspan fill="{C['text']}" dx="10">deploy --all</tspan></text>
  {''.join(rows)}
  <rect class="cur" x="{tx + 28}" y="{ty + th - 30}" width="11" height="20" fill="{C['accent']}"/>
</g>"""
    write("hero.svg", svg(W, H, f"{h['name']}, {h['role']}", body, style))


# ---------------------------------------------------------------- cards
def card(p, lang):
    W, H = 600, 270
    t = L10N[lang]
    desc = p[lang].split("\n")
    status = t["prod"]
    owner = p["owner"] if p["owner"] != "autoral" else t["own"]
    chips_text = "".join(p["chips"])
    style = fonts(sans_bold=p["name"], sans="".join(desc) + status + owner, mono=chips_text) + f"""
.n{{font-family:GB,sans-serif;font-size:32px;letter-spacing:-.8px;fill:{C['text']}}}
.d{{font-family:G,sans-serif;font-size:21px;fill:{C['soft']}}}
.s{{font-family:G,sans-serif;font-size:17px}}
.c{{font-family:GM,monospace;font-size:16px;fill:{C['soft']}}}"""
    chips, cx = [], 32
    for ch in p["chips"]:
        w = 24 + len(ch) * 9.7
        chips.append(f'<rect x="{cx}" y="206" width="{w:.0f}" height="34" rx="9" fill="{C["bg"]}" stroke="{C["line"]}"/>'
                     f'<text x="{cx + w / 2:.0f}" y="228.5" class="c" text-anchor="middle">{esc(ch)}</text>')
        cx += w + 10
    sw = 40 + len(status) * 8.6
    body = f"""
<defs>
  <radialGradient id="glow" cx="0%" cy="0%" r="70%"><stop offset="0" stop-color="{C['accent']}" stop-opacity=".16"/><stop offset="1" stop-color="{C['accent']}" stop-opacity="0"/></radialGradient>
  <linearGradient id="tile" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C['accent']}"/><stop offset="1" stop-color="{C['accent2']}"/></linearGradient>
</defs>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="22" fill="{C['panel']}" stroke="{C['line']}" stroke-width="1.5"/>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="22" fill="url(#glow)"/>
<rect x="32" y="32" width="56" height="56" rx="14" fill="{C['bg']}" stroke="url(#tile)" stroke-width="1.5"/>
<g transform="translate(44 44) scale(1.333)" fill="none" stroke="url(#tile)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{lucide(p['icon'])}</g>
<text x="106" y="58" class="n">{esc(p['name'])}</text>
<text x="107" y="84" class="s" fill="{C['muted']}">{esc(owner)}</text>
<g transform="translate({W - 32 - sw:.0f} 34)">
  <rect width="{sw:.0f}" height="32" rx="16" fill="{C['ok']}" fill-opacity=".08" stroke="{C['ok']}" stroke-opacity=".35"/>
  <circle cx="18" cy="16" r="4.5" fill="{C['ok']}"/>
  <text x="31" y="22" class="s" fill="{C['ok']}">{esc(status)}</text>
</g>
<text x="32" y="140" class="d">{esc(desc[0])}</text>
<text x="32" y="170" class="d">{esc(desc[1])}</text>
{''.join(chips)}"""
    write(f"card-{p['slug']}-{lang}.svg", svg(W, H, f"{p['name']}: {p[lang].replace(chr(10), ' ')}", body, style))


# ---------------------------------------------------------------- stack
def stack():
    n = len(STACK)
    tile, gap, pad = 64, 12, 0
    W = n * tile + (n - 1) * gap
    H = tile
    items = []
    for i, name in enumerate(STACK):
        x = i * (tile + gap)
        items.append(f'<g transform="translate({x} 0)"><rect x=".75" y=".75" width="{tile - 1.5}" height="{tile - 1.5}" rx="16" '
                     f'fill="{C["panel"]}" stroke="{C["line"]}" stroke-width="1.5"/>'
                     f'<path transform="translate(18 18) scale(1.1667)" d="{simple(name)}" fill="{C["soft"]}"/></g>')
    label = "Stack: " + ", ".join(STACK)
    write("stack.svg", svg(W, H, label, "".join(items)))


# ---------------------------------------------------------------- contato
def button(icon, label):
    W, H = 220, 56
    style = fonts(sans=label) + f".l{{font-family:G,sans-serif;font-size:19px;fill:{C['text']}}}"
    body = f"""<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="14" fill="{C['panel']}" stroke="{C['line']}" stroke-width="1.5"/>
<g transform="translate(26 16)" fill="none" stroke="{C['accent']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{lucide(icon)}</g>
<text x="64" y="35" class="l">{label}</text>"""
    write(f"btn-{icon}.svg", svg(W, H, label, body, style))


def lang_pill(code, label, hint):
    W, H = 300, 56
    style = fonts(sans_bold=label, sans=hint, mono=code) + f"""
.l{{font-family:GB,sans-serif;font-size:20px;fill:{C['text']}}}
.h{{font-family:G,sans-serif;font-size:15px;fill:{C['muted']}}}
.c{{font-family:GM,monospace;font-size:15px;fill:{C['accent']}}}"""
    body = f"""<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="14" fill="{C['panel']}" stroke="{C['line']}" stroke-width="1.5"/>
<rect x="12" y="12" width="44" height="32" rx="8" fill="{C['bg']}" stroke="{C['accent']}" stroke-opacity=".5"/>
<text x="34" y="33" class="c" text-anchor="middle">{code}</text>
<text x="70" y="27" class="l">{label}</text>
<text x="70" y="45" class="h">{hint}</text>"""
    write(f"lang-{code.lower()}.svg", svg(W, H, label, body, style))


if __name__ == "__main__":
    lang_pill("PT", "Português", "Clique para abrir ou fechar")
    lang_pill("EN", "English", "Click to expand or collapse")
    hero()
    for p in PROJECTS:
        for lang in L10N:
            card(p, lang)
    stack()
    for icon, label in CONTACT:
        button(icon, label)
