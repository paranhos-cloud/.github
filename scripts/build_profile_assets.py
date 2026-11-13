"""Generates the animated SVGs for the paranhos-cloud organization profile README.

Fonts and the logo are embedded as data URIs (subset to the characters each SVG uses), because
an SVG shown through <img> cannot load anything external.

Usage: pip install fonttools brotli pillow
       BRAND_DIR=<path to paranhos-cloud-socialmedia> python scripts/build_profile_assets.py
"""

import base64
import os
import io
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

from fontTools.subset import Options, Subsetter  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from PIL import Image  # noqa: E402

BRAND = Path(os.environ.get("BRAND_DIR", HERE.parent / "socialmedia"))
FONTS = {
    "Manrope": BRAND / "styles/fonts/manrope-latin-wght-normal.woff2",
    "JetBrains Mono": BRAND / "styles/fonts/jetbrains-mono-latin-wght-normal.woff2",
}
OUT = HERE / "profile/assets"
OUT.mkdir(parents=True, exist_ok=True)

THEMES = {
    "dark": dict(
        bg="#0b0d10", surface="#101216", line="rgba(255,255,255,0.08)", line_strong="rgba(255,255,255,0.14)",
        fg="#eef0f3", muted="#a3a9b4", subtle="#737a86", brand="#7cb6ff", ok="#4ade9a", node_ring="#7cb6ff",
    ),
    "light": dict(
        bg="#ffffff", surface="#f6f8fa", line="#e6e9ee", line_strong="#d0d7de",
        fg="#0b0d10", muted="#4b5563", subtle="#6b7280", brand="#004afd", ok="#16a34a", node_ring="#004afd",
    ),
}
DARK = THEMES["dark"]

# ---------------------------------------------------------------- text measuring

_fonts = {name: TTFont(path) for name, path in FONTS.items()}


def measure(text: str, size: float, family: str = "Manrope", spacing: float = 0.0, weight_fudge: float = 1.0) -> float:
    font = _fonts[family]
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    upm = font["head"].unitsPerEm
    width = 0
    for ch in text:
        glyph = cmap.get(ord(ch))
        width += hmtx[glyph][0] if glyph else upm * 0.5
    return width / upm * size * weight_fudge + spacing * max(len(text) - 1, 0)


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- embedding

def font_face(family: str, chars: str) -> str:
    font = TTFont(FONTS[family])
    options = Options()
    options.flavor = "woff2"
    options.layout_features = ["*"]
    subsetter = Subsetter(options)
    subsetter.populate(text=chars + " ")
    subsetter.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    return (
        f"@font-face{{font-family:'{family}';font-weight:200 800;"
        f"src:url(data:font/woff2;base64,{data}) format('woff2');}}"
    )


def png_data(path: Path, height: int) -> tuple[str, float]:
    image = Image.open(path).convert("RGBA")
    ratio = image.width / image.height
    image = image.resize((round(height * ratio), height), Image.LANCZOS)
    buf = io.BytesIO()
    image.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), ratio


def texts_in(body: str) -> str:
    return "".join(re.findall(r">([^<>]+)<", body)).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def svg(width: int, height: int, body: str, css: str, label: str, families=("Manrope", "JetBrains Mono")) -> str:
    chars = "".join(sorted(set(texts_in(body))))
    faces = "".join(font_face(f, chars) for f in families)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}">'
        f"<title>{esc(label)}</title>"
        f"<style>{faces}"
        ".sans{font-family:'Manrope',system-ui,sans-serif}.mono{font-family:'JetBrains Mono',ui-monospace,monospace}"
        f"{css}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
        f"</style>{body}</svg>"
    )


def keyframes(name: str, total: float, stops: list[tuple[float, str]]) -> str:
    """Keyframes from (seconds, declarations) pairs inside a cycle of `total` seconds."""
    parts = []
    for seconds, decl in stops:
        pct = max(0.0, min(100.0, seconds / total * 100))
        parts.append(f"{pct:.2f}%{{{decl}}}")
    return f"@keyframes {name}{{{''.join(parts)}}}"


