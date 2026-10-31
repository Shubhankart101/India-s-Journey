"""Generate the original illustrated backgrounds for every group and subgroup.

Each scene is a layered SVG (sky, glow, stars, far hills, a themed foreground) with gentle CSS animation:
drifting smoke and clouds, turning gears, moving vehicles, sweeping radar, twinkling windows. Animations stop
under prefers-reduced-motion. Output goes to docs/assets/ (static site) and frontend/public/art/ (React app).

    python scripts/generate_art.py
"""
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIRS = [ROOT / 'docs' / 'assets', ROOT / 'frontend' / 'public' / 'art']
W, H = 1200, 600

STYLE = """<style>
.tw{animation:tw 4s ease-in-out infinite}
@keyframes tw{0%,100%{opacity:.2}50%{opacity:1}}
.rot{transform-box:view-box;transform-origin:0 0;animation:rot 16s linear infinite}
.rot-r{transform-box:view-box;transform-origin:0 0;animation:rot 12s linear infinite reverse}
.rot-slow{transform-box:view-box;transform-origin:0 0;animation:rot 40s linear infinite}
@keyframes rot{to{transform:rotate(360deg)}}
.swing{transform-box:view-box;transform-origin:0 0;animation:swing 5s ease-in-out infinite}
@keyframes swing{0%,100%{transform:rotate(-14deg)}50%{transform:rotate(14deg)}}
.needle{transform-box:view-box;transform-origin:0 0;animation:needle 7s ease-in-out infinite}
@keyframes needle{0%,100%{transform:rotate(-55deg)}60%{transform:rotate(38deg)}}
.smoke{transform-box:fill-box;transform-origin:center;animation:smoke 8s ease-out infinite;opacity:0}
@keyframes smoke{0%{transform:translate(0,0) scale(.5);opacity:0}20%{opacity:.5}100%{transform:translate(46px,-130px) scale(2);opacity:0}}
.bob{animation:bob 6s ease-in-out infinite}
@keyframes bob{50%{transform:translateY(7px)}}
.float{animation:float 7s ease-in-out infinite}
@keyframes float{50%{transform:translateY(-16px)}}
.drift{animation:drift 90s linear infinite}
@keyframes drift{from{transform:translateX(-420px)}to{transform:translateX(1320px)}}
.drive{animation:drive 16s linear infinite}
@keyframes drive{from{transform:translateX(-360px)}to{transform:translateX(1500px)}}
.drive-r{animation:driver 19s linear infinite}
@keyframes driver{from{transform:translateX(1500px)}to{transform:translateX(-360px)}}
.fly{animation:fly 20s linear infinite}
@keyframes fly{from{transform:translate(-360px,50px)}to{transform:translate(1560px,-70px)}}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 5s ease-in-out infinite}
@keyframes pulse{50%{transform:scale(1.08);opacity:.75}}
.ping{transform-box:fill-box;transform-origin:center;animation:ping 3.2s ease-out infinite}
@keyframes ping{from{transform:scale(.35);opacity:.9}to{transform:scale(1.7);opacity:0}}
.draw{stroke-dasharray:1000;animation:draw 7s ease-in-out infinite alternate}
@keyframes draw{from{stroke-dashoffset:1000}to{stroke-dashoffset:0}}
.flow{stroke-dasharray:22 16;animation:flow 1.6s linear infinite}
@keyframes flow{to{stroke-dashoffset:-38}}
.wave{animation:wave 6s ease-in-out infinite}
@keyframes wave{50%{transform:translateX(-30px)}}
.drop{animation:drop 3.5s ease-in infinite}
@keyframes drop{0%{transform:translateY(-60px);opacity:0}25%{opacity:1}80%{transform:translateY(0);opacity:1}100%{transform:translateY(8px);opacity:0}}
.scroll{animation:scroll 14s linear infinite}
@keyframes scroll{to{transform:translateX(-120px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.smoke{opacity:.35}}
</style>"""

PALETTES = {
    # sky top, sky bottom, glow, far hills, ground, ink (structures), accent, highlight
    'saffron': ('#1a1033', '#c4672f', '#ffd38a', '#4a2a3a', '#20141d', '#f6dcc0', '#ff9933', '#fff1d6'),
    'dusk':    ('#0e1530', '#7a3f6b', '#ffb38a', '#352245', '#140f22', '#f1d7e6', '#ff8fa3', '#ffe7ef'),
    'night':   ('#030812', '#1b2b55', '#bcd4ff', '#16223f', '#070c18', '#cfe0ff', '#58a6ff', '#ffffff'),
    'teal':    ('#04161d', '#1d6b73', '#a6fff0', '#0f3a42', '#05181d', '#d5fff8', '#2ee6c5', '#f0fffc'),
    'forest':  ('#06140c', '#2f6b3b', '#e6ffb0', '#173d23', '#07140b', '#dff5d8', '#7ddc6a', '#f4ffe8'),
    'desert':  ('#21120a', '#b8783a', '#ffe3a3', '#5a3a22', '#25160c', '#f7e2c4', '#ffb547', '#fff4de'),
    'steel':   ('#0a0d12', '#4b5563', '#ffb070', '#262c36', '#0b0e13', '#e5e9f0', '#ff7a1a', '#fff3e6'),
    'royal':   ('#0b0a2a', '#3f2f8f', '#ffd6ff', '#241c5a', '#0b0a20', '#e6dcff', '#b18cff', '#ffffff'),
    'crimson': ('#150508', '#7a1f2b', '#ffc2a8', '#3d1219', '#120508', '#ffdcd6', '#ff5a5f', '#fff0ee'),
    'ocean':   ('#03101f', '#14548a', '#c7ecff', '#0d3157', '#041121', '#d8f0ff', '#38bdf8', '#f2fbff'),
    'rose':    ('#160b18', '#8b3a62', '#ffd1e3', '#43203a', '#140a15', '#ffe0ee', '#ff6fae', '#fff2f8'),
    'emerald': ('#03130f', '#0f6b52', '#b9ffe2', '#0d3b30', '#03130f', '#d9fff1', '#34d399', '#effff8'),
    'gold':    ('#140f02', '#8a6a12', '#fff0a8', '#3e3008', '#130f03', '#fff3c8', '#facc15', '#fffbe6'),
    'slate':   ('#060a10', '#334155', '#dbeafe', '#1e293b', '#060a10', '#e2e8f0', '#60a5fa', '#f8fafc'),
    'usa':     ('#050a1c', '#26346e', '#ffe2e2', '#1a2350', '#060a1a', '#e9edff', '#ef4444', '#ffffff'),
}


def f(value):
    return f'{value:.1f}'.rstrip('0').rstrip('.')


def g(content, transform='', cls='', style='', opacity=None):
    attrs = ''
    if transform:
        attrs += f' transform="{transform}"'
    if cls:
        attrs += f' class="{cls}"'
    if style:
        attrs += f' style="{style}"'
    if opacity is not None:
        attrs += f' opacity="{f(opacity)}"'
    return f'<g{attrs}>{content}</g>'


def at(x, y, s=1.0):
    return f'translate({f(x)} {f(y)}) scale({f(s)})'


def rect(x, y, w, h, fill, rx=0, extra=''):
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" fill="{fill}"{extra}/>'


def circle(cx, cy, r, fill, extra=''):
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}"{extra}/>'


def path(d, fill='none', stroke=None, width=None, extra=''):
    attrs = f' fill="{fill}"'
    if stroke:
        attrs += f' stroke="{stroke}" stroke-width="{f(width or 4)}" stroke-linecap="round" stroke-linejoin="round"'
    return f'<path d="{d}"{attrs}{extra}/>'


def text(x, y, value, size, fill, weight=700):
    return (f'<text x="{f(x)}" y="{f(y)}" font-family="Arial, Helvetica, sans-serif" font-size="{f(size)}" '
            f'font-weight="{weight}" text-anchor="middle" dominant-baseline="central" fill="{fill}">{value}</text>')


def delay(seconds):
    return f'animation-delay:{f(seconds)}s'


# ---------- Scenery layers ----------

def sky(p, uid):
    return (f'<defs><linearGradient id="sky{uid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{p[0]}"/><stop offset="1" stop-color="{p[1]}"/></linearGradient>'
            f'<radialGradient id="glow{uid}"><stop offset="0" stop-color="{p[2]}" stop-opacity=".95"/>'
            f'<stop offset=".35" stop-color="{p[2]}" stop-opacity=".35"/><stop offset="1" stop-color="{p[2]}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="ground{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p[4]}" stop-opacity=".7"/>'
            f'<stop offset="1" stop-color="{p[4]}"/></linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#sky{uid})"/>')


def glow(p, uid, cx, cy, r):
    return (circle(cx, cy, r * 3.2, f'url(#glow{uid})', ' class="pulse"')
            + circle(cx, cy, r, p[7], ' opacity=".85"'))


