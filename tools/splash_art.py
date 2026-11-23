# SPDX-License-Identifier: GPL-3.0-only
"""RDPNO's start picture as SVG (an own drawing, in the manner of a Rhodes MK-80, no maker's mark): writes
/home/claude/splash/splash.svg as it was made; render it in a browser with Michroma loaded (site/fonts/), 960 x 960:
site/img/rdpno.jpg. The FM-1's version: the same with plain colours, reduced to 16 colours at 240 x 240
(assets/splash_240.png, then tools/gen_splash.py)."""
import math
W = 960
A, ca, sa = 0, math.cos(math.radians(32)), math.sin(math.radians(32))
C, D = 0.50, 0.74          # the depth axis: toward the viewer, down-right
E, F = -170, 600
def P(u, v): return (E + ca * u + C * v, F - sa * u + D * v)
def poly(pts, fill, extra=""):
    return '<polygon points="%s" fill="%s" %s/>' % (" ".join("%.1f,%.1f" % p for p in pts), fill, extra)
def quad(u0, v0, u1, v1, fill, extra=""):
    return poly([P(u0, v0), P(u1, v0), P(u1, v1), P(u0, v1)], fill, extra)
MAT = f"matrix({ca:.4f} {-sa:.4f} {C:.4f} {D:.4f} {E} {F})"
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}" width="{W}" height="{W}">',
'''<defs>
<style>@font-face{font-family:M;src:url(michroma.woff2)}</style>
<linearGradient id="silver" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9dde0"/><stop offset=".45" stop-color="#b9bfc4"/><stop offset=".55" stop-color="#cfd4d8"/><stop offset="1" stop-color="#8e959b"/></linearGradient>
<linearGradient id="band" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#26282c"/><stop offset=".5" stop-color="#141518"/><stop offset="1" stop-color="#0b0c0e"/></linearGradient>
<radialGradient id="warm" cx=".2" cy=".1" r=".9"><stop offset="0" stop-color="#ffb46a" stop-opacity=".2"/><stop offset=".6" stop-color="#ff9a4a" stop-opacity=".06"/><stop offset="1" stop-color="#ff9a4a" stop-opacity="0"/></radialGradient>
<linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1c1d20"/><stop offset=".6" stop-color="#0d0e10"/><stop offset="1" stop-color="#16171a"/></linearGradient>
<linearGradient id="wood" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3a2a24"/><stop offset="1" stop-color="#1e1512"/></linearGradient>
<linearGradient id="lcd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffb347"/><stop offset="1" stop-color="#d9772a"/></linearGradient>
<linearGradient id="white" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfc9bd"/><stop offset=".25" stop-color="#f3efe6"/><stop offset="1" stop-color="#fbf6ec"/></linearGradient>
<radialGradient id="vig" cx=".45" cy=".45" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>
<filter id="glow"><feGaussianBlur stdDeviation="6"/></filter>
</defs>''',
f'<rect width="{W}" height="{W}" fill="#0b0b0c"/>', '<g transform="translate(-210 -20) scale(1.38)">']
L0, L1 = -200, 1700
# the music rest: dark wood, with grooves
out.append(quad(L0, -520, L1, -170, "url(#wood)"))
for k in range(9):
    v = -500 + k * 38
    out.append(f'<line x1="{P(L0, v)[0]:.1f}" y1="{P(L0, v)[1]:.1f}" x2="{P(L1, v)[0]:.1f}" y2="{P(L1, v)[1]:.1f}" stroke="#120c0a" stroke-width="5"/>')
    out.append(f'<line x1="{P(L0, v+5)[0]:.1f}" y1="{P(L0, v+5)[1]:.1f}" x2="{P(L1, v+5)[0]:.1f}" y2="{P(L1, v+5)[1]:.1f}" stroke="#4a3830" stroke-width="1.5" opacity=".6"/>')
# the silver band, its lower edge a dark lip
out.append(f'<g transform="{MAT}"><rect x="{L0}" y="-170" width="{L1-L0}" height="120" fill="url(#band)"/></g>')
out.append(quad(L0, -172, L1, -162, "url(#silver)"))
out.append(quad(L0, -50, L1, -40, "#2a2c2f"))
# RDPNO on the band
out.append(f'<g transform="{MAT}"><text x="560" y="-86" font-family="M" font-size="64" letter-spacing="7" fill="#ffffff" stroke="#ffffff" stroke-width="3">RDPNO</text>'
           f'<rect x="562" y="-74" width="318" height="7" fill="#2f7fd0"/></g>')