def write(name: str, content: str) -> None:
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"{name}: {len(content.encode()) / 1024:.1f} KB")


# ---------------------------------------------------------------- shared pieces

CHECK = "M-4 0.2 L-1.2 3 L4.2 -2.6"
LOCK = (
    '<rect x="-5" y="-1" width="10" height="8" rx="2" fill="none" stroke="{c}" stroke-width="1.5"/>'
    '<path d="M-3 -1 V-3.5 a3 3 0 0 1 6 0 V-1" fill="none" stroke="{c}" stroke-width="1.5"/>'
)
REPO_ICON = (
    "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"
)


def wave_defs(uid: str, width: int, height: int, crest_y: float) -> str:
    """The brand's blue wave rising from the bottom, as blurred shapes."""
    return f"""
<linearGradient id="{uid}-sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#020309"/><stop offset=".45" stop-color="#040817"/>
  <stop offset=".8" stop-color="#06123a"/><stop offset="1" stop-color="#0a2272"/>
</linearGradient>
<linearGradient id="{uid}-wave" x1="0" y1="0" x2="1" y2="0">
  <stop offset=".1" stop-color="#0019dd"/><stop offset=".5" stop-color="#004afd"/><stop offset=".9" stop-color="#009cfd"/>
</linearGradient>
<filter id="{uid}-blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{height * 0.09:.0f}"/></filter>
<filter id="{uid}-soft" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="{uid}-grain"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>
  <feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .05 0"/></filter>
<pattern id="{uid}-grid" width="48" height="48" patternUnits="userSpaceOnUse">
  <path d="M48 0H0V48" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
</pattern>
<radialGradient id="{uid}-gridfade" cx=".7" cy=".25" r=".7">
  <stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</radialGradient>
<mask id="{uid}-gridmask"><rect width="{width}" height="{height}" fill="url(#{uid}-gridfade)"/></mask>
<clipPath id="{uid}-clip"><rect width="{width}" height="{height}" rx="20"/></clipPath>
"""


def wave_layers(uid: str, width: int, height: int, crest_y: float) -> str:
    cx = width / 2
    return f"""
<rect width="{width}" height="{height}" fill="url(#{uid}-sky)"/>
<rect width="{width}" height="{height}" fill="url(#{uid}-grid)" mask="url(#{uid}-gridmask)"/>
<g transform="rotate(-6 {cx} {crest_y})">
  <ellipse cx="{cx}" cy="{crest_y + height * 0.32}" rx="{width * 0.8}" ry="{height * 0.36}" fill="url(#{uid}-wave)" opacity=".8" filter="url(#{uid}-blur)"/>
  <ellipse cx="{cx + width * 0.05}" cy="{crest_y + height * 0.36}" rx="{width * 0.66}" ry="{height * 0.34}" fill="none" stroke="rgba(124,182,255,0.5)" stroke-width="3" filter="url(#{uid}-soft)"/>
</g>
<rect width="{width}" height="{height}" filter="url(#{uid}-grain)" opacity=".6"/>
"""


# ---------------------------------------------------------------- hero