def stars(rng, p, n=40, top=0, bottom=260):
    out = []
    for i in range(n):
        x, y = rng.uniform(0, W), rng.uniform(top, bottom)
        r = rng.choice([0.8, 1.1, 1.4, 2.0])
        cls = ' class="tw"' if i % 3 == 0 else ''
        style = f' style="{delay(rng.uniform(0, 4))}"' if cls else ''
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{p[7]}" opacity=".7"{cls}{style}/>')
    return ''.join(out)


def clouds(rng, p, n=3, top=60, bottom=200):
    out = []
    for i in range(n):
        y = rng.uniform(top, bottom)
        s = rng.uniform(0.7, 1.4)
        shape = (f'<ellipse cx="0" cy="0" rx="{f(90 * s)}" ry="{f(18 * s)}" fill="{p[7]}"/>'
                 f'<ellipse cx="{f(-30 * s)}" cy="{f(-12 * s)}" rx="{f(40 * s)}" ry="{f(20 * s)}" fill="{p[7]}"/>'
                 f'<ellipse cx="{f(25 * s)}" cy="{f(-16 * s)}" rx="{f(46 * s)}" ry="{f(26 * s)}" fill="{p[7]}"/>')
        out.append(g(g(shape, f'translate(0 {f(y)})'), cls='drift', style=delay(-rng.uniform(0, 90)), opacity=0.1 + 0.05 * i))
    return ''.join(out)


def hills(rng, base, amp, fill, opacity=1.0, step=150):
    points = [(x, base - rng.uniform(0.25, 1) * amp) for x in range(-step, W + 2 * step, step)]
    d = f'M-200 {H} L{f(points[0][0])} {f(points[0][1])}'
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        d += f' Q{f(x0 + step / 2)} {f(min(y0, y1) - amp * 0.25)} {f(x1)} {f(y1)}'
    d += f' L{W + 200} {H}Z'
    return path(d, fill, extra=f' opacity="{f(opacity)}"')


def mountains(rng, base, amp, fill, snow=None, opacity=1.0):
    x, d, caps = -80, f'M-80 {H} L-80 {base}', []
    while x < W + 80:
        width = rng.uniform(120, 240)
        peak = base - rng.uniform(0.5, 1) * amp
        px = x + width / 2
        d += f' L{f(px)} {f(peak)} L{f(x + width)} {f(base)}'
        if snow:
            caps.append(f'M{f(px - width * 0.13)} {f(peak + amp * 0.18)} L{f(px)} {f(peak)} L{f(px + width * 0.13)} {f(peak + amp * 0.18)} '
                        f'L{f(px + width * 0.05)} {f(peak + amp * 0.13)} L{f(px - width * 0.04)} {f(peak + amp * 0.2)}Z')
        x += width * 0.8
    d += f' L{W + 80} {H}Z'
    out = path(d, fill, extra=f' opacity="{f(opacity)}"')
    if snow:
        out += path(' '.join(caps), snow, extra=' opacity=".85"')
    return out


def skyline(rng, p, x0, x1, base, hmin, hmax, fill=None, windows=True, opacity=1.0):
    out, x = [], x0
    while x < x1:
        w = rng.uniform(34, 80)
        h = rng.uniform(hmin, hmax)
        out.append(rect(x, base - h, w - 4, h, fill or p[3]))
        if rng.random() < 0.25:
            out.append(rect(x + w / 2 - 3, base - h - 26, 4, 26, fill or p[3]))
        if windows:
            for wy in range(int(base - h + 12), int(base - 10), 18):
                for wx in range(int(x + 7), int(x + w - 12), 13):
                    if rng.random() < 0.3:
                        cls = ' class="tw"' if rng.random() < 0.3 else ''
                        style = f' style="{delay(rng.uniform(0, 4))}"' if cls else ''
                        out.append(f'<rect x="{wx}" y="{wy}" width="5" height="7" fill="{p[2]}" opacity=".75"{cls}{style}/>')
        x += w
    return g(''.join(out), opacity=opacity)


def ground(p, uid, y):
    return rect(-10, y, W + 20, H - y + 10, f'url(#ground{uid})')


def water(p, y, depth=None):
    depth = depth or H - y
    out = rect(-10, y, W + 20, depth + 10, p[3], extra=' opacity=".9"')
    for i, wy in enumerate(range(int(y + 14), int(y + depth), 22)):
        d = ' '.join(f'M{x} {wy} q15 -7 30 0 t30 0' for x in range(-60, W + 60, 120))
        out += g(path(d, stroke=p[7], width=2, extra=' opacity=".25"'), cls='wave', style=delay(-i * 1.3))
    return out


def road(p, y, h=46):
    out = rect(-10, y, W + 20, h, '#0b0b0d', extra=' opacity=".85"')
    out += path(f'M-40 {y + h / 2}H{W + 40}', stroke=p[7], width=3, extra=' class="flow" opacity=".55"')
    return out


# ---------- Motifs (drawn around a local origin at the base centre) ----------

def gear(r, fill, teeth=10, hole=None):
    pts = []
    for i in range(teeth * 2):
        a = math.pi * i / teeth
        rr = r if i % 2 == 0 else r * 0.8
        a0, a1 = a - math.pi / teeth / 2.2, a + math.pi / teeth / 2.2
        pts.append(f'{f(rr * math.cos(a0))} {f(rr * math.sin(a0))} L{f(rr * math.cos(a1))} {f(rr * math.sin(a1))}')
    d = 'M' + ' L'.join(pts) + 'Z'
    return path(d, fill) + circle(0, 0, r * 0.32, hole or '#000', ' opacity=".55"')


def spinning(x, y, content, cls='rot', dl=0):
    return g(g(content, cls=cls, style=delay(dl) if dl else ''), f'translate({f(x)} {f(y)})')


def smoke_puffs(x, y, color, n=4, size=16):
    return ''.join(circle(x, y, size, color, f' class="smoke" style="{delay(i * 2)}"') for i in range(n))


def factory(p, w=360):
    out = rect(-w / 2, -120, w, 120, p[3])
    teeth = ''.join(f'M{f(-w / 2 + i * w / 4)} -120 l{f(w / 8)} -50 v50Z' for i in range(4))
    out += path(teeth, p[3])
    for i, (cx, ch) in enumerate([(-w / 2 + 40, 240), (-w / 2 + 90, 200), (w / 2 - 60, 260)]):
        out += rect(cx - 14, -ch, 28, ch, p[3]) + rect(cx - 14, -ch, 28, 10, p[6], extra=' opacity=".8"')
        out += smoke_puffs(cx, -ch - 10, p[7], 4, 15)
    for wx in range(int(-w / 2 + 24), int(w / 2 - 30), 44):
        out += rect(wx, -80, 26, 34, p[2], extra=f' class="tw" style="{delay((wx % 7) * .5)}" opacity=".8"')
    return out


def gears_cluster(p):
    return (spinning(0, -150, gear(110, p[5], 12, p[1]), 'rot-slow')
            + spinning(150, -60, gear(70, p[6], 9, p[1]), 'rot-r')
            + spinning(-130, -40, gear(54, p[2], 8, p[1]), 'rot'))


def crane(p, h=280, boom=220):
    out = rect(-10, -h, 20, h, p[5]) + path(f'M-10 {-h} L{boom} {-h} L-10 {-h + 40}Z', p[5])
    out += path(f'M-60 {-h} H{boom}', stroke=p[5], width=6)
    lattice = ''.join(f'M-10 {-y} L10 {-y - 22} ' for y in range(0, h, 22))
    out += path(lattice, stroke=p[1], width=2)
    hook = path('M0 0 V110', stroke=p[7], width=2) + rect(-28, 110, 56, 34, p[6])
    out += g(hook, f'translate({boom - 60} {-h})', cls='swing')
    return out


def containers(p, rng, cols=6, rows=3):
    colors = [p[6], p[2], p[5], '#3b82f6', '#22c55e', '#ef4444']
    out = ''
    for r in range(rows):
        for c in range(cols - r):
            out += rect(-cols * 33 + c * 66 + r * 33, -(r + 1) * 30, 62, 28, rng.choice(colors), 2, ' opacity=".9"')
    return out


def ship(p, rng):
    hull = path('M-320 -40 H330 L280 40 H-280Z', '#0b0f17') + rect(-320, -44, 650, 8, p[6])
    deck = rect(200, -130, 90, 90, p[5]) + rect(225, -170, 30, 40, p[6])
    return g(hull + g(containers(p, rng, 7, 3), 'translate(-60 -40)') + deck + smoke_puffs(240, -175, p[7], 3, 14), cls='bob')


def bank(p, cols=6, w=420):
    out = path(f'M{-w / 2 - 20} -260 L0 -350 L{w / 2 + 20} -260Z', p[5])
    out += rect(-w / 2 - 20, -262, w + 40, 18, p[5]) + rect(-w / 2 - 30, -24, w + 60, 24, p[5])
    gap = w / (cols - 1)
    for i in range(cols):
        out += rect(-w / 2 + i * gap - 14, -244, 28, 220, p[5], extra=' opacity=".9"')
    out += circle(0, -298, 22, p[6], ' class="pulse"') + text(0, -298, '₹', 28, p[1])
    return out


