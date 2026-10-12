#!/usr/bin/env python3
"""
generate_assets.py - builds the three minimal, corporate-style SVGs used in the README.
Run from the repo root:  python scripts/generate_assets.py
Edit the CONFIG block, re-run, commit the files in /assets.
"""
import html
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)

# =====================================================================
# CONFIG - edit this section only
# =====================================================================
NAME = "Sonu Sinha"
TITLE = "Data Analyst"
DOMAIN = "Sales  \u00b7  Supply Chain  \u00b7  Operations Analytics"
PITCH_1 = "I turn raw operational data into decisions:"
PITCH_2 = "clean data, clear dashboards, actionable insight."
CHIPS = ["SQL", "Power BI", "Excel", "Python", "DAX"]

# "At a glance" tiles: (LABEL, headline, sub-line). Keep them TRUE.
GLANCE = [
    ("FOCUS", "Sales & Supply Chain", "Operations analytics"),
    ("CORE STACK", "SQL \u00b7 Power BI", "Excel \u00b7 Python \u00b7 DAX"),
    ("PORTFOLIO", "3 projects", "1 in progress"),
    ("STATUS", "Open to roles", "Data Analyst"),
]

# Your analysis workflow: (step title, tools / description)
WORKFLOW = [
    ("Ask", "Define the question"),
    ("Acquire", "SQL, Excel, exports"),
    ("Clean", "Power Query, Pandas"),
    ("Analyze", "EDA, statistics"),
    ("Visualize", "Power BI, charts"),
    ("Recommend", "Insight and action"),
]

# =====================================================================
# Design tokens
# =====================================================================
BG, BG2, LINE = "#0f172a", "#111c36", "#233149"
TXT, MUTED, ACC, ACC2 = "#f1f5f9", "#94a3b8", "#38bdf8", "#2dd4bf"
UI = "'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Courier New', monospace"


def esc(t):
    return html.escape(str(t), quote=True)


def svg(w, h, body, defs="", title=""):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">\n'
            f'<title>{esc(title)}</title>\n<defs>{defs}</defs>\n{body}\n</svg>\n')


def anim(attr, pts, dur, begin=0.0):
    """Looping animation. pts = [(seconds, value)], times must be increasing."""
    pts = [(float(t), v) for t, v in pts]
    if pts[0][0] > 0:
        pts.insert(0, (0.0, pts[0][1]))
    if pts[-1][0] < dur:
        pts.append((float(dur), pts[-1][1]))
    kt = ";".join(f"{t / dur:.5f}" for t, _ in pts)
    vals = ";".join(str(v) for _, v in pts)
    b = f' begin="-{begin}s"' if begin else ""
    return (f'<animate attributeName="{attr}" values="{vals}" keyTimes="{kt}" dur="{dur}s" '
            f'repeatCount="indefinite"{b}/>')


# =====================================================================
# 1. BANNER: identity + a trend line that draws itself
# =====================================================================
def banner():
    W, H, D = 900, 240, 10.0
    actual = [.30, .38, .34, .46, .52, .49, .60, .66, .62, .74, .80, .88]
    target = [.36 + i * 0.045 for i in range(12)]
    x0, x1, yb, yh = 540, 860, 196, 136
    X = lambda i: x0 + (x1 - x0) * i / 11
    Y = lambda v: yb - v * yh
    line = "M" + " L".join(f"{X(i):.1f} {Y(v):.1f}" for i, v in enumerate(actual))
    area = line + f" L{x1} {yb} L{x0} {yb} Z"
    tline = "M" + " L".join(f"{X(i):.1f} {Y(v):.1f}" for i, v in enumerate(target))
    defs = (f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG}"/>'
            f'<stop offset="1" stop-color="{BG2}"/></linearGradient>'
            f'<linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ACC}" stop-opacity=".30"/>'
            f'<stop offset="1" stop-color="{ACC}" stop-opacity="0"/></linearGradient>')
    b = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="url(#bg)" stroke="{LINE}" stroke-width="2"/>']
    for k in range(5):
        y = yb - k * yh / 4
        b.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{LINE}" stroke-width="1"/>')
    for i, m in enumerate("JFMAMJJASOND"):
        if i % 2 == 0:
            b.append(f'<text x="{X(i):.1f}" y="{yb + 18}" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{MUTED}">{m}</text>')
    b.append(f'<text x="{x0}" y="46" font-family="{MONO}" font-size="11" letter-spacing="1.5" fill="{MUTED}">PERFORMANCE TREND</text>')
    b.append(f'<line x1="{x0 + 190}" y1="42" x2="{x0 + 210}" y2="42" stroke="{ACC}" stroke-width="3"/>'
             f'<text x="{x0 + 216}" y="46" font-family="{MONO}" font-size="10" fill="{MUTED}">Actual</text>'
             f'<line x1="{x0 + 262}" y1="42" x2="{x0 + 282}" y2="42" stroke="{ACC2}" stroke-width="2" stroke-dasharray="4 3"/>'
             f'<text x="{x0 + 288}" y="46" font-family="{MONO}" font-size="10" fill="{MUTED}">Target</text>')
    b.append(f'<g>{anim("opacity", [(0, 0), (.4, 1), (D - 1.0, 1), (D, 0)], D)}'
             f'<path d="{tline}" fill="none" stroke="{ACC2}" stroke-width="2" stroke-dasharray="4 4" opacity=".8"/>'
             f'<path d="{area}" fill="url(#ar)" opacity="0">{anim("opacity", [(0, 0), (1.6, 0), (3.2, 1), (D - 1.0, 1)], D)}</path>'
             f'<path d="{line}" pathLength="100" fill="none" stroke="{ACC}" stroke-width="3.5" stroke-linecap="round" '
             f'stroke-linejoin="round" stroke-dasharray="100" stroke-dashoffset="100">'
             f'{anim("stroke-dashoffset", [(0, 100), (.5, 100), (3.0, 0)], D)}</path>'
             f'<circle cx="{X(11):.1f}" cy="{Y(actual[-1]):.1f}" r="5" fill="{ACC}" opacity="0">{anim("opacity", [(0, 0), (3.0, 0), (3.2, 1)], D)}</circle>'
             f'<circle cx="{X(11):.1f}" cy="{Y(actual[-1]):.1f}" r="5" fill="none" stroke="{ACC}" stroke-width="2" opacity="0">'
             f'{anim("r", [(0, 5), (3.2, 5), (4.4, 16), (4.41, 5)], D)}{anim("opacity", [(0, 0), (3.2, .8), (4.4, 0)], D)}</circle></g>')
    b.append(f'<text x="44" y="82" font-family="{UI}" font-size="40" font-weight="700" fill="{TXT}">{esc(NAME)}</text>'
             f'<text x="44" y="114" font-family="{UI}" font-size="20" font-weight="600" fill="{ACC}">{esc(TITLE)}</text>'
             f'<text x="44" y="140" font-family="{UI}" font-size="14" fill="{MUTED}" xml:space="preserve">{esc(DOMAIN)}</text>'
             f'<text x="44" y="172" font-family="{UI}" font-size="13" fill="{MUTED}">{esc(PITCH_1)}</text>'
             f'<text x="44" y="190" font-family="{UI}" font-size="13" fill="{MUTED}">{esc(PITCH_2)}</text>')
    x = 44
    for c in CHIPS:
        w = 16 + len(c) * 7.6
        b.append(f'<rect x="{x:.0f}" y="206" width="{w:.0f}" height="22" rx="11" fill="none" stroke="{LINE}" stroke-width="1.5"/>'
                 f'<text x="{x + w / 2:.0f}" y="221" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{TXT}">{esc(c)}</text>')
        x += w + 8
    return svg(W, H, "\n".join(b), defs, f"{NAME} - {TITLE}")