def hero() -> str:
    W, H = 1280, 480
    T = 10.0
    logo, ratio = png_data(BRAND / "brand/logo-white.png", 68)
    logo_h = 32

    steps = [
        ("Projeto detectado", "0.3s", None),
        ("Next.js", "0.1s", "framework"),
        ("Dependências instaladas", "6.8s", None),
        ("Build concluído", "14.2s", None),
        ("SSL configurado", "0.9s", None),
        ("Deploy concluído", "1.6s", None),
    ]
    step_gap = 0.42
    first = 0.5
    done_at = first + step_gap * len(steps) + 0.3
    fade = (T - 0.7, T - 0.25)

    css = [
        ".fg{fill:%s}.muted{fill:%s}.subtle{fill:%s}.brand{fill:%s}.ok{fill:%s}"
        % (DARK["fg"], DARK["muted"], DARK["subtle"], DARK["brand"], DARK["ok"]),
        ".anim{animation-duration:%ss;animation-iteration-count:infinite;animation-timing-function:cubic-bezier(.22,1,.36,1)}" % T,
        ".pop{transform-box:fill-box;transform-origin:center}",
    ]

    card_x, card_y, card_w, card_h = 716, 56, 500, 368
    inner_l, inner_r = card_x + 20, card_x + card_w - 20
    rows = []
    for i, (label, time, tag) in enumerate(steps):
        y = card_y + 82 + i * 34
        a = first + i * step_gap
        css.append(keyframes(f"s{i}", T, [
            (0, "opacity:0;transform:translateX(-6px)"), (a, "opacity:0;transform:translateX(-6px)"),
            (a + 0.35, "opacity:1;transform:translateX(0)"), (fade[0], "opacity:1;transform:translateX(0)"),
            (fade[1], "opacity:0;transform:translateX(0)"), (T, "opacity:0;transform:translateX(-6px)"),
        ]))
        css.append(keyframes(f"c{i}", T, [
            (0, "opacity:0;transform:scale(.4)"), (a + 0.2, "opacity:0;transform:scale(.4)"),
            (a + 0.38, "opacity:1;transform:scale(1.15)"), (a + 0.5, "opacity:1;transform:scale(1)"),
            (fade[0], "opacity:1;transform:scale(1)"), (fade[1], "opacity:0;transform:scale(1)"),
            (T, "opacity:0;transform:scale(.4)"),
        ]))
        tag_svg = ""
        if tag:
            tx = inner_l + 32 + measure(label, 15, weight_fudge=1.06) + 10
            tw = measure(tag, 11, "JetBrains Mono") + 14
            tag_svg = (
                f'<rect x="{tx:.1f}" y="{y - 13}" width="{tw:.1f}" height="19" rx="9.5" fill="rgba(124,182,255,0.1)" stroke="rgba(124,182,255,0.25)"/>'
                f'<text x="{tx + 7:.1f}" y="{y}" class="mono brand" font-size="11">{tag}</text>'
            )
        rows.append(
            f'<g class="anim" style="animation-name:s{i}">'
            f'<g class="anim pop" style="animation-name:c{i}"><circle cx="{inner_l + 10}" cy="{y - 4.5}" r="10" fill="rgba(74,222,154,0.14)"/>'
            f'<path d="{CHECK}" transform="translate({inner_l + 10} {y - 4.5})" fill="none" stroke="{DARK["ok"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g>'
            f'<text x="{inner_l + 32}" y="{y}" class="sans fg" font-size="15" font-weight="600">{esc(label)}</text>{tag_svg}'
            f'<text x="{inner_r}" y="{y}" text-anchor="end" class="mono subtle" font-size="13">{time}</text></g>'
        )

    bar_y = card_y + 296
    css.append(keyframes("bar", T, [
        (0, "transform:scaleX(0)"), (0.4, "transform:scaleX(0)"), (done_at, "transform:scaleX(1)"),
        (fade[0], "transform:scaleX(1);opacity:1"), (fade[1], "transform:scaleX(1);opacity:0"), (T, "transform:scaleX(0);opacity:0"),
    ]))
    css.append(".bar{transform-box:fill-box;transform-origin:left center;animation-timing-function:cubic-bezier(.45,0,.55,1)!important}")
    css.append(keyframes("building", T, [
        (0, "opacity:1"), (done_at, "opacity:1"), (done_at + 0.2, "opacity:0"), (fade[1], "opacity:0"), (T, "opacity:1"),
    ]))
    css.append(keyframes("online", T, [
        (0, "opacity:0"), (done_at, "opacity:0"), (done_at + 0.2, "opacity:1"), (fade[0], "opacity:1"), (fade[1], "opacity:0"), (T, "opacity:0"),
    ]))
    css.append(keyframes("result", T, [
        (0, "opacity:0;transform:translateY(8px)"), (done_at + 0.1, "opacity:0;transform:translateY(8px)"),
        (done_at + 0.7, "opacity:1;transform:translateY(0)"), (fade[0], "opacity:1;transform:translateY(0)"),
        (fade[1], "opacity:0;transform:translateY(0)"), (T, "opacity:0;transform:translateY(8px)"),
    ]))
    css.append(keyframes("blink", 1.2, [(0, "opacity:1"), (0.6, "opacity:.25"), (1.2, "opacity:1")]))

    header_y = card_y + 30
    res_y = card_y + 308
    status = (
        f'<g class="anim" style="animation-name:building;opacity:0">'
        f'<circle cx="{inner_r - 72}" cy="{header_y - 4}" r="4" fill="#fbbf24" style="animation:blink 1.2s infinite"/>'
        f'<text x="{inner_r}" y="{header_y}" text-anchor="end" class="mono" fill="#fbbf24" font-size="12">Building</text></g>'
        f'<g class="anim" style="animation-name:online">'
        f'<circle cx="{inner_r - 58}" cy="{header_y - 4}" r="4" class="ok"/>'
        f'<text x="{inner_r}" y="{header_y}" text-anchor="end" class="mono ok" font-size="12">Online</text></g>'
    )

    title_size = 60
    lead = [
        "Hospede sites e aplicações sem configurar infraestrutura.",
        "Conecte o GitHub e a Paranhos Cloud cuida do resto.",
    ]
    pill_text = "Cloud simples para aplicações modernas"
    pill_w = measure(pill_text, 13, weight_fudge=1.05) + 46
    stack = "HTML  ·  React  ·  Vue  ·  Angular  ·  Next.js estático"

    body = f"""
<defs>{wave_defs("h", W, H, 400)}
<linearGradient id="h-bar" x1="0" x2="1"><stop offset="0" stop-color="#004afd"/><stop offset="1" stop-color="#009cfd"/></linearGradient>
<filter id="h-shadow" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="24" stdDeviation="28" flood-color="#000" flood-opacity=".6"/></filter>
</defs>
<g clip-path="url(#h-clip)">
{wave_layers("h", W, H, 400)}

<image x="64" y="52" width="{logo_h * ratio:.1f}" height="{logo_h}" href="{logo}" xlink:href="{logo}"/>

<rect x="64" y="122" width="{pill_w:.1f}" height="30" rx="15" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.14)"/>
<circle cx="83" cy="137" r="3.5" class="brand"/>
<text x="97" y="141.5" class="sans muted" font-size="13" font-weight="500">{esc(pill_text)}</text>

<text x="62" y="{218}" class="sans fg" font-size="{title_size}" font-weight="700" letter-spacing="-2.6">Seu projeto.</text>
<text x="62" y="{218 + 68}" class="sans muted" font-size="{title_size}" font-weight="700" letter-spacing="-2.6">Online em minutos.</text>

<text x="64" y="338" class="sans muted" font-size="17" font-weight="500">{esc(lead[0])}</text>
<text x="64" y="364" class="sans muted" font-size="17" font-weight="500">{esc(lead[1])}</text>

<text x="64" y="420" class="mono" fill="rgba(238,240,243,0.75)" font-size="12.5" xml:space="preserve">{esc(stack)}</text>

<g filter="url(#h-shadow)"><rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="16" fill="rgba(11,13,16,0.86)" stroke="rgba(255,255,255,0.14)"/></g>
<circle cx="{inner_l + 4}" cy="{header_y - 4}" r="5" fill="#1d2127"/><circle cx="{inner_l + 20}" cy="{header_y - 4}" r="5" fill="#1d2127"/><circle cx="{inner_l + 36}" cy="{header_y - 4}" r="5" fill="#1d2127"/>
<text x="{inner_l + 58}" y="{header_y}" class="mono muted" font-size="12.5">meu-projeto  ·  main</text>
{status}
<line x1="{card_x}" x2="{card_x + card_w}" y1="{card_y + 50}" y2="{card_y + 50}" stroke="rgba(255,255,255,0.08)"/>
{''.join(rows)}
<rect x="{inner_l}" y="{bar_y - 22}" width="{inner_r - inner_l}" height="4" rx="2" fill="rgba(255,255,255,0.08)"/>
<rect class="anim bar" style="animation-name:bar" x="{inner_l}" y="{bar_y - 22}" width="{inner_r - inner_l}" height="4" rx="2" fill="url(#h-bar)"/>
<g class="anim" style="animation-name:result">
  <rect x="{inner_l}" y="{res_y - 10}" width="{inner_r - inner_l}" height="40" rx="10" fill="rgba(74,222,154,0.07)" stroke="rgba(74,222,154,0.28)"/>
  <g transform="translate({inner_l + 20} {res_y + 8})">{LOCK.format(c=DARK["ok"])}</g>
  <text x="{inner_l + 38}" y="{res_y + 15}" class="mono fg" font-size="13.5">meu-projeto.paranhos.cloud</text>
  <circle cx="{inner_r - 66}" cy="{res_y + 10}" r="4" class="ok"/>
  <text x="{inner_r - 16}" y="{res_y + 15}" text-anchor="end" class="sans ok" font-size="13" font-weight="700">Online</text>
</g>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="rgba(255,255,255,0.08)"/>
"""
    return svg(W, H, body, "".join(css), "Paranhos Cloud — Seu projeto. Online em minutos.")