def bar_chart(p, rng, n=7, w=420, hmax=240):
    out = path(f'M{-w / 2} 0 H{w / 2} M{-w / 2} 0 V{-hmax - 30}', stroke=p[5], width=3)
    bw = w / n
    pts = []
    for i in range(n):
        h = hmax * (0.25 + 0.75 * (i + rng.random() * 1.5) / (n + 1))
        x = -w / 2 + i * bw + 10
        out += rect(x, -h, bw - 20, h, p[6] if i % 2 else p[2], 3, f' class="tw" style="{delay(i * .4)}" opacity=".85"')
        pts.append(f'{f(x + bw / 2 - 10)} {f(-h - 24)}')
    out += path('M' + ' L'.join(pts), stroke=p[7], width=4, extra=' class="draw" pathLength="1000"')
    return out


def line_chart(p, rng, w=520, h=200):
    pts, y = [], -h * 0.3
    for i in range(14):
        y = max(-h, min(-10, y - rng.uniform(-30, 42)))
        pts.append(f'{f(-w / 2 + i * w / 13)} {f(y)}')
    line = 'M' + ' L'.join(pts)
    grid = ''.join(f'M{-w / 2} {-gy} H{w / 2} ' for gy in range(0, h + 1, 50))
    return (path(grid, stroke=p[5], width=1, extra=' opacity=".25"')
            + path(line + f' L{w / 2} 0 L{-w / 2} 0Z', p[6], extra=' opacity=".18"')
            + path(line, stroke=p[6], width=5, extra=' class="draw" pathLength="1000"'))


def coins(p, n=5):
    out = ''
    for s in range(3):
        for i in range(n - s):
            out += f'<ellipse cx="{s * 70 - 70}" cy="{-i * 14 - 8}" rx="30" ry="9" fill="{p[6]}" stroke="{p[1]}" stroke-width="2"/>'
    return out + g(circle(0, 0, 34, p[2]) + text(0, 0, '₹', 38, p[1]), 'translate(0 -150)', cls='float')


def pylon(p, h=260):
    d = (f'M-40 0 L-8 {-h} L8 {-h} L40 0 M-30 {-h * .3} H30 M-20 {-h * .6} H20 '
         f'M-60 {-h * .78} H60 M-46 {-h * .9} H46 M-36 0 L20 {-h * .3} M36 0 L-20 {-h * .3}')
    return path(d, stroke=p[5], width=4)


def power_lines(p, xs, h=260, base=0):
    out = ''.join(g(pylon(p, h), f'translate({x} {base})') for x in xs)
    for a, b in zip(xs, xs[1:]):
        for yy, off in ((-h * .78, 60), (-h * .9, 46)):
            out += path(f'M{a + off} {base + yy} Q{(a + b) / 2} {base + yy + 40} {b - off} {base + yy}', stroke=p[2], width=2,
                        extra=' class="flow" opacity=".7"')
    return out


def furnace(p):
    out = path('M-70 0 L-50 -260 H50 L70 0Z', p[3]) + rect(-56, -280, 112, 22, p[5])
    out += circle(0, -60, 38, p[6], ' class="pulse"') + circle(0, -60, 22, p[7], ' opacity=".8"')
    out += path('M60 -200 Q160 -200 170 -60 V0', stroke=p[5], width=16)
    out += smoke_puffs(0, -290, p[7], 4, 18)
    pour = path('M120 -40 Q170 -10 200 0', stroke=p[6], width=10, extra=' class="flow"')
    return out + pour + f'<ellipse cx="230" cy="-4" rx="70" ry="14" fill="{p[6]}" class="pulse"/>'


def headframe(p):
    d = 'M-80 0 L-20 -300 H20 L80 0 M-60 -80 H60 M-46 -150 H46 M-32 -220 H32 M-80 0 L32 -220 M80 0 L-32 -220 M20 -300 L160 0'
    wheel = g(circle(0, 0, 34, 'none', f' stroke="{p[6]}" stroke-width="6"') + path('M-34 0H34M0 -34V34', stroke=p[6], width=4), cls='rot')
    return path(d, stroke=p[5], width=6) + g(wheel, 'translate(0 -300)') + rect(-110, -40, 60, 40, p[3])


def ore_cart(p, rng):
    ore = ''.join(circle(rng.uniform(-50, 50), rng.uniform(-78, -60), rng.uniform(10, 18), rng.choice([p[6], p[2], p[5]])) for _ in range(8))
    body = path('M-70 -60 H70 L56 -14 H-56Z', p[3]) + ore
    wheels = ''.join(g(g(circle(0, 0, 14, p[5]) + rect(-2, -14, 4, 28, p[1]), cls='rot'), f'translate({x} -8)') for x in (-36, 36))
    return g(body + wheels, cls='drive')


def rails(p, y):
    ties = ''.join(f'M{x} {y + 4} v10 ' for x in range(-20, W + 20, 26))
    return path(ties, stroke=p[5], width=6, extra=' opacity=".5"') + path(f'M-20 {y}H{W + 20}M-20 {y + 14}H{W + 20}', stroke=p[5], width=3)


def pumpjack(p):
    base = path('M-60 0 L0 -140 L60 0', stroke=p[5], width=8) + rect(-90, -10, 260, 10, p[5])
    beam = g(rect(-130, -10, 260, 20, p[6], 4) + path('M-130 -20 Q-170 0 -130 40', p[6], stroke=p[6], width=10), cls='swing')
    return base + g(beam, 'translate(0 -140)') + rect(110, -60, 40, 60, p[3])


def crystals(p, rng, n=7):
    out = ''
    for i in range(n):
        x, h, w = -n * 30 + i * 60 + rng.uniform(-10, 10), rng.uniform(80, 220), rng.uniform(34, 56)
        c = [p[6], p[2], p[7], '#38bdf8', '#a78bfa'][i % 5]
        tilt = rng.uniform(-14, 14)
        shard = path(f'M{-w / 2} 0 L{-w / 2} {-h * .7} L0 {-h} L{w / 2} {-h * .7} L{w / 2} 0Z', c, extra=' opacity=".85"')
        shard += path(f'M0 {-h} V0', stroke=p[7], width=2, extra=' opacity=".5"')
        out += g(shard, f'translate({f(x)} 0) rotate({f(tilt)})', cls='tw', style=delay(i * .6))
    return out


def vehicle(p, kind='car', color=None):
    c = color or p[6]
    wheels = lambda xs, r=14: ''.join(g(g(circle(0, 0, r, '#111') + rect(-2, -r, 4, 2 * r, p[5]), cls='rot'), f'translate({x} 0)') for x in xs)
    if kind == 'truck':
        body = rect(-110, -90, 160, 80, p[5], 4) + path('M50 -70 H96 L120 -40 V-10 H50Z', c) + rect(70, -64, 26, 20, p[1])
        return body + wheels((-80, -40, 90), 16)
    if kind == 'bus':
        body = rect(-120, -96, 240, 86, c, 14) + ''.join(rect(x, -84, 34, 28, p[1], 3) for x in range(-104, 100, 42))
        return body + wheels((-70, 70), 16)
    if kind == 'scooter':
        return path('M-40 -20 Q-20 -60 20 -40 L40 -80 M30 -80 H54', stroke=c, width=10) + wheels((-40, 40), 16)
    body = path('M-80 -14 V-40 Q-70 -54 -40 -58 L-14 -84 H40 L70 -56 Q90 -52 92 -36 V-14Z', c)
    return body + path('M-6 -76 H34 L56 -56 H-26Z', p[1], extra=' opacity=".6"') + wheels((-46, 58))


def train(p, cars=4):
    out = path('M0 -100 H140 Q190 -100 200 -50 V-12 H0Z', p[6]) + rect(150, -90, 30, 28, p[1])
    for i in range(1, cars + 1):
        x = -i * 190
        out += rect(x, -100, 180, 88, p[5], 8) + ''.join(rect(x + 14 + j * 42, -86, 30, 26, p[2], 3, ' opacity=".8"') for j in range(4))
    wheels = ''.join(circle(x, -8, 10, '#111') for x in range(-cars * 190 + 20, 200, 48))
    return out + wheels


def bridge(p, span=900, h=200):
    out = rect(-span / 2, -30, span, 20, p[5])
    for x in (-span / 4, span / 4):
        out += rect(x - 12, -h - 30, 24, h + 100, p[5])
        for k in range(1, 7):
            out += path(f'M{f(x)} {-h - 20} L{f(x - k * span / 28)} -30 M{f(x)} {-h - 20} L{f(x + k * span / 28)} -30', stroke=p[2], width=1.6)
    return out


def newspaper(p):
    page = rect(-170, -230, 340, 230, p[7], 6) + rect(-150, -210, 300, 34, p[1], 3)
    page += ''.join(rect(-150, y, 140 if y % 2 else 300, 8, p[3], 3, ' opacity=".55"') for y in range(-160, -20, 18))
    page += rect(10, -160, 140, 100, p[6], 4, ' opacity=".7"')
    return g(page, 'rotate(-6)', cls='float')