# the panel
out.append(quad(L0, -40, L1, 150, "url(#panel)"))
# the LCD, glowing amber
g = f'<g transform="{MAT}">'
g += '<rect x="960" y="-20" width="210" height="78" rx="4" fill="#060606"/>'
g += '<rect x="972" y="-10" width="186" height="58" rx="3" fill="url(#lcd)" filter="url(#glow)" opacity=".7"/>'
g += '<rect x="972" y="-10" width="186" height="58" rx="3" fill="url(#lcd)"/>'
g += '<text x="1065" y="34" font-family="monospace" font-weight="700" font-size="34" letter-spacing="4" text-anchor="middle" fill="#5a2a08">PIANO</text>'
# buttons right of the LCD, and a row below
for r in range(3):
    for c in range(7):
        x, y = 1205 + c * 46, -24 + r * 30
        g += f'<rect x="{x}" y="{y}" width="34" height="18" rx="3" fill="#2a2c30" stroke="#45484d" stroke-width="1.2"/>'
        if (r, c) in ((0, 2), (1, 5)): g += f'<rect x="{x+12}" y="{y-7}" width="10" height="4" fill="#ff4632"/>'
for c in range(5):
    g += f'<rect x="{960 + c*44}" y="82" width="32" height="18" rx="3" fill="#2a2c30" stroke="#45484d" stroke-width="1.2"/>'
# sliders on the left: slots and caps
for k, pos in enumerate((0.3, 0.55, 0.2, 0.7, 0.45, 0.6)):
    x = 300 + k * 70
    g += f'<rect x="{x}" y="8" width="8" height="118" rx="3" fill="#050505"/>'
    for t in range(6): g += f'<rect x="{x+16}" y="{12+t*21}" width="12" height="2" fill="#5a5e63"/>'
    y = 8 + pos * 100
    g += f'<rect x="{x-14}" y="{y}" width="36" height="20" rx="2" fill="#3a3d42" stroke="#6a6e74" stroke-width="1.5"/>'
    g += f'<rect x="{x-14}" y="{y+8}" width="36" height="3" fill="#cfd3d6"/>'
for c in range(4):
    g += f'<rect x="{760 + c*44}" y="30" width="32" height="18" rx="3" fill="#2a2c30" stroke="#45484d" stroke-width="1.2"/>'
g += '</g>'
out.append(g)
# the key bed: a dark slip, then the keys
out.append(quad(L0, 150, L1, 168, "#060606"))
KW, KL = 50, 340
u = -180
whites = []
while u < L1:
    whites.append(u); u += KW
KEYS_AT = len(out)
for u in whites:
    pts = [P(u + 2, 168), P(u + KW - 2, 168), P(u + KW - 2, 168 + KL), P(u + 2, 168 + KL)]
    front = [P(u + 2, 168 + KL), P(u + KW - 2, 168 + KL)]
    out.append(poly([front[0], front[1], (front[1][0], front[1][1] + 14), (front[0][0], front[0][1] + 14)], "#bdb6a8"))
    out.append(f'<g transform="{MAT}"><rect x="{u+2}" y="168" width="{KW-4}" height="{KL}" fill="url(#white)"/></g>')
# the case in front of the keys
out.insert(KEYS_AT, quad(L0, 168 + KL, L1, 168 + KL + 260, "url(#panel)"))
# black keys: in the octave after whites 0, 1, 3, 4, 5
BW, BL = 30, 215
for i, u in enumerate(whites):
    if (i % 7) in (0, 1, 3, 4, 5) and i + 1 < len(whites):
        bu = u + KW - BW / 2
        f0, f1 = P(bu, 168 + BL), P(bu + BW, 168 + BL)
        # its shadow on the white keys, its front face, its top
        out.append(poly([f0, f1, (f1[0], f1[1] + 12), (f0[0], f0[1] + 12)], "#000"))
        side = [P(bu + BW, 168), P(bu + BW, 168 + BL)]
        out.append(poly([side[0], side[1], (side[1][0], side[1][1] + 12), (side[0][0], side[0][1] + 12)], "#000"))
        out.append(quad(bu, 160, bu + BW, 168 + BL, "#0b0b0b"))
        out.append(quad(bu + 2, 162, bu + 4, 168 + BL - 2, "#262626"))   # (one thin edge catching the light)
out.append('</g>')
out.append(f'<rect width="{W}" height="{W}" fill="url(#warm)"/>')
out.append(f'<rect width="{W}" height="{W}" fill="url(#vig)"/>')
out.append('</svg>')
open('/home/claude/splash/splash.svg', 'w').write("\n".join(out))