# ---------------------------------------------------------------- how it works

def how(theme: str) -> str:
    t = THEMES[theme]
    W, H = 1280, 300
    T = 6.0
    xs = [200, 640, 1080]
    y = 186
    steps = [
        ("Conecte o repositório", "Um pull request adiciona o workflow"),
        ("Build no seu GitHub Actions", "Autenticado por OIDC, sem segredos"),
        ("No ar, com HTTPS", "Subdomínio ou domínio próprio"),
    ]
    travel = (0.4, 3.4)
    arrive = [travel[0] + (travel[1] - travel[0]) * (x - xs[0]) / (xs[-1] - xs[0]) for x in xs]
    length = xs[-1] - xs[0]

    css = [
        f".fg{{fill:{t['fg']}}}.muted{{fill:{t['muted']}}}.brand{{fill:{t['brand']}}}",
        ".anim{animation-duration:%ss;animation-iteration-count:infinite}" % T,
        ".ring{transform-box:fill-box;transform-origin:center}",
        keyframes("progress", T, [
            (0, f"stroke-dashoffset:{length};opacity:1"), (travel[0], f"stroke-dashoffset:{length};opacity:1"),
            (travel[1], "stroke-dashoffset:0;opacity:1"), (T - 0.6, "stroke-dashoffset:0;opacity:1"),
            (T - 0.1, "stroke-dashoffset:0;opacity:0"), (T, f"stroke-dashoffset:{length};opacity:0"),
        ]),
        keyframes("pulse", T, [
            (0, f"transform:translateX(0);opacity:0"), (travel[0] - 0.1, "transform:translateX(0);opacity:0"),
            (travel[0], "transform:translateX(0);opacity:1"), (travel[1], f"transform:translateX({length}px);opacity:1"),
            (travel[1] + 0.3, f"transform:translateX({length}px);opacity:0"), (T, f"transform:translateX({length}px);opacity:0"),
        ]),
        ".linear{animation-timing-function:cubic-bezier(.45,0,.55,1)}",
    ]
    nodes = []
    for i, (x, (title, desc)) in enumerate(zip(xs, steps)):
        a = arrive[i]
        css.append(keyframes(f"r{i}", T, [
            (0, "opacity:0;transform:scale(1)"), (a, "opacity:0;transform:scale(1)"),
            (a + 0.05, "opacity:.9;transform:scale(1)"), (a + 1.0, "opacity:0;transform:scale(1.9)"), (T, "opacity:0;transform:scale(1.9)"),
        ]))
        nodes.append(f"""
<circle class="anim ring" style="animation-name:r{i};opacity:0" cx="{x}" cy="{y}" r="26" fill="none" stroke="{t['node_ring']}" stroke-width="2"/>
<circle cx="{x}" cy="{y}" r="34" fill="{t['surface']}"/>
<circle cx="{x}" cy="{y}" r="26" fill="url(#w-grad)"/>
<text x="{x}" y="{y + 6}" text-anchor="middle" class="mono" fill="#fff" font-size="17" font-weight="700">{i + 1}</text>
<text x="{x}" y="{y + 64}" text-anchor="middle" class="sans fg" font-size="18" font-weight="700">{esc(title)}</text>
<text x="{x}" y="{y + 88}" text-anchor="middle" class="sans muted" font-size="14" font-weight="500">{esc(desc)}</text>""")

    body = f"""
<defs>
<linearGradient id="w-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0019dd"/><stop offset=".45" stop-color="#004afd"/><stop offset="1" stop-color="#009cfd"/></linearGradient>
<linearGradient id="w-line" gradientUnits="userSpaceOnUse" x1="{xs[0]}" x2="{xs[-1]}" y1="0" y2="0"><stop offset="0" stop-color="#004afd"/><stop offset="1" stop-color="#009cfd"/></linearGradient>
<radialGradient id="w-glow"><stop offset="0" stop-color="#9cd2ff"/><stop offset=".35" stop-color="#009cfd" stop-opacity=".9"/><stop offset="1" stop-color="#009cfd" stop-opacity="0"/></radialGradient>
</defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="{t['surface']}" stroke="{t['line_strong']}"/>
<text x="64" y="64" class="mono brand" font-size="13" font-weight="600" letter-spacing="2.6">COMO FUNCIONA</text>
<text x="64" y="102" class="sans fg" font-size="28" font-weight="800" letter-spacing="-0.8">Do push ao ar, sem servidor para cuidar.</text>
<line x1="{xs[0]}" x2="{xs[-1]}" y1="{y}" y2="{y}" stroke="{t['subtle']}" stroke-opacity=".55" stroke-width="3" stroke-dasharray="0.1 9" stroke-linecap="round"/>
<line class="anim linear" style="animation-name:progress" x1="{xs[0]}" x2="{xs[-1]}" y1="{y}" y2="{y}" stroke="url(#w-line)" stroke-width="3" stroke-dasharray="{length}" stroke-dashoffset="0"/>
{''.join(nodes)}
<circle class="anim linear" style="animation-name:pulse;opacity:0" cx="{xs[0]}" cy="{y}" r="14" fill="url(#w-glow)"/>
"""
    return svg(W, H, body, "".join(css), "Como funciona: conecte o repositório, o build roda no seu GitHub Actions e o site fica no ar com HTTPS.")