def candles(p, rng, n=14, w=560, h=220):
    out, y = '', -h / 2
    for i in range(n):
        o = y
        y = max(-h, min(-20, y + rng.uniform(-40, 34)))
        top, bot = min(o, y), max(o, y)
        x = -w / 2 + i * w / n
        up = y < o
        c = '#22c55e' if up else '#ef4444'
        out += path(f'M{f(x + 10)} {f(top - 16)} V{f(bot + 16)}', stroke=c, width=2)
        out += rect(x, top, 20, max(bot - top, 4), c, 2, f' class="tw" style="{delay(i * .3)}"')
    return out


def phone_qr(p, rng):
    out = rect(-90, -330, 180, 330, p[3], 22) + rect(-78, -310, 156, 290, p[1], 12)
    qr = ''.join(rect(-56 + c * 14, -270 + r * 14, 12, 12, p[7]) for r in range(8) for c in range(8) if rng.random() < .5 or (r < 2 and c < 2))
    out += qr + rect(-60, -120, 120, 34, p[6], 8) + text(0, -103, '₹ PAY', 18, p[1])
    tick = g(circle(0, 0, 28, '#22c55e') + path('M-12 0 L-3 10 L14 -10', stroke='#fff', width=6), 'translate(0 -50)', cls='pulse')
    rings = ''.join(circle(130, -260, 30, 'none', f' stroke="{p[6]}" stroke-width="3" class="ping" style="{delay(i)}"') for i in range(3))
    return out + tick + rings


def network(p, rng, n=11, w=700, h=300):
    nodes = [(rng.uniform(-w / 2, w / 2), rng.uniform(-h, -20)) for _ in range(n)]
    out = ''
    for i, (x, y) in enumerate(nodes):
        for x2, y2 in nodes[i + 1:i + 3]:
            out += path(f'M{f(x)} {f(y)} L{f(x2)} {f(y2)}', stroke=p[6], width=2, extra=' class="flow" opacity=".55"')
    for i, (x, y) in enumerate(nodes):
        out += circle(x, y, 9, p[7]) + circle(x, y, 18, 'none', f' stroke="{p[6]}" stroke-width="2" class="ping" style="{delay(i * .4)}"')
    return out


def cards(p):
    card = lambda c, rot, y, dl: g(rect(-130, -80, 260, 160, c, 16) + rect(-100, -40, 40, 30, p[2], 5) +
                                   rect(-100, 30, 140, 10, p[7], 4, ' opacity=".7"') + circle(80, 40, 18, p[6], ' opacity=".8"'),
                                   f'translate(0 {y}) rotate({rot})', cls='float', style=delay(dl))
    pos = rect(160, -200, 120, 200, p[3], 14) + rect(176, -184, 88, 60, p[2], 6, ' class="tw"')
    pos += ''.join(rect(180 + c * 30, -110 + r * 28, 22, 20, p[5], 3) for r in range(3) for c in range(3))
    return card(p[6], -12, -190, 0) + card('#6366f1', 6, -120, 1.5) + pos


def huts(p, n=4):
    out = ''
    for i in range(n):
        x = -n * 70 + i * 140
        out += rect(x - 50, -70, 100, 70, p[3]) + path(f'M{x - 64} -66 L{x} -130 L{x + 64} -66Z', p[6], extra=' opacity=".85"')
        out += rect(x - 12, -40, 24, 40, p[1]) + rect(x + 22, -52, 18, 16, p[2], extra=f' class="tw" style="{delay(i)}"')
    return out


def person(fill, scale=1.0):
    return g(circle(0, -150, 22, fill) + path('M-34 0 V-80 Q-34 -122 0 -122 Q34 -122 34 -80 V0Z', fill), f'scale({f(scale)})')


def crowd(p, rng, n=9, w=700):
    out = ''
    for i in range(n):
        x = -w / 2 + i * w / (n - 1)
        out += g(person(rng.choice([p[5], p[6], p[2], p[7]]), rng.uniform(.7, 1.05)), f'translate({f(x)} 0)', cls='bob', style=delay(i * .5))
    return out


def map_pins(p, rng, n=6, w=640):
    out = ''
    for i in range(n):
        x, y = rng.uniform(-w / 2, w / 2), rng.uniform(-260, -40)
        pin = path('M0 0 C-22 -26 -26 -40 -26 -52 A26 26 0 1 1 26 -52 C26 -40 22 -26 0 0Z', p[6]) + circle(0, -52, 10, p[1])
        out += f'<ellipse cx="{f(x)}" cy="{f(y + 4)}" rx="22" ry="6" fill="{p[6]}" class="ping" style="{delay(i * .5)}"/>'
        out += g(g(pin, cls='drop', style=delay(i * .55)), f'translate({f(x)} {f(y)})')
    return out


def heartbeat(p, w=900, y=-150):
    d = f'M{-w / 2} {y} H-160 L-130 {y - 30} L-100 {y + 20} L-70 {y - 120} L-40 {y + 80} L-10 {y} H90 L110 {y - 40} L130 {y} H{w / 2}'
    return (path(d, stroke=p[6], width=12, extra=' opacity=".2"')
            + path(d, stroke=p[7], width=5, extra=' class="draw" pathLength="1000"'))


def virus(p, r=60):
    spikes = ''.join(f'<g transform="rotate({a})"><path d="M0 {-r} V{-r - 26}" stroke="{p[6]}" stroke-width="7"/>'
                     f'<circle cx="0" cy="{-r - 30}" r="10" fill="{p[6]}"/></g>' for a in range(0, 360, 30))
    return spikes + circle(0, 0, r, p[3]) + circle(-18, -14, 12, p[6], ' opacity=".6"') + circle(20, 16, 9, p[6], ' opacity=".6"')


def hospital(p):
    out = rect(-220, -260, 440, 260, p[5]) + rect(-80, -320, 160, 60, p[5])
    out += g(rect(-12, -36, 24, 72, '#ef4444') + rect(-36, -12, 72, 24, '#ef4444'), 'translate(0 -290)', cls='pulse')
    for r in range(4):
        for c in range(6):
            out += rect(-196 + c * 68, -236 + r * 52, 40, 30, p[2], 3, f' class="tw" style="{delay((r + c) * .5)}" opacity=".7"')
    return out + rect(-40, -60, 80, 60, p[1])


def ambulance(p):
    body = rect(-120, -100, 170, 90, '#f8fafc', 8) + path('M50 -84 H92 L120 -50 V-10 H50Z', '#f8fafc')
    body += rect(-80, -70, 18, 50, '#ef4444') + rect(-96, -54, 50, 18, '#ef4444') + rect(64, -76, 30, 24, p[1])
    siren = rect(-20, -116, 30, 16, '#ef4444', 4, ' class="tw" style="animation-duration:.8s"')
    wheels = ''.join(circle(x, -10, 16, '#111') for x in (-80, 80))
    return body + siren + wheels


def school(p):
    out = rect(-240, -200, 480, 200, p[3]) + path('M-270 -196 L0 -300 L270 -196Z', p[6])
    out += rect(-8, -360, 4, 70, p[5]) + g(path('M-4 -360 h56 v34 h-56Z', p[6]), cls='swing', style='transform-origin:0 0')
    out += circle(0, -240, 26, p[7]) + path('M0 -240 V-256 M0 -240 H12', stroke=p[1], width=3)
    for c in range(-3, 4):
        if c:
            out += rect(c * 64 - 20, -150, 40, 50, p[2], 3, f' class="tw" style="{delay(abs(c) * .7)}" opacity=".8"')
    return out + rect(-30, -80, 60, 80, p[1])


def grad_cap(p):
    return g(path('M-120 -40 L0 -90 L120 -40 L0 10Z', p[3]) + path('M-70 -20 V40 Q0 70 70 40 V-20', p[3]) +
             path('M100 -40 V40', stroke=p[6], width=4) + circle(100, 44, 8, p[6]), cls='float')


def books(p, rng):
    out = ''
    for i in range(7):
        h = rng.uniform(120, 190)
        out += rect(-210 + i * 60, -h, 50, h, [p[6], p[2], p[5], '#60a5fa'][i % 4], 4) + rect(-200 + i * 60, -h + 20, 30, 8, p[1], 2, ' opacity=".6"')
    return out


def jet(p, color=None):
    c = color or p[5]
    return path('M-90 0 L60 -8 Q100 -6 110 0 Q100 6 60 8Z M-10 -4 L-50 -60 H-30 L30 -6Z M-10 4 L-50 60 H-30 L30 6Z '
                'M-80 -2 L-100 -30 H-86 L-60 -3Z', c) + path('M-100 0 H-170', stroke=p[6], width=4, extra=' opacity=".5" class="flow"')