# =====================================================================
# 2. AT A GLANCE tiles
# =====================================================================
def glance():
    W, H = 900, 112
    cols = [ACC, ACC2, "#a78bfa", "#fbbf24"]
    b = []
    tw, gap = 203, 27
    for i, (lab, head, sub) in enumerate(GLANCE):
        x = 2 + i * (tw + gap)
        b.append(f'<g opacity="0">{anim("opacity", [(0, 0), (.2 + i * .15, 0), (.6 + i * .15, 1)], 8.0)}'
                 f'<rect x="{x}" y="4" width="{tw}" height="104" rx="10" fill="{BG}" stroke="{LINE}" stroke-width="2"/>'
                 f'<rect x="{x}" y="4" width="{tw}" height="4" rx="2" fill="{cols[i]}"/>'
                 f'<text x="{x + 18}" y="34" font-family="{MONO}" font-size="10.5" letter-spacing="1.5" fill="{MUTED}">{esc(lab)}</text>'
                 f'<text x="{x + 18}" y="64" font-family="{UI}" font-size="18" font-weight="700" fill="{TXT}">{esc(head)}</text>'
                 f'<text x="{x + 18}" y="86" font-family="{UI}" font-size="13" fill="{MUTED}">{esc(sub)}</text></g>')
    return svg(W, H, "\n".join(b), "", "At a glance")


# =====================================================================
# 3. WORKFLOW strip with a soft moving highlight
# =====================================================================
def workflow():
    W, H, D = 900, 120, 9.0
    n = len(WORKFLOW)
    bw = 132
    gap = (872 - bw * n) / (n - 1)
    b = []
    for i, (t, d) in enumerate(WORKFLOW):
        x = 14 + i * (bw + gap)
        s = 0.4 + i * 1.1
        b.append(f'<rect x="{x:.0f}" y="18" width="{bw}" height="84" rx="10" fill="{BG}" stroke="{LINE}" stroke-width="2"/>'
                 f'<rect x="{x:.0f}" y="18" width="{bw}" height="84" rx="10" fill="none" stroke="{ACC}" stroke-width="2.5" opacity="0">'
                 f'{anim("opacity", [(0, 0), (s, 0), (s + .4, 1), (s + 1.4, 1), (s + 1.8, 0)], D)}</rect>'
                 f'<text x="{x + 16:.0f}" y="44" font-family="{MONO}" font-size="11" fill="{ACC}">{i + 1:02d}</text>'
                 f'<text x="{x + 16:.0f}" y="68" font-family="{UI}" font-size="17" font-weight="700" fill="{TXT}">{esc(t)}</text>'
                 f'<text x="{x + 16:.0f}" y="88" font-family="{UI}" font-size="11.5" fill="{MUTED}">{esc(d)}</text>')
        if i < n - 1:
            ax = x + bw + gap / 2
            b.append(f'<path d="M{ax - 4:.1f} 54 L{ax + 3:.1f} 60 L{ax - 4:.1f} 66" fill="none" stroke="{MUTED}" stroke-width="2" '
                     f'stroke-linecap="round" stroke-linejoin="round"/>')
    return svg(W, H, "\n".join(b), "", "Analysis workflow")


def main():
    for name, content in {"banner.svg": banner(), "glance.svg": glance(), "workflow.svg": workflow()}.items():
        (ASSETS / name).write_text(content, encoding="utf-8")
        print(f"  wrote assets/{name}")
    print("Done. Commit the assets folder and push.")


if __name__ == "__main__":
    main()