# ---------------------------------------------------------------- repo cards

REPOS = [
    ("deploy-action", ["Action que faz o build no seu GitHub", "e publica o site na Paranhos Cloud."], "Shell", "#89e051"),
    ("docs", ["Código-fonte de docs.paranhos.cloud,", "feito com Next.js e Fumadocs."], "MDX", "#fcb32c"),
]


def card(theme: str, name: str, desc: list[str], lang: str, color: str) -> str:
    t = THEMES[theme]
    W, H = 400, 140
    badge = "Público"
    bw = measure(badge, 11, weight_fudge=1.05) + 18
    css = f".fg{{fill:{t['fg']}}}.muted{{fill:{t['muted']}}}.subtle{{fill:{t['subtle']}}}.brand{{fill:{t['brand']}}}"
    body = f"""
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="{t['surface']}" stroke="{t['line_strong']}"/>
<path d="{REPO_ICON}" transform="translate(22 22)" fill="{t['subtle']}"/>
<text x="46" y="35" class="sans brand" font-size="16" font-weight="700">{esc(name)}</text>
<rect x="{W - 22 - bw:.1f}" y="21" width="{bw:.1f}" height="20" rx="10" fill="none" stroke="{t['line_strong']}"/>
<text x="{W - 22 - bw / 2:.1f}" y="35" text-anchor="middle" class="sans subtle" font-size="11" font-weight="600">{badge}</text>
<text x="22" y="70" class="sans muted" font-size="14" font-weight="500">{esc(desc[0])}</text>
<text x="22" y="91" class="sans muted" font-size="14" font-weight="500">{esc(desc[1])}</text>
<circle cx="28" cy="117" r="6" fill="{color}"/>
<text x="42" y="121.5" class="mono subtle" font-size="12">{esc(lang)}</text>
"""
    return svg(W, H, body, css, f"{name}: {' '.join(desc)}")