def radar(p):
    dish = path('M-90 -80 Q0 20 90 -80', p[5], stroke=p[5], width=6) + path('M0 -40 V-110', stroke=p[5], width=5) + circle(0, -112, 7, p[6])
    sweep = g(path('M0 0 L240 -60 A250 250 0 0 1 240 60Z', p[6], extra=' opacity=".22"'), cls='rot', style='animation-duration:6s')
    rings = ''.join(circle(0, 0, r, 'none', f' stroke="{p[6]}" stroke-width="1.5" opacity=".35"') for r in (80, 160, 240))
    return g(rings + sweep, 'translate(0 -260)') + g(dish, 'translate(0 -40) rotate(-20)') + rect(-30, -40, 60, 40, p[3])


def missile(p):
    body = path('M-18 0 V-260 Q0 -330 18 -260 V0Z', p[7]) + path('M-18 -40 L-50 10 H-18Z M18 -40 L50 10 H18Z', p[6])
    flame = g(path('M-14 10 Q0 90 14 10Z', '#ffb347'), cls='pulse')
    return body + flame + rect(-80, 10, 160, 20, p[3])


def submarine(p):
    return g(path('M-260 0 Q-260 -46 -180 -46 H200 Q270 -40 280 0 Q270 40 200 46 H-180 Q-260 46 -260 0Z', p[5]) +
             rect(-40, -100, 90, 56, p[5], 12) + path('M10 -100 V-140 H40', stroke=p[5], width=6) +
             ''.join(circle(x, 0, 8, p[2], f' class="tw" style="{delay(i * .5)}"') for i, x in enumerate(range(-160, 180, 70))), cls='bob')


def satellite(p):
    panel = lambda x: rect(x, -24, 110, 48, '#1d4ed8', 4) + path(''.join(f'M{x + k} -24 V24 ' for k in range(22, 110, 22)), stroke=p[7], width=1)
    sat = panel(-170) + panel(60) + rect(-60, -40, 120, 80, p[5], 8) + path('M0 -40 V-80', stroke=p[5], width=4) + circle(0, -86, 10, p[6], ' class="pulse"')
    return g(sat, cls='float')


def forest(p, rng, n=16, w=1300, hmin=80, hmax=200):
    out = ''
    for i in range(n):
        x, h = -w / 2 + i * w / n + rng.uniform(-20, 20), rng.uniform(hmin, hmax)
        out += g(path(f'M0 0 L{f(-h * .32)} 0 L0 {f(-h)} L{f(h * .32)} 0Z', p[3]) + rect(-5, 0, 10, 16, p[3]),
                 f'translate({f(x)} 0)', cls='bob', style=delay(i * .4) + ';animation-duration:9s')
    return out


def watchtower(p):
    out = path('M-50 0 L-26 -260 H26 L50 0 M-40 -80 H40 M-34 -170 H34 M-50 0 L34 -170 M50 0 L-34 -170', stroke=p[5], width=6)
    out += rect(-60, -300, 120, 44, p[3]) + path('M-74 -296 L0 -340 L74 -296Z', p[3])
    beam = g(path('M0 0 L520 -120 L520 60Z', p[2], extra=' opacity=".18"'), cls='needle')
    return g(beam, 'translate(0 -278)') + out + circle(0, -278, 10, p[7], ' class="pulse"')


def barbed(p, y=-40, w=1300):
    d = f'M{-w / 2} {y}' + ''.join(f' q15 -14 30 0 t30 0' for _ in range(int(w / 60)))
    return path(d, stroke=p[5], width=2) + path(f'M{-w / 2} {y + 40}H{w / 2}', stroke=p[5], width=3) + \
        ''.join(rect(x, y - 30, 6, 90, p[5]) for x in range(int(-w / 2), int(w / 2), 160))


def scales(p):
    beam = g(path('M-150 0 H150', stroke=p[6], width=8) + path('M-150 0 L-190 90 M-150 0 L-110 90 M150 0 L110 90 M150 0 L190 90', stroke=p[6], width=2) +
             f'<ellipse cx="-150" cy="92" rx="48" ry="12" fill="{p[6]}"/><ellipse cx="150" cy="92" rx="48" ry="12" fill="{p[6]}"/>', cls='swing',
             style='animation-duration:8s')
    return path('M0 -300 V0 M-70 0 H70', stroke=p[6], width=10) + g(beam, 'translate(0 -280)') + circle(0, -300, 14, p[7])


def hemicycle(p, rng, rows=7, r0=110, gap=34):
    out = ''
    palette = [p[6], '#ff9933', '#138808', '#3b82f6', '#a855f7', '#eab308', p[7]]
    for row in range(rows):
        r = r0 + row * gap
        n = int(math.pi * r / 26)
        for k in range(n + 1):
            a = math.pi - math.pi * k / n
            out += circle(r * math.cos(a), -r * math.sin(a), 9, palette[min(int(k / (n + 1) * 6), 5)],
                          f' class="tw" style="{delay(rng.uniform(0, 4))}"')
    return out


def ballot_box(p):
    box = rect(-130, -170, 260, 170, p[5], 10) + rect(-70, -176, 140, 12, p[1], 4) + text(0, -86, 'VOTE', 40, p[1], 900)
    paper = g(rect(-46, -60, 92, 110, p[7], 6) + path('M-22 -10 L-6 8 L26 -28', stroke='#16a34a', width=8), cls='drop')
    return box + g(paper, 'translate(0 -220)')


def evm(p):
    out = rect(-120, -320, 240, 320, p[3], 16) + rect(-96, -300, 192, 30, p[1], 6)
    for i in range(6):
        y = -250 + i * 40
        out += rect(-90, y, 120, 26, p[5], 5, ' opacity=".7"') + circle(70, y + 13, 11, '#3b82f6')
        out += circle(48, y + 13, 6, '#ef4444', f' class="tw" style="{delay(i * .7)}"')
    return out


def ink_finger(p):
    return g(path('M-30 0 V-200 Q-30 -240 0 -240 Q30 -240 30 -200 V0Z', '#e8b996') + rect(-12, -236, 24, 40, '#4c1d95', 12), cls='float')


def capitol(p):
    out = rect(-360, -120, 720, 120, p[5]) + rect(-120, -200, 240, 80, p[5])
    out += path('M-100 -200 Q-100 -340 0 -350 Q100 -340 100 -200Z', p[5]) + rect(-6, -400, 12, 56, p[5]) + circle(0, -404, 10, p[6])
    out += ''.join(rect(x, -110, 16, 100, p[1], extra=' opacity=".35"') for x in range(-340, 350, 40))
    return out


def whitehouse(p):
    out = rect(-300, -150, 600, 150, p[5]) + path('M-110 -150 Q0 -230 110 -150Z', p[5])
    out += ''.join(rect(x, -140, 14, 130, p[1], extra=' opacity=".3"') for x in range(-100, 110, 34))
    return out + rect(-4, -290, 4, 70, p[5]) + g(rect(0, -290, 70, 40, p[6]) + ''.join(rect(0, -290 + k * 8, 70, 4, p[7]) for k in range(0, 5, 2)),
                                                 cls='swing', style='transform-origin:0 -290px')


def dollars(p, rng, n=8):
    out = ''
    for i in range(n):
        bill = rect(-70, -32, 140, 64, '#86efac', 6) + rect(-60, -24, 120, 48, 'none', 4, ' stroke="#166534" stroke-width="3"') + text(0, 0, '$', 34, '#166534')
        x, rot = rng.uniform(-400, 400), rng.uniform(-30, 30)
        out += g(g(bill, f'rotate({f(rot)})'), f'translate({f(x)} {f(rng.uniform(-320, -60))})', cls='float', style=delay(i * .8))
    return out


def plane(p):
    return g(g(jet(p, p[7]), 'scale(1.1)'), cls='fly')


def taj(p):
    out = rect(-170, -160, 340, 160, p[7]) + path('M-80 -160 Q-80 -300 0 -320 Q80 -300 80 -160Z', p[7]) + rect(-3, -350, 6, 34, p[7])
    for x in (-250, 250):
        out += rect(x - 10, -280, 20, 280, p[7]) + circle(x, -286, 16, p[7])
    for x in (-120, 120):
        out += path(f'M{x - 30} -160 Q{x - 30} -210 {x} -216 Q{x + 30} -210 {x + 30} -160Z', p[7])
    out += path('M-40 0 V-90 Q0 -130 40 -90 V0Z', p[1], extra=' opacity=".5"')
    return out


def stupa(p):
    return (rect(-220, -40, 440, 40, p[7]) + path('M-180 -40 Q-180 -230 0 -240 Q180 -230 180 -40Z', p[7]) +
            rect(-40, -280, 80, 40, p[7]) + rect(-6, -340, 12, 60, p[7]) + ''.join(rect(-40 + k * 8, -330 + k * 16, 80 - k * 16, 8, p[7]) for k in range(3)))


def temple(p):
    out = path('M-80 0 V-180 Q-60 -300 0 -380 Q60 -300 80 -180 V0Z', p[7])
    out += ''.join(path(f'M{-80 + k * 6} {-180 - k * 40} H{80 - k * 6}', stroke=p[1], width=3, extra=' opacity=".4"') for k in range(5))
    out += rect(-160, -120, 80, 120, p[7]) + rect(80, -120, 80, 120, p[7]) + rect(-3, -410, 6, 32, p[7])
    return out + g(path('M3 -410 l40 10 l-40 10Z', p[6]), cls='swing', style='transform-origin:3px -410px')


def globe(p, r=150):
    lines = path(f'M{-r} 0 H{r} M0 {-r} V{r}', stroke=p[7], width=2, extra=' opacity=".4"')
    lines += ''.join(f'<ellipse cx="0" cy="0" rx="{f(r * k)}" ry="{r}" fill="none" stroke="{p[7]}" stroke-width="2" opacity=".35"/>' for k in (.35, .7))
    lines += ''.join(f'<ellipse cx="0" cy="0" rx="{r}" ry="{f(r * k)}" fill="none" stroke="{p[7]}" stroke-width="2" opacity=".35"/>' for k in (.4,))
    land = g(path('M-100 -60 Q-60 -110 0 -80 Q40 -40 -10 0 Q-60 30 -90 0Z M30 20 Q90 0 110 50 Q80 100 40 80Z', p[6], extra=' opacity=".8"'), cls='wave')
    orbit = g(g(circle(r + 40, 0, 10, p[2]), cls='rot', style='animation-duration:10s'), '')
    return circle(0, 0, r, p[3]) + land + lines + orbit


def pie(p, values, r=150):
    colors = [p[6], p[2], '#60a5fa', '#a78bfa', '#34d399', p[7]]
    total, a0, out = sum(values), -math.pi / 2, ''
    for i, v in enumerate(values):
        a1 = a0 + 2 * math.pi * v / total
        large = 1 if a1 - a0 > math.pi else 0
        mid = (a0 + a1) / 2
        dx, dy = 12 * math.cos(mid), 12 * math.sin(mid)
        d = f'M0 0 L{f(r * math.cos(a0))} {f(r * math.sin(a0))} A{r} {r} 0 {large} 1 {f(r * math.cos(a1))} {f(r * math.sin(a1))}Z'
        out += g(path(d, colors[i % len(colors)]), f'translate({f(dx)} {f(dy)})', cls='tw' if i == 0 else '', style='animation-duration:6s' if i == 0 else '')
        a0 = a1
    return g(out + circle(0, 0, r * .45, p[1]), cls='rot-slow')


def speech(p, rng, n=5):
    out = ''
    for i in range(n):
        x, y, w = rng.uniform(-380, 380), rng.uniform(-320, -80), rng.uniform(110, 170)
        bubble = rect(-w / 2, -40, w, 80, [p[6], p[2], p[7]][i % 3], 22, ' opacity=".9"') + path('M-10 40 L-30 70 L10 40Z', [p[6], p[2], p[7]][i % 3])
        bubble += ''.join(circle(k * 24, 0, 7, p[1]) for k in (-1, 0, 1))
        out += g(bubble, f'translate({f(x)} {f(y)})', cls='float', style=delay(i))
    return out


def ship_wheel(p, r=110):
    spokes = ''.join(f'<g transform="rotate({a})"><path d="M0 0 V{-r - 26}" stroke="{p[6]}" stroke-width="10" stroke-linecap="round"/></g>' for a in range(0, 360, 45))
    return spokes + circle(0, 0, r, 'none', f' stroke="{p[6]}" stroke-width="14"') + circle(0, 0, 24, p[6])


def place(content, x, y, s=1.0, cls='', style='', opacity=None):
    return g(content, at(x, y, s), cls=cls, style=style, opacity=opacity)


# ---------- Scene assembly ----------

def build(uid, pal, backdrop, fg, sun=(980, 130, 46)):
    p = PALETTES[pal]
    rng = random.Random(uid)
    CURRENT['uid'] = uid
    out = [sky(p, uid), stars(rng, p, 46 if p[0] < '#10' else 24), glow(p, uid, *sun), clouds(rng, p)]
    if backdrop in ('mountains', 'snow'):
        out.append(mountains(rng, 420, 200, p[3], snow=p[7] if backdrop == 'snow' else None, opacity=.75))
        out.append(hills(rng, 470, 70, p[4], .9))
    elif backdrop == 'city':
        out.append(hills(rng, 420, 90, p[3], .5))
        out.append(skyline(rng, p, -20, W + 20, 500, 60, 210, opacity=.65))
    elif backdrop == 'sea':
        out.append(hills(rng, 400, 70, p[3], .6))
        out.append(skyline(rng, p, 820, W + 20, 420, 30, 120, opacity=.55))
    else:
        out.append(hills(rng, 420, 110, p[3], .7))
        out.append(hills(rng, 470, 60, p[4], .9))
    out.append(fg(rng, p))
    out.append(f'<rect width="{W}" height="{H}" fill="{p[0]}" opacity=".08"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" '
            f'role="img" aria-hidden="true">{STYLE}{"".join(out)}</svg>')


CURRENT = {'uid': ''}


def on_ground(p, _label, y=500):
    return ground(p, CURRENT['uid'], y)


SCENES = {}


def scene(name, pal, backdrop='hills', sun=(980, 130, 46)):
    def register(fn):
        SCENES[name] = (pal, backdrop, fn, sun)
        return fn
    return register


# Groups
@scene('economy', 'saffron', 'city')
def _(r, p):
    return on_ground(p, 'economy') + place(bank(p), 330, 520, .8) + place(line_chart(p, r), 820, 400, .9) + place(coins(p), 1060, 520, .8)


@scene('industry', 'steel')
def _(r, p):
    return on_ground(p, 'industry') + place(factory(p, 420), 420, 520) + place(gears_cluster(p), 930, 470, .85)


@scene('mining', 'desert', 'mountains')
def _(r, p):
    return on_ground(p, 'mining') + place(headframe(p), 300, 500) + rails(p, 520) + place(ore_cart(p, r), 0, 516) + place(crystals(p, r, 5), 920, 500, .8)


@scene('payments', 'royal', 'city')
def _(r, p):
    return place(network(p, r), 600, 380) + place(phone_qr(p, r), 330, 560, .95) + place(cards(p), 880, 540, .8)


@scene('states', 'emerald')
def _(r, p):
    return on_ground(p, 'states') + place(map_pins(p, r, 7), 620, 420) + place(huts(p, 3), 250, 540, .8) + place(skyline(r, p, 0, 300, 0, 40, 160), 860, 520)


@scene('health', 'teal', 'city')
def _(r, p):
    return on_ground(p, 'health', 520) + place(hospital(p), 400, 520, .9) + place(heartbeat(p), 640, 300, .9) + place(ambulance(p), 0, 548, .8, 'drive')


@scene('social', 'dusk')
def _(r, p):
    return on_ground(p, 'social') + place(huts(p, 3), 290, 520, .9) + place(crowd(p, r, 9, 560), 800, 540, .8) + place(school(p), 1080, 520, .45)


@scene('defence', 'night', 'mountains', (200, 110, 30))
def _(r, p):
    return (on_ground(p, 'defence') + place(radar(p), 900, 520, .9) + place(missile(p), 330, 500, .8)
            + place(jet(p), 0, 160, .9, 'fly') + place(jet(p), 0, 230, .7, 'fly', delay(-7)))


@scene('security', 'forest', 'mountains', (240, 120, 34))
def _(r, p):
    return place(forest(p, r), 600, 520) + place(watchtower(p), 860, 520, .9) + place(barbed(p), 600, 560) + on_ground(p, 'security', 560)


@scene('opinion', 'rose', 'city')
def _(r, p):
    return place(speech(p, r, 5), 420, 560) + place(pie(p, [38, 24, 18, 12, 8]), 900, 300, .9) + place(crowd(p, r, 7, 500), 420, 600, .7)


@scene('elections', 'saffron')
def _(r, p):
    return on_ground(p, 'elections', 520) + place(hemicycle(p, r), 760, 500, .95) + place(ballot_box(p), 250, 540, .9)


@scene('us-elections', 'usa', 'city', (220, 120, 36))
def _(r, p):
    return on_ground(p, 'us', 520) + place(capitol(p), 620, 530, .9) + place(dollars(p, r, 5), 620, 300, .7)


@scene('tourism', 'gold')
def _(r, p):
    return on_ground(p, 'tourism', 520) + place(taj(p), 600, 520, .95) + place(plane(p), 0, 160, .8) + water(p, 540)


# Economic
@scene('macro-skyline', 'saffron', 'city')
def _(r, p):
    return on_ground(p, 'macro', 520) + place(skyline(r, p, 0, 520, 0, 120, 300, p[5]), 80, 520, 1, opacity=.85) + place(line_chart(p, r, 460), 900, 360)


@scene('income-wealth', 'gold')
def _(r, p):
    return on_ground(p, 'income') + place(coins(p, 6), 330, 520, 1.1) + place(crowd(p, r, 7, 460), 830, 540, .8)