# ---------------------------------------------------------------- buttons

def button(theme: str | None, label: str, primary: bool = False) -> str:
    t = THEMES[theme or "dark"]
    size = 15
    arrow = "  →" if primary else ""
    W = round(measure(label + arrow, size, weight_fudge=1.08) + 48)
    H = 46
    if primary:
        bg = '<rect width="{0}" height="{1}" rx="12" fill="url(#b-grad)"/>'.format(W, H)
        fill = "#fff"
        defs = '<defs><linearGradient id="b-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0019dd"/><stop offset=".5" stop-color="#004afd"/><stop offset="1" stop-color="#009cfd"/></linearGradient></defs>'
    else:
        bg = f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{t["surface"]}" stroke="{t["line_strong"]}"/>'
        fill = t["fg"]
        defs = ""
    body = f'{defs}{bg}<text x="{W / 2}" y="{H / 2 + 5.5}" text-anchor="middle" class="sans" fill="{fill}" font-size="{size}" font-weight="700" xml:space="preserve">{esc(label + arrow)}</text>'
    return svg(W, H, body, "", label, families=("Manrope",))


# ---------------------------------------------------------------- footer

def footer() -> str:
    W, H = 1280, 150
    mark, ratio = png_data(BRAND / "brand/logo-white.png", 52)
    lh = 24
    body = f"""
<defs>{wave_defs("f", W, H, 120)}</defs>
<g clip-path="url(#f-clip)">{wave_layers("f", W, H, 120)}
<image x="{(W - lh * ratio) / 2:.1f}" y="40" width="{lh * ratio:.1f}" height="{lh}" href="{mark}" xlink:href="{mark}"/>
<text x="{W / 2}" y="100" text-anchor="middle" class="mono" fill="rgba(238,240,243,0.8)" font-size="12.5" letter-spacing="1.5" xml:space="preserve">FEITO NO BRASIL  ·  PARANHOS.CLOUD</text>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="rgba(255,255,255,0.08)"/>
"""
    return svg(W, H, body, "", "Paranhos Cloud — feito no Brasil", families=("JetBrains Mono",))


if __name__ == "__main__":
    write("hero.svg", hero())
    write("footer.svg", footer())
    for theme in THEMES:
        write(f"how-{theme}.svg", how(theme))
        for name, desc, lang, color in REPOS:
            write(f"repo-{name}-{theme}.svg", card(theme, name, desc, lang, color))
        write(f"btn-docs-{theme}.svg", button(theme, "Documentação"))
        write(f"btn-site-{theme}.svg", button(theme, "Site"))
        write(f"btn-status-{theme}.svg", button(theme, "Status"))
    write("btn-start.svg", button(None, "Começar grátis", primary=True))