@scene('factory-floor', 'steel')
def _(r, p):
    return on_ground(p, 'factory') + place(factory(p, 500), 520, 520) + place(gears_cluster(p), 1040, 360, .55) + road(p, 530, 40) + place(vehicle(p, 'truck'), 0, 566, .7, 'drive')


@scene('port-trade', 'ocean', 'sea', (220, 120, 40))
def _(r, p):
    return water(p, 470) + place(crane(p), 860, 470) + place(crane(p, 240, 180), 1060, 470, .9) + place(ship(p, r), 420, 470, .9) + place(containers(p, r, 5, 3), 960, 470, .8)


@scene('central-bank', 'royal', 'city')
def _(r, p):
    return on_ground(p, 'rbi', 520) + place(bank(p, 8, 520), 600, 520) + place(coins(p), 1060, 540, .7) + place(coins(p), 140, 540, .7)


@scene('commodities', 'desert')
def _(r, p):
    silos = ''.join(rect(x, -220, 70, 220, p[5], 30) + rect(x, -140, 70, 6, p[6]) for x in (-160, -80, 0))
    return on_ground(p, 'commodities') + place(silos, 300, 500) + rails(p, 520) + place(train(p, 4), 0, 518, .7, 'drive') + place(containers(p, r, 4, 2), 960, 500, .9)


@scene('media-press', 'slate', 'city')
def _(r, p):
    return place(newspaper(p), 420, 520, 1.1) + place(speech(p, r, 4), 860, 520, .8) + place(satellite(p), 980, 130, .5)


@scene('stock-market', 'emerald', 'city')
def _(r, p):
    return place(candles(p, r), 600, 400, 1.1) + on_ground(p, 'stocks', 530) + place(line_chart(p, r, 900, 120), 600, 520, .9, opacity=.6)


@scene('union-budget', 'saffron')
def _(r, p):
    return on_ground(p, 'budget') + place(pie(p, [34, 22, 16, 14, 14]), 380, 300) + place(bank(p, 5, 300), 860, 520, .9)


# Industry
@scene('infrastructure', 'dusk', 'sea')
def _(r, p):
    return water(p, 490) + place(bridge(p, 1000), 600, 470) + place(train(p, 5), 0, 440, .55, 'drive') + place(power_lines(p, [-300, 0, 300], 200), 600, 380, .5, opacity=.6)


@scene('food-processing', 'forest')
def _(r, p):
    fields = ''.join(path(f'M-600 {y} Q0 {y - 20} 600 {y}', stroke=p[6], width=4, extra=' opacity=".45"') for y in range(0, 90, 18))
    return on_ground(p, 'food') + place(fields, 600, 520) + place(factory(p, 320), 760, 510, .85) + place(vehicle(p, 'truck', p[2]), 0, 572, .7, 'drive')


@scene('steel-plant', 'steel')
def _(r, p):
    return on_ground(p, 'steel') + place(furnace(p), 420, 510) + place(crane(p, 260, 160), 920, 510, .9) + place(gears_cluster(p), 160, 400, .4, opacity=.6)


@scene('auto-highway', 'night', 'city', (200, 110, 30))
def _(r, p):
    return (road(p, 470, 56) + road(p, 534, 56) + place(vehicle(p, 'car'), 0, 518, .8, 'drive')
            + place(vehicle(p, 'bus', p[2]), 0, 518, .7, 'drive', delay(-8)) + place(vehicle(p, 'truck'), 0, 582, .8, 'drive-r')
            + place(vehicle(p, 'scooter', '#f472b6'), 0, 582, .8, 'drive-r', delay(-9)))


@scene('chem-pharma', 'teal', 'city')
def _(r, p):
    flask = lambda c: path('M-20 -150 V-90 L-70 0 H70 L20 -90 V-150Z', 'none', stroke=p[7], width=5) + path('M-55 -24 L-36 -60 H36 L55 -24 L70 0 H-70Z', c, extra=' class="pulse"')
    bubbles = ''.join(circle(r.uniform(-30, 30), -40, 6, p[7], f' class="smoke" style="{delay(i * 1.2)}"') for i in range(5))
    return on_ground(p, 'chem') + place(flask(p[6]) + bubbles, 300, 520, 1.2) + place(flask('#a78bfa'), 480, 520, .8) + place(network(p, r, 8, 420, 240), 900, 470)


@scene('iip-monitor', 'steel')
def _(r, p):
    return on_ground(p, 'iip') + place(bar_chart(p, r), 420, 500) + place(gears_cluster(p), 900, 440, .8)


# Mining
@scene('metal-ores', 'desert', 'mountains')
def _(r, p):
    return on_ground(p, 'ores') + place(headframe(p), 760, 500, 1.1) + rails(p, 530) + place(ore_cart(p, r), 0, 526) + place(ore_cart(p, r), -200, 526)


@scene('energy-fuel', 'crimson')
def _(r, p):
    return on_ground(p, 'energy') + place(pumpjack(p), 330, 500, 1.1) + place(power_lines(p, [-260, 40, 340]), 820, 500, .9)


@scene('industrial-minerals', 'royal', 'mountains')
def _(r, p):
    return on_ground(p, 'minerals') + place(crystals(p, r, 9), 600, 520, 1.1)


@scene('mineral-exports', 'ocean', 'sea', (220, 120, 40))
def _(r, p):
    heap = path('M-160 0 Q0 -180 160 0Z', p[6]) + path('M-120 0 Q0 -120 120 0Z', p[2], extra=' opacity=".6"')
    return water(p, 480) + place(heap, 1000, 480) + place(crane(p, 230, 170), 860, 480) + place(ship(p, r), 380, 480, .85)


@scene('mining-output', 'gold', 'mountains')
def _(r, p):
    return on_ground(p, 'mining-out') + place(bar_chart(p, r, 6, 380, 200), 820, 480) + rails(p, 530) + place(ore_cart(p, r), 0, 526)


@scene('mineral-prices', 'rose', 'mountains')
def _(r, p):
    return on_ground(p, 'wpi') + place(crystals(p, r, 4), 260, 520) + place(line_chart(p, r, 520, 220), 800, 440) + place(candles(p, r, 8, 300, 140), 820, 300, .7, opacity=.6)


# Payments
@scene('upi-payments', 'royal', 'city')
def _(r, p):
    return place(network(p, r, 12, 900, 340), 600, 420) + place(phone_qr(p, r), 600, 580, 1.1)


@scene('card-spends', 'rose', 'city')
def _(r, p):
    return place(cards(p), 520, 520, 1.15) + place(coins(p), 1000, 540, .7)


@scene('digital-index', 'teal')
def _(r, p):
    return place(globe(p), 380, 300) + place(network(p, r, 10, 520, 300), 880, 470) + on_ground(p, 'dfi', 540)


@scene('state-banking', 'emerald', 'city')
def _(r, p):
    return on_ground(p, 'sbank', 520) + place(bank(p, 5, 300), 360, 520, .9) + place(map_pins(p, r, 5, 420), 880, 480)


@scene('rural-banks', 'forest')
def _(r, p):
    return on_ground(p, 'rrb') + place(huts(p, 4), 440, 520, .9) + place(bank(p, 4, 160), 1000, 520, .7) + place(forest(p, r, 8, 1200, 40, 90), 600, 440, opacity=.4)


@scene('pensions', 'dusk')
def _(r, p):
    bench = rect(-120, -50, 240, 12, p[5]) + rect(-110, -38, 10, 38, p[5]) + rect(100, -38, 10, 38, p[5])
    return on_ground(p, 'pension') + place(bench + place(person(p[7], .55), -50, -40) + place(person(p[6], .5), 50, -40), 420, 520, 1.2) + place(coins(p), 940, 520, .9)


# State performance
@scene('state-gsdp', 'emerald')
def _(r, p):
    return on_ground(p, 'gsdp') + place(bar_chart(p, r, 8, 460), 380, 500) + place(map_pins(p, r, 5, 360), 940, 480)


@scene('state-infra', 'dusk', 'sea')
def _(r, p):
    return water(p, 500) + place(bridge(p, 760), 420, 480) + place(power_lines(p, [-120, 140]), 1000, 500, .8)


@scene('state-industry', 'steel')
def _(r, p):
    return on_ground(p, 'shub') + place(factory(p, 320), 360, 520, .9) + place(factory(p, 260), 760, 520, .6, opacity=.7) + place(map_pins(p, r, 4, 360), 960, 420, .8)


@scene('state-welfare', 'saffron')
def _(r, p):
    return on_ground(p, 'swelf') + place(huts(p, 3), 330, 520, .9) + place(crowd(p, r, 6, 380), 860, 540, .8) + place(map_pins(p, r, 3, 300), 860, 260, .6)


@scene('state-demography', 'rose')
def _(r, p):
    return on_ground(p, 'sdemo', 530) + place(pie(p, [30, 26, 22, 22]), 330, 290, .9) + place(crowd(p, r, 8, 520), 830, 560, .85)


@scene('state-economy', 'gold', 'city')
def _(r, p):
    return on_ground(p, 'secon', 520) + place(line_chart(p, r, 600, 220), 600, 420) + place(map_pins(p, r, 4, 900), 600, 300, .6, opacity=.7)


# Public health
@scene('lifespan', 'teal')
def _(r, p):
    return on_ground(p, 'life') + place(heartbeat(p, 1300), 600, 300) + place(crowd(p, r, 9, 820), 600, 560, .7)


@scene('epidemiology', 'crimson')
def _(r, p):
    return (place(virus(p), 360, 270, 1.2, 'float') + place(virus(p, 40), 820, 200, .9, 'float', delay(-2))
            + place(virus(p, 30), 1000, 380, .8, 'float', delay(-4)) + place(heartbeat(p, 1300), 600, 640, .8) + on_ground(p, 'epi', 540))


@scene('health-infra', 'teal', 'city')
def _(r, p):
    return on_ground(p, 'hinfra', 520) + place(hospital(p), 600, 520) + road(p, 528, 40) + place(ambulance(p), 0, 560, .7, 'drive')


@scene('state-health', 'emerald')
def _(r, p):
    return on_ground(p, 'shealth') + place(map_pins(p, r, 6, 700), 600, 470) + place(heartbeat(p, 1300), 600, 260, .8)


@scene('state-hospitals', 'ocean', 'city')
def _(r, p):
    return on_ground(p, 'shosp', 520) + place(hospital(p), 360, 520, .8) + place(hospital(p), 860, 520, .55, opacity=.8) + place(map_pins(p, r, 3, 300), 1000, 280, .6)


# Social
@scene('demographics', 'dusk')
def _(r, p):
    return on_ground(p, 'demo', 530) + place(crowd(p, r, 11, 900), 600, 560, .85) + place(pie(p, [48, 52]), 1000, 200, .55)


@scene('welfare', 'saffron')
def _(r, p):
    return on_ground(p, 'welfare') + place(huts(p, 4), 480, 520, .9) + place(coins(p), 1040, 520, .7)


@scene('schemes', 'forest')
def _(r, p):
    return on_ground(p, 'schemes') + place(huts(p, 3), 360, 520, .85) + place(power_lines(p, [-200, 120]), 900, 520, .8) + place(phone_qr(p, r), 1100, 540, .45)


@scene('employment', 'steel', 'city')
def _(r, p):
    return on_ground(p, 'employ', 520) + place(factory(p, 300), 320, 520, .8) + place(crowd(p, r, 6, 420), 860, 540, .85)


@scene('education', 'royal')
def _(r, p):
    return on_ground(p, 'edu') + place(school(p), 470, 520, .95) + place(books(p, r), 1000, 520, .6) + place(grad_cap(p), 980, 200, .7)


# Defence
@scene('defence-budget', 'night', 'mountains', (200, 110, 30))
def _(r, p):
    return on_ground(p, 'dbud') + place(bar_chart(p, r, 6, 400, 200), 820, 500) + place(jet(p), 0, 180, .9, 'fly') + place(missile(p), 300, 500, .7)


@scene('defence-exports', 'ocean', 'sea', (200, 110, 30))
def _(r, p):
    warship = path('M-300 -30 H320 L270 30 H-260Z', p[5]) + rect(-80, -110, 160, 80, p[5]) + rect(-20, -170, 40, 60, p[5]) + path('M0 -170 V-220', stroke=p[5], width=4)
    return water(p, 480) + place(warship, 480, 480, .9, 'bob') + place(missile(p), 1000, 480, .7) + place(jet(p), 0, 160, .8, 'fly')


@scene('strategic-assets', 'night', 'sea', (200, 110, 30))
def _(r, p):
    return water(p, 400) + place(submarine(p), 560, 470, .9) + place(satellite(p), 900, 150, .7) + place(radar(p), 160, 400, .4, opacity=.6)


# Crime & security
@scene('northeast-hills', 'forest', 'mountains', (240, 120, 34))
def _(r, p):
    return place(forest(p, r, 22), 600, 520) + place(watchtower(p), 280, 520, .75) + on_ground(p, 'ne', 540)


@scene('kashmir-valley', 'slate', 'snow', (240, 120, 34))
def _(r, p):
    return on_ground(p, 'jk', 520) + place(forest(p, r, 12, 1300, 60, 140), 600, 520, opacity=.8) + place(watchtower(p), 900, 520, .8) + place(barbed(p), 600, 560)


@scene('punjab-border', 'gold')
def _(r, p):
    fields = ''.join(path(f'M-600 {y} Q0 {y - 10} 600 {y}', stroke=p[6], width=5, extra=' opacity=".4"') for y in range(0, 80, 14))
    return on_ground(p, 'pb') + place(fields, 600, 510) + place(barbed(p), 600, 520) + place(watchtower(p), 260, 520, .7)


@scene('law-justice', 'royal', 'city')
def _(r, p):
    return on_ground(p, 'law', 520) + place(scales(p), 600, 520, 1.1) + place(books(p, r), 1020, 520, .5)


@scene('red-corridor', 'crimson', 'mountains', (240, 120, 34))
def _(r, p):
    return place(forest(p, r, 20, 1300, 90, 220), 600, 530) + place(watchtower(p), 920, 530, .8) + on_ground(p, 'lwe', 540)


@scene('counter-terror', 'night', 'city', (200, 110, 30))
def _(r, p):
    return on_ground(p, 'ct', 520) + place(radar(p), 600, 520, 1.1) + place(jet(p), 0, 140, .6, 'fly')


# Pew, Elections
@scene('public-opinion', 'rose', 'city')
def _(r, p):
    return place(speech(p, r, 7), 600, 520) + place(pie(p, [45, 30, 25]), 1000, 280, .6)


@scene('ballot-box', 'saffron')
def _(r, p):
    return on_ground(p, 'ballot') + place(ballot_box(p), 420, 520, 1.1) + place(ink_finger(p), 800, 520, .9) + place(crowd(p, r, 4, 220), 1040, 540, .7)


@scene('lok-sabha', 'saffron', 'city')
def _(r, p):
    return on_ground(p, 'ls', 520) + place(hemicycle(p, r, 9, 110, 34), 600, 520, 1.05)


@scene('vote-map', 'emerald')
def _(r, p):
    return on_ground(p, 'vmap') + place(map_pins(p, r, 7, 620), 480, 480) + place(evm(p), 1000, 520, .8)


@scene('assembly-results', 'dusk')
def _(r, p):
    return on_ground(p, 'assembly', 520) + place(hemicycle(p, r, 6), 380, 510, .8) + place(bar_chart(p, r, 6, 380, 220), 900, 500)


@scene('election-compare', 'royal')
def _(r, p):
    return on_ground(p, 'ecomp', 530) + place(pie(p, [40, 28, 18, 14]), 330, 290, .9) + place(bar_chart(p, r, 6, 380, 220), 860, 510)


# U.S.
@scene('white-house', 'usa', 'hills', (220, 120, 36))
def _(r, p):
    return on_ground(p, 'wh', 520) + place(whitehouse(p), 600, 530, 1.05)


@scene('campaign-finance', 'emerald', 'city')
def _(r, p):
    return on_ground(p, 'cf', 520) + place(dollars(p, r, 9), 600, 560) + place(capitol(p), 600, 540, .45, opacity=.6)


@scene('congress-finance', 'usa', 'city', (220, 120, 36))
def _(r, p):
    return on_ground(p, 'cong', 520) + place(capitol(p), 420, 530, .8) + place(dollars(p, r, 4), 960, 520, .8)


@scene('funding-mix', 'slate')
def _(r, p):
    return on_ground(p, 'fmix', 540) + place(pie(p, [42, 26, 18, 14]), 380, 300) + place(dollars(p, r, 5), 860, 520, .8)


# Tourism
@scene('visitor-trends', 'ocean', 'sea', (220, 120, 40))
def _(r, p):
    return water(p, 500) + place(plane(p), 0, 140) + place(line_chart(p, r, 520, 180), 420, 440, opacity=.8) + place(taj(p), 980, 500, .5)


@scene('heritage-sites', 'gold')
def _(r, p):
    return on_ground(p, 'whs', 520) + place(stupa(p), 250, 520, .8) + place(taj(p), 640, 520, .8) + place(temple(p), 1010, 520, .75)


@scene('global-tourism', 'night', 'hills', (200, 110, 30))
def _(r, p):
    return place(globe(p, 170), 600, 300) + place(plane(p), 0, 120, .7) + on_ground(p, 'gt', 540)


def main():
    for d in OUTPUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
    for name, (pal, backdrop, fn, sun) in SCENES.items():
        svg = build(name, pal, backdrop, fn, sun)
        for d in OUTPUT_DIRS:
            (d / f'{name}.svg').write_text(svg, encoding='utf-8')
    print(f'Generated {len(SCENES)} scenes into {", ".join(str(d.relative_to(ROOT)) for d in OUTPUT_DIRS)}')


if __name__ == '__main__':
    main()
