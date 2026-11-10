"""Generate the original illustrated backgrounds for every group and subgroup.

Each scene is a layered SVG (sky, glow, stars, far hills, a themed foreground) with gentle CSS animation:
drifting smoke and clouds, turning gears, moving vehicles, sweeping radar, twinkling windows. Animations stop
under prefers-reduced-motion. Output goes to frontend/public/art/, which is bundled into both hosted apps.

    python scripts/generate_art.py
"""
import html
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIRS = [ROOT / 'frontend' / 'public' / 'art']
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
            f'<stop offset="1" stop-color="{p[4]}"/></linearGradient>'
            f'<linearGradient id="lower{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p[4]}" stop-opacity="0"/>'
            f'<stop offset=".42" stop-color="{p[4]}" stop-opacity=".72"/><stop offset="1" stop-color="{p[4]}" stop-opacity=".98"/></linearGradient>'
            f'<radialGradient id="vignette{uid}"><stop offset=".48" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".42"/></radialGradient>'
            f'<filter id="grain{uid}" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="{sum(map(ord, uid)) % 997}"/>'
            f'<feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 .12"/></feComponentTransfer></filter></defs>'
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


def place(content, x, y, s=1.0, cls='', style='', opacity=None):
    return g(content, at(x, y, s), cls=cls, style=style, opacity=opacity)


# ---------- Scene assembly ----------

def finish_overlay(uid, p, label):
    safe_label = html.escape(label or uid.replace('-', ' ').title())
    length = ' textLength="780" lengthAdjust="spacingAndGlyphs"' if len(safe_label) > 31 else ''
    return (f'<rect width="{W}" height="{H}" fill="url(#lower{uid})"/>'
            f'<rect width="{W}" height="{H}" fill="url(#vignette{uid})"/>'
            f'<text x="600" y="488" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="31" font-weight="700" letter-spacing=".3" fill="{p[7]}"{length}>{safe_label}</text>'
            f'<text x="600" y="535" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="600" letter-spacing="3.5" fill="{p[6]}" opacity=".94">INDIA  •  PUBLIC DATA ATLAS</text>'
            f'<rect width="{W}" height="{H}" fill="#fff" filter="url(#grain{uid})" opacity=".16"/>')


def build(uid, pal, backdrop, fg, sun=(980, 130, 46), label=''):
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
    out.append(finish_overlay(uid, p, label))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" preserveAspectRatio="xMidYMid slice" '
            f'role="img" aria-hidden="true">{STYLE}<g transform="scale(1.333333 1.5)">{"".join(out)}</g></svg>')


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


# ---------- Epics, faiths and journeys ----------

def lotus(p, petals=7, r=70):
    out = ''
    for i in range(petals):
        a = -90 + (i - (petals - 1) / 2) * 24
        out += g(path(f'M0 0 Q{-r * .45} {-r * .7} 0 {-r * 1.5} Q{r * .45} {-r * .7} 0 0Z', p[6] if i % 2 else p[2], extra=' opacity=".9"'), f'rotate({f(a)})')
    return out + circle(0, -6, 10, p[7])


def dharma_wheel(p, r=110):
    spokes = ''.join(path(f'M0 0 L{f(r * .86 * math.cos(math.radians(a)))} {f(r * .86 * math.sin(math.radians(a)))}', stroke=p[7], width=5) for a in range(0, 360, 30))
    return g(circle(0, 0, r, 'none', f' stroke="{p[7]}" stroke-width="10"') + circle(0, 0, r * .2, p[7]) + spokes, cls='rot-slow')


def khanda(p):
    blade = path('M0 -300 L22 -190 L0 -10 L-22 -190Z', p[7])
    ring = circle(0, -150, 62, 'none', f' stroke="{p[7]}" stroke-width="12"')
    sabres = path('M-110 -250 Q-150 -150 -70 -70 M110 -250 Q150 -150 70 -70', stroke=p[7], width=14)
    return blade + ring + sabres + rect(-34, -40, 68, 14, p[6], 4)


def fire_altar(p):
    flame = path('M0 0 Q-90 -70 -12 -220 Q-4 -140 24 -96 Q70 -200 88 -140 Q112 -62 0 0Z', '#ff8b38', '#ffd77b', 5)
    return g(flame, cls='pulse') + path('M-140 0 L-100 -60 H100 L140 0Z', '#9d5930', '#edbd76', 5)


def palm_leaf(p, lines=5):
    return rect(-190, -60, 380, 74, '#c99a55', 8, f' stroke="{p[7]}" stroke-width="3"') + ''.join(path(f'M-165 {-42 + i * 14}H165', stroke='#5a3720', width=2.5, extra=' opacity=".8"') for i in range(lines - 1))


def war_chariot(p):
    wheel = lambda x: place(dharma_wheel(p, 36), x, -48)
    horses = ''.join(path(f'M{-120 - i * 70} -96 q-26 -50 -54 -30 q-18 6 -10 24 l20 12 q28 4 44 -6Z', p[7], extra=' opacity=".9"') for i in range(2))
    return path('M-110 -70 H70 L40 -170 H-90Z', '#b77736', p[7], 5) + wheel(-60) + wheel(20) + horses + path('M40 -170 V-300 L90 -270 L40 -245', stroke=p[6], width=6)


def dotted_route(p, pts, color=None):
    d = 'M' + ' L'.join(f'{x} {y}' for x, y in pts)
    nodes = ''.join(circle(x, y, 11, color or p[6], f' stroke="{p[7]}" stroke-width="3"') for x, y in pts)
    return path(d, stroke=color or p[6], width=5, extra=' stroke-dasharray="4 14" class="flow"') + nodes


@scene('epics-faiths', 'saffron', 'mountains')
def _(r, p):
    return (on_ground(p, 'epics-faiths', 520) + place(stupa(p), 160, 520, .55) + place(temple(p), 450, 520, .7)
            + place(khanda(p), 760, 520, .6) + place(dharma_wheel(p, 80), 980, 300, .9) + place(lotus(p), 1060, 520, .8)
            + dotted_route(p, [(40, 560), (300, 470), (560, 540), (820, 450), (1120, 540)]))


@scene('epic-routes', 'crimson', 'mountains')
def _(r, p):
    bow = path('M-90 -250 Q-10 -90 80 -250 M-90 -250 Q-12 -400 80 -250', stroke=p[6], width=8) + path('M-130 -250 H125 M95 -262 L125 -250 L95 -238', stroke=p[7], width=5)
    return (on_ground(p, 'epic-routes', 520) + place(temple(p), 180, 520, .8) + place(war_chariot(p), 640, 520, .95)
            + place(bow, 1040, 400, .8) + dotted_route(p, [(60, 570), (330, 500), (610, 560), (900, 480), (1150, 560)], p[2]))


@scene('vedic-journeys', 'desert', 'hills')
def _(r, p):
    rivers = ''.join(path(f'M{-60 + i * 30} {60 + i * 40} Q{300 + i * 20} {-40 + i * 30} {640 + i * 10} {100 + i * 26} T{1260} {80 + i * 22}', stroke=(p[6], p[2])[i % 2], width=4, extra=' opacity=".7" class="flow"') for i in range(5))
    return on_ground(p, 'vedic', 520) + place(fire_altar(p), 320, 520, .95) + place(palm_leaf(p), 840, 480, 1) + place(palm_leaf(p, 4), 880, 400, .9) + place(rivers, 0, 380, .8)


@scene('buddhist-journeys', 'saffron', 'mountains')
def _(r, p):
    bodhi = ''.join(path(f'M{x} {-300 - i * 14} q-50 -40 -15 -88 q48 20 15 88Z', p[6], extra=f' opacity="{.5 + i * .1}"') for i, x in enumerate((-170, -70, 30, 120, 210)))
    trunk = path('M0 0 Q-20 -120 -60 -250 M0 0 Q10 -150 40 -260 M0 -90 Q50 -170 130 -250', stroke=p[5], width=16)
    return (on_ground(p, 'buddhist', 525) + place(stupa(p), 250, 520, .95) + place(trunk + bodhi, 720, 520, .9)
            + place(dharma_wheel(p, 70), 1030, 300, .9) + dotted_route(p, [(80, 570), (420, 545), (760, 575), (1100, 548)]))


@scene('jain-journeys', 'forest', 'hills')
def _(r, p):
    hand = (path('M-48 0 V-110 Q-48 -150 -20 -150 V-210 M-20 -150 H20 V-230 M20 -150 H52 V-215 M52 -150 H80 Q94 -150 94 -120 V-60 Q94 0 40 0Z', '#e6c59a', p[7], 4)
            + circle(24, -72, 22, 'none', f' stroke="{p[6]}" stroke-width="8"'))
    peaks = path('M-260 0 L-130 -170 L-40 -90 L60 -230 L190 -90 L260 0Z', p[3], p[7], 4)
    return (on_ground(p, 'jain', 520) + place(peaks, 330, 520, 1.2) + place(temple(p), 760, 520, .75)
            + place(hand, 1030, 520, .8) + place(lotus(p, 5, 50), 120, 540, .7) + dotted_route(p, [(60, 565), (400, 535), (780, 570), (1140, 540)]))


@scene('sikh-journeys', 'royal', 'sea', (220, 120, 36))
def _(r, p):
    shrine = (rect(-190, -120, 380, 120, '#d3a847', 4, ' stroke="#fff0bb" stroke-width="5"')
              + path('M-190 -120 Q-175 -200 -90 -180 Q-55 -255 0 -190 Q55 -255 90 -180 Q175 -200 190 -120Z', '#e3bd65', '#fff0bb', 5)
              + circle(0, -212, 19, '#fff0bb') + rect(-25, -40, 50, 40, '#1d2345'))
    ripples = ''.join(path(f'M{-210 + i * 34} {10 + i * 7} q22 -16 44 0 t44 0', stroke=p[6], width=3, extra=' opacity=".7"') for i in range(13))
    return water(p, 455, 160) + place(shrine, 620, 480, 1.1) + place(ripples, 620, 500, 1.05) + place(khanda(p), 140, 500, .5) + place(khanda(p), 1080, 500, .5) + dotted_route(p, [(40, 580), (360, 560), (700, 585), (1150, 560)])


@scene('folk-stories', 'dusk', 'hills')
def _(r, p):
    book = rect(-120, -150, 240, 150, '#8b4f2a', 10, f' stroke="{p[7]}" stroke-width="5"') + path('M0 -150 V0', stroke=p[7], width=4) + ''.join(path(f'M{-100 + i * 6} {-120 + i * 24}H-12 M12 {-120 + i * 24}H100', stroke=p[7], width=3, extra=' opacity=".6"') for i in range(4))
    camel = (path('M-90 -70 q10 -70 40 -40 q20 -50 50 -10 q40 -10 70 20 l30 -40 l14 10 l-20 54 v60 h-18 v-60 h-80 v60 h-18 v-60Z', p[5], extra=' opacity=".9"'))
    globe_art = place(globe(p, 90), 0, 0)
    return (on_ground(p, 'folk', 520) + place(book, 220, 520, 1) + place(camel, 620, 520, .9) + place(globe_art, 1000, 330, 1)
            + dotted_route(p, [(60, 575), (330, 520), (640, 575), (930, 500), (1140, 560)]))


# ---------- Environment, agriculture and population motifs ----------

def wind_turbine(p, h=260, dl=0):
    blade = path(f'M0 0 L-7 -6 L0 {-h * .42} L7 -6Z', p[7], extra=' opacity=".9"')
    rotor = ''.join(g(blade, f'rotate({a})') for a in (0, 120, 240)) + circle(0, 0, 8, p[6])
    return path(f'M-6 0 L-3 {-h} L3 {-h} L6 0Z', p[5]) + spinning(0, -h, rotor, 'rot', dl)


def solar_panels(p, n=4):
    out = ''
    for i in range(n):
        x = (i - (n - 1) / 2) * 130
        out += path(f'M{x - 56} -40 L{x - 36} -96 L{x + 56} -96 L{x + 36} -40Z', p[3], p[6], 2)
        out += path(f'M{x - 46} -68 H{x + 46} M{x} -96 L{x} -40', stroke=p[6], width=1.5, extra=' opacity=".6"')
        out += rect(x - 3, -40, 6, 40, p[5]) + path(f'M{x - 36} -96 L{x + 56} -96', stroke=p[7], width=2, extra=' class="tw" opacity=".7"')
    return out


def thermometer(p):
    return (rect(-16, -230, 32, 210, p[5], 16) + circle(0, -14, 32, p[5]) + rect(-7, -200, 14, 190, p[6], 7, ' class="pulse"')
            + circle(0, -14, 22, p[6]) + ''.join(path(f'M18 {-60 - i * 30} h14', stroke=p[5], width=3) for i in range(5)))


def rain(p, rng, n=26, w=900, top=-360):
    return ''.join(path(f'M{f(rng.uniform(-w / 2, w / 2))} {f(top + rng.uniform(0, 200))} l-6 22', stroke=p[7], width=2,
                        extra=f' class="drop" opacity=".7" style="{delay(-rng.uniform(0, 3.5))}"') for _ in range(n))


def storm_cloud(p, w=260):
    return (circle(-w * .25, 0, w * .2, p[3]) + circle(0, -w * .12, w * .27, p[3]) + circle(w * .28, 0, w * .19, p[3])
            + rect(-w * .45, 0, w * .9, w * .14, p[3], w * .07))


def lightning(p):
    return path('M20 0 L-14 70 H10 L-18 150 L40 52 H14 L44 0Z', p[2], extra=' class="tw"')


def cyclone(p, r=150):
    arms = ''.join(path(f'M0 0 Q{f(r * .9)} {f(-r * .15)} {f(r * .7)} {f(r * .75)}', stroke=p[7], width=10 - i * 2,
                        extra=' opacity=".55"') for i in range(3))
    return spinning(0, 0, ''.join(g(arms, f'rotate({a})') for a in (0, 120, 240)) + circle(0, 0, r * .12, p[2]), 'rot-r')


def crop_field(p, rng, n=26, w=1100):
    out = ''
    for i in range(n):
        x, h = -w / 2 + i * w / n + rng.uniform(-8, 8), rng.uniform(70, 120)
        stalk = path(f'M0 0 Q4 {f(-h / 2)} 0 {f(-h)}', stroke=p[6], width=3)
        grains = ''.join(f'<ellipse cx="{f((-1) ** k * 6)}" cy="{f(-h + 8 + k * 9)}" rx="5" ry="9" fill="{p[2]}"/>' for k in range(5))
        out += g(stalk + grains, f'translate({f(x)} 0)', cls='bob', style=delay(-i * .3) + ';animation-duration:5s')
    return out


def tractor(p):
    return (rect(-90, -86, 110, 46, p[6], 8) + rect(-10, -130, 50, 60, p[3], 6) + rect(0, -122, 30, 26, p[2], 3, ' opacity=".7"')
            + circle(46, -36, 40, p[5]) + circle(46, -36, 16, p[3]) + circle(-66, -24, 24, p[5]) + circle(-66, -24, 10, p[3])
            + rect(-80, -120, 8, 34, p[5]) + smoke_puffs(-76, -124, p[7], 3, 10))


def cow(p, s=1.0):
    body = (f'<ellipse cx="0" cy="-60" rx="60" ry="32" fill="{p[7]}"/>' + circle(-12, -66, 12, p[3]) + circle(22, -52, 9, p[3])
            + f'<ellipse cx="66" cy="-80" rx="20" ry="15" fill="{p[7]}"/>' + path('M58 -94 l-6 -14 M74 -94 l6 -14', stroke=p[5], width=4)
            + ''.join(rect(x, -36, 10, 36, p[7]) for x in (-44, -24, 22, 40)) + path('M-60 -64 q-20 10 -14 40', stroke=p[7], width=4))
    return g(body, f'scale({f(s)})')


def fish(p, color=None, s=1.0):
    color = color or p[6]
    return g(f'<ellipse cx="0" cy="0" rx="34" ry="16" fill="{color}"/>' + path('M30 0 L58 -18 V18Z', color) + circle(-18, -4, 4, p[0]),
             f'scale({f(s)})')


def sack(p, label='NPK'):
    return (path('M-50 0 Q-60 -70 -40 -120 Q0 -134 40 -120 Q60 -70 50 0Z', p[7]) + path('M-40 -120 Q0 -108 40 -120', stroke=p[3], width=4)
            + text(0, -58, label, 24, p[3]))


def bins(p):
    out = ''
    for i, c in enumerate((p[6], '#3fb950', '#58a6ff')):
        x = (i - 1) * 90
        out += rect(x - 32, -110, 64, 110, c, 6) + rect(x - 38, -122, 76, 14, p[5], 4) + path(f'M{x - 12} -80 V-24 M{x + 12} -80 V-24', stroke=p[0], width=3, extra=' opacity=".4"')
    return out


def landfill(p, rng):
    out = path('M-260 0 Q-140 -150 0 -170 Q150 -150 260 0Z', p[3])
    for _ in range(18):
        out += rect(rng.uniform(-180, 160), rng.uniform(-140, -20), rng.uniform(12, 30), rng.uniform(8, 18), rng.choice((p[6], p[5], p[2])), 3, ' opacity=".7"')
    return out + ''.join(g(circle(0, 0, 10, '#fff', ' opacity=".9"'), f'translate({x} {y})', cls='fly', style=delay(-i * 5)) for i, (x, y) in enumerate(((0, -220), (-90, -260))))


def family(p, rng):
    sizes = (1.0, .95, .6, .5)
    return ''.join(g(person(p[6] if i % 2 else p[7], s), f'translate({(i - 1.5) * 70} 0)', cls='bob', style=delay(-i)) for i, s in enumerate(sizes))


def plate(p):
    return (f'<ellipse cx="0" cy="-20" rx="120" ry="30" fill="{p[7]}"/>' + f'<ellipse cx="0" cy="-26" rx="94" ry="20" fill="{p[3]}"/>'
            + circle(-40, -34, 18, p[2]) + circle(10, -36, 20, p[6]) + circle(52, -30, 14, '#3fb950'))


# Environment & Climate
@scene('environment', 'forest', 'mountains')
def _(r, p):
    return on_ground(p, 'env', 520) + place(forest(p, r, 12, 700), 320, 520, .8) + place(wind_turbine(p), 880, 520) + place(wind_turbine(p, 200, -3), 1030, 520) + place(solar_panels(p, 2), 640, 540, .7)


@scene('climate-weather', 'ocean', 'hills', (300, 140, 50))
def _(r, p):
    return (on_ground(p, 'clim', 540) + place(storm_cloud(p), 760, 170) + place(rain(p, r), 760, 540) + place(lightning(p), 820, 200, .9)
            + place(thermometer(p), 260, 520, .9))


@scene('forests-land', 'forest')
def _(r, p):
    return on_ground(p, 'forest', 520) + place(forest(p, r, 22, 1300, 110, 260), 600, 520) + place(forest(p, r, 10, 700, 60, 120), 900, 560, .8)


@scene('pollution-waste', 'slate', 'city')
def _(r, p):
    return on_ground(p, 'waste', 520) + place(landfill(p, r), 380, 520, .9) + place(bins(p), 900, 520, .85) + place(factory(p, 300), 1120, 520, .4, opacity=.6)


@scene('disasters', 'night', 'sea', (200, 110, 30))
def _(r, p):
    return water(p, 470) + place(cyclone(p, 170), 760, 240) + place(storm_cloud(p, 300), 320, 150) + place(rain(p, r, 20, 500), 320, 470) + place(lightning(p), 360, 190)


@scene('energy-transition', 'gold')
def _(r, p):
    return (on_ground(p, 'energy', 520) + place(solar_panels(p, 4), 360, 540, .85) + place(wind_turbine(p, 280), 820, 520)
            + place(wind_turbine(p, 230, -4), 990, 520) + place(wind_turbine(p, 180, -7), 1120, 520) + power_lines(p, [620], 220, 520))


# Agriculture & Food
@scene('agriculture', 'saffron')
def _(r, p):
    return on_ground(p, 'agri', 520) + place(crop_field(p, r, 20, 760), 380, 540) + place(tractor(p), 920, 540, .9) + place(huts(p, 2), 1100, 520, .5)


@scene('crop-production', 'gold')
def _(r, p):
    return on_ground(p, 'crop', 520) + place(crop_field(p, r, 34, 1300), 600, 560, 1.1) + place(bar_chart(p, r, 5, 260, 160), 980, 300, .6)


@scene('farm-inputs', 'desert')
def _(r, p):
    return on_ground(p, 'inputs', 520) + place(sack(p), 330, 530) + place(sack(p, 'UREA'), 450, 540, .85) + place(tractor(p), 820, 540) + water(p, 560, 40)


@scene('livestock-fisheries', 'emerald', 'sea')
def _(r, p):
    return (water(p, 500) + on_ground(p, 'live', 470) + place(cow(p), 260, 470, 1.0) + place(cow(p), 470, 480, .8)
            + g(place(fish(p), 760, 540) + place(fish(p, p[2], .8), 900, 570) + place(fish(p, p[7], .7), 1040, 540), cls='wave'))


# Social and health additions
@scene('gender-population', 'rose')
def _(r, p):
    return on_ground(p, 'gender', 530) + place(family(p, r), 400, 530, 1.2) + place(pie(p, [48, 52]), 900, 260, .7) + place(crowd(p, r, 6, 500), 950, 560, .6)


@scene('higher-education', 'royal', 'city')
def _(r, p):
    return on_ground(p, 'higher', 520) + place(school(p), 380, 520, 1.1) + place(grad_cap(p), 860, 220, .9) + place(books(p, r), 900, 520, .8)


@scene('nutrition', 'teal')
def _(r, p):
    return on_ground(p, 'nutri', 530) + place(plate(p), 420, 520, 1.3) + place(family(p, r), 900, 530, .9) + place(crop_field(p, r, 8, 300), 140, 540, .7)



# ---------- Air travel and railways: India-specific motifs ----------

def tricolor(p, w=150, h=100):
    band = h / 3
    flag = rect(0, 0, w, band, '#ff9933') + rect(0, band, w, band, '#ffffff') + rect(0, 2 * band, w, band, '#138808')
    chakra = circle(w / 2, h / 2, band * .38, 'none', ' stroke="#000080" stroke-width="2"') + circle(w / 2, h / 2, 3, '#000080')
    return rect(-5, -10, 6, h + 130, p[5]) + g(flag + chakra, 'translate(0 0)', cls='swing', style='transform-origin:0 0')


def control_tower(p):
    shaft = path('M-24 0 L-14 -260 H14 L24 0Z', p[5])
    cab = path('M-70 -260 H70 L52 -320 H-52Z', p[3], p[6], 3) + rect(-48, -312, 96, 36, p[2], 2, ' opacity=".6"') + rect(-76, -266, 152, 10, p[5])
    return shaft + cab + rect(-3, -380, 6, 60, p[5]) + circle(0, -384, 7, p[6], ' class="pulse"')


def terminal(p, w=520):
    roof = path(f'M{-w / 2} -90 Q{-w / 4} -150 0 -110 Q{w / 4} -70 {w / 2} -130 V-80 H{-w / 2}Z', p[5])
    glass = ''.join(rect(-w / 2 + 10 + i * 40, -78, 30, 60, p[2], 2, ' opacity=".5"') for i in range(int((w - 20) // 40)))
    return roof + rect(-w / 2, -20, w, 20, p[3]) + glass


def india_gate(p):
    out = rect(-110, -40, 220, 40, p[7]) + rect(-90, -230, 180, 190, p[7]) + rect(-110, -250, 220, 20, p[7])
    out += path('M-40 -40 V-130 Q0 -190 40 -130 V-40Z', p[1], extra=' opacity=".8"') + rect(-100, -265, 200, 15, p[7])
    return out + circle(0, -285, 12, p[6], ' class="pulse"')


def vande_bharat(p, cars=3):
    nose = path('M0 -96 H150 Q230 -92 250 -34 V-12 H0Z', '#f4f6f8') + path('M150 -80 Q205 -78 224 -46 H150Z', p[1])
    nose += path('M0 -46 H245', stroke='#ff9933', width=8) + path('M0 -34 H248', stroke='#138808', width=4)
    out = nose
    for i in range(1, cars + 1):
        x = -i * 200
        out += rect(x, -96, 190, 84, '#f4f6f8', 8) + path(f'M{x} -46 H{x + 190}', stroke='#ff9933', width=8) + ''.join(rect(x + 14 + j * 44, -86, 32, 24, p[1], 3, ' opacity=".85"') for j in range(4))
    return out + ''.join(circle(x, -8, 10, '#111') for x in range(-cars * 200 + 30, 240, 52))


def csmt(p):
    out = rect(-260, -120, 520, 120, p[7]) + rect(-70, -250, 140, 130, p[7])
    out += path('M-70 -250 Q-70 -330 0 -380 Q70 -330 70 -250Z', p[7]) + rect(-3, -410, 6, 34, p[7])
    for x in (-200, 200):
        out += rect(x - 40, -190, 80, 70, p[7]) + path(f'M{x - 40} -190 L{x} -250 L{x + 40} -190Z', p[7])
    out += ''.join(path(f'M{x} 0 V-70 Q{x + 18} -96 {x + 36} -70 V0Z', p[1], extra=' opacity=".55"') for x in range(-240, 220, 60))
    return out


def arch_bridge(p, span=640):
    deck = rect(-span / 2, -150, span, 14, p[5])
    arch = path(f'M{-span / 2} -20 Q0 -330 {span / 2} -20', stroke=p[6], width=12)
    ribs = ''.join(path(f'M{x} {f(-150)} V{f(-20 - (1 - (x / (span / 2)) ** 2) * 230 + 20 * 0)}', stroke=p[2], width=2) for x in range(-int(span / 2) + 40, int(span / 2), 40))
    return rect(-span / 2 - 30, -20, 60, 120, p[3]) + rect(span / 2 - 30, -20, 60, 120, p[3]) + arch + deck + ribs


def pylon_line(p, n=5, gap=240):
    out = ''
    for i in range(n):
        x = i * gap
        out += path(f'M{x - 18} 0 L{x} -190 L{x + 18} 0 M{x - 40} -170 H{x + 40}', stroke=p[5], width=4)
    return out + path(f'M-40 -170 Q{n * gap / 2} -140 {(n - 1) * gap + 40} -170', stroke=p[6], width=2)


def signal(p):
    return rect(-4, -220, 8, 220, p[5]) + rect(-22, -260, 44, 90, p[3], 6) + circle(0, -240, 10, '#ef4444', ' class="pulse"') + circle(0, -210, 10, '#22c55e', ' opacity=".4"')


def wagon_row(p, n=5, color=None):
    c = color or p[6]
    return ''.join(rect(-i * 150, -80, 140, 60, c if i % 2 else p[5], 6) + circle(-i * 150 + 30, -12, 10, '#111') + circle(-i * 150 + 110, -12, 10, '#111') for i in range(n))


# Air Travel & Civil Aviation
@scene('air-group', 'saffron', 'city', (1000, 130, 50))
def _(r, p):
    return (on_ground(p, 'air', 520) + place(control_tower(p), 330, 520, .95) + place(terminal(p), 760, 520, .9)
            + place(plane(p), 0, 150, .9) + place(tricolor(p), 1090, 400, .8))


@scene('air-growth', 'gold', 'hills')
def _(r, p):
    return on_ground(p, 'ag', 520) + place(line_chart(p, r, 520), 500, 400, 1) + place(plane(p), 0, 130, .8) + place(india_gate(p), 1010, 520, .6)


@scene('air-global', 'night', 'hills', (200, 110, 30))
def _(r, p):
    return place(globe(p, 170), 600, 300) + place(plane(p), 0, 120, .7) + place(tricolor(p), 960, 420, .8) + on_ground(p, 'agl', 540)


@scene('air-traffic', 'steel', 'city')
def _(r, p):
    return on_ground(p, 'at', 520) + place(terminal(p, 560), 380, 520) + place(pie(p, [81, 19]), 900, 330, .8) + place(plane(p), 0, 140, .7)


@scene('air-airports', 'emerald', 'hills')
def _(r, p):
    return on_ground(p, 'aa', 520) + place(control_tower(p), 300, 520) + place(map_pins(p, r, 7), 860, 400, .9)


@scene('air-cargo', 'dusk', 'city')
def _(r, p):
    return on_ground(p, 'ac', 520) + place(vehicle(p, 'truck'), 400, 520, 1.1) + place(plane(p), 0, 170, .9) + place(bar_chart(p, r, 6, 360, 200), 820, 470, .8)


@scene('air-finance', 'royal', 'city')
def _(r, p):
    return on_ground(p, 'af', 520) + place(coins(p, 5), 330, 520, 1) + place(bar_chart(p, r, 6, 380, 220), 820, 480, .85) + place(plane(p), 0, 150, .7)


# Indian Railways
@scene('rail-group', 'saffron', 'city', (1000, 130, 50))
def _(r, p):
    return on_ground(p, 'rail', 540) + rails(p, 540) + place(csmt(p), 300, 520, .9) + place(vande_bharat(p), 1040, 538, .9, 'drive') + place(tricolor(p), 80, 400, .6)


@scene('rail-network', 'forest', 'mountains')
def _(r, p):
    return on_ground(p, 'rn', 540) + rails(p, 540) + place(arch_bridge(p), 540, 520, .9) + place(train(p, 3), 1000, 538, .8, 'drive')


@scene('rail-passenger', 'gold', 'city')
def _(r, p):
    return on_ground(p, 'rp', 540) + rails(p, 540) + place(csmt(p), 320, 520, .85) + place(crowd(p, r, 8, 540), 760, 540, .8) + place(train(p, 3), 1100, 538, .7, 'drive')


@scene('rail-freight', 'desert', 'hills')
def _(r, p):
    return on_ground(p, 'rf', 540) + rails(p, 540) + place(wagon_row(p, 6), 1000, 538, .9, 'drive') + place(headframe(p), 260, 520, .8)


@scene('rail-fleet', 'steel', 'hills')
def _(r, p):
    return on_ground(p, 'rl', 540) + rails(p, 540) + place(pylon_line(p), 140, 520, 1) + place(vande_bharat(p, 2), 1000, 538, .9, 'drive')


@scene('rail-safety', 'crimson', 'hills')
def _(r, p):
    return on_ground(p, 'rs', 540) + rails(p, 540) + place(signal(p), 330, 520, 1.1) + place(signal(p), 640, 520, .9) + place(train(p, 3), 1050, 538, .8, 'drive')


@scene('rail-finance', 'royal', 'city')
def _(r, p):
    return on_ground(p, 'rfin', 540) + rails(p, 540) + place(coins(p, 5), 320, 520, 1) + place(line_chart(p, r, 460), 820, 400, .9) + place(train(p, 2), 1100, 538, .6, 'drive')


@scene('rail-global', 'night', 'hills', (200, 110, 30))
def _(r, p):
    return place(globe(p, 170), 560, 300) + rails(p, 540) + place(vande_bharat(p, 2), 1060, 538, .8, 'drive') + on_ground(p, 'rg', 548)



# ---------- Waterways, ports and logistics: India-specific motifs ----------

BOX_COLORS = ('#e4572e', '#17bebb', '#ffc914', '#2e86ab', '#76b041', '#f4f6f8', '#ff9933')


def box_stack(p, cols, rows, bw=34, bh=20, seed=0):
    out = ''
    for c in range(cols):
        for rw in range(rows):
            out += rect(c * (bw + 2), -(rw + 1) * (bh + 2), bw, bh, BOX_COLORS[(c * 3 + rw * 2 + seed) % len(BOX_COLORS)], 2)
    return out


def container_ship(p, rows=3, cols=12):
    hull = path('M-290 -34 H290 L250 20 H-250Z', p[5]) + rect(-290, -34, 580, 8, p[6])
    deck = g(box_stack(p, cols, rows), 'translate(-210 -34)')
    bridge_ = rect(-280, -120, 56, 86, '#f4f6f8', 3) + rect(-290, -134, 76, 16, p[3]) + ''.join(rect(-272 + i * 16, -108, 10, 10, p[1]) for i in range(3))
    return hull + deck + bridge_ + rect(-250, -160, 8, 28, p[6]) + smoke_puffs(-246, -164, p[7], 3, 9)


def gantry_crane(p, h=240):
    legs = path(f'M-50 0 V{-h} M50 0 V{-h} M-50 {-h * .5} H50 M-50 0 L50 {-h * .5} M50 0 L-50 {-h * .5}', stroke=p[6], width=7)
    boom = path(f'M-210 {-h} H190 M-210 {-h} L-50 {-h - 60} L190 {-h}', stroke=p[6], width=6)
    trolley = g(rect(-12, -h + 2, 24, 16, p[5], 2) + path(f'M0 {-h + 18} V{-h + 62}', stroke=p[5], width=2) + rect(-14, -h + 62, 28, 12, BOX_COLORS[0], 1),
                cls='scroll', style='animation-duration:9s;animation-direction:alternate;animation-timing-function:ease-in-out')
    return legs + boom + trolley + circle(-50, -h - 60, 5, '#ef4444', ' class="pulse"')


def port_yard(p, n=4):
    return ''.join(g(box_stack(p, 3, 3 - i % 2, seed=i), f'translate({i * 118} 0)') for i in range(n))


def kettuvallam(p):
    hull = path('M-190 -16 Q-170 20 0 22 Q170 20 190 -16 Q150 -4 0 -2 Q-150 -4 -190 -16Z', p[3], p[5], 2)
    roof = path('M-150 -20 Q-150 -112 0 -116 Q150 -112 150 -20Z', '#b8863b') + ''.join(path(f'M{x} -24 Q{x} -92 {x * .8} -108', stroke='#7a5320', width=2) for x in range(-120, 130, 30))
    door = path('M-30 -20 V-60 Q0 -84 30 -60 V-20Z', p[1]) + rect(-150, -26, 300, 8, '#7a5320')
    return roof + door + hull + path('M-190 -16 q-14 -30 4 -44 M190 -16 q14 -30 -4 -44', stroke=p[6], width=4)


def water_metro(p):
    hull = path('M-150 -30 H140 Q170 -26 180 -6 L150 14 H-130Z', '#f4f6f8') + rect(-150, -30, 300, 6, p[6])
    cabin = path('M-120 -30 V-70 Q-118 -84 -100 -84 H90 Q112 -80 120 -30Z', p[6]) + ''.join(rect(-104 + i * 40, -72, 30, 22, p[1], 3, ' opacity=".85"') for i in range(5))
    return hull + cabin + rect(-100, -92, 190, 8, p[5]) + path('M-170 14 q-30 4 -60 10 M-180 24 q-40 4 -70 12', stroke=p[7], width=3, extra=' opacity=".4"')


def dhow(p):
    hull = path('M-150 -30 Q-130 22 0 22 Q120 22 170 -50 L150 -30Z', p[3], p[5], 3) + path('M-150 -30 H150', stroke=p[6], width=5)
    sail = path('M-10 -34 L-90 -50 L40 -250 Q70 -150 90 -52Z', '#f1e3c2') + path('M40 -250 V-34', stroke=p[3], width=4)
    return sail + hull + path('M40 -250 L-130 -30', stroke=p[5], width=3)


def lighthouse(p, h=250):
    tower = path(f'M-34 0 L-20 {-h} H20 L34 0Z', '#f4f6f8') + ''.join(path(f'M{-33 + i * 3} {-i * h / 4 - 20} H{33 - i * 3}', stroke='#e4572e', width=h / 9) for i in range(3))
    lamp = rect(-24, -h - 36, 48, 36, p[2], 3, ' class="pulse"') + path(f'M-32 {-h - 36} H32 L0 {-h - 74}Z', p[5]) + rect(-30, -h - 4, 60, 8, p[5])
    beam = path(f'M0 {-h - 18} L520 {-h - 70} V{-h + 34}Z', p[2], extra=' class="tw" opacity=".25"') + path(f'M0 {-h - 18} L-520 {-h - 70} V{-h + 34}Z', p[2], extra=' class="tw" opacity=".25"')
    return beam + tower + lamp


def gateway_india(p):
    base = rect(-130, -30, 260, 30, '#d7b98a') + rect(-120, -190, 240, 160, '#d7b98a')
    arch = path('M-40 -30 V-110 Q0 -170 40 -110 V-30Z', p[1]) + path('M-120 -190 H120 L106 -206 H-106Z', '#c9a572')
    domes = ''.join(path(f'M{x - 26} -206 Q{x} -250 {x + 26} -206Z', '#c9a572') + rect(x - 3, -262, 6, 14, '#c9a572') for x in (-90, -30, 30, 90))
    cap = path('M-60 -206 Q0 -290 60 -206Z', '#d7b98a')
    return base + arch + domes + cap + ''.join(rect(x, -170, 16, 40, p[1], 2, ' opacity=".6"') for x in (-100, 84))


def howrah_bridge(p, span=720):
    h = 230
    tow = path(f'M{-span / 2} 0 L{-span / 2 + 40} {-h} M{span / 2} 0 L{span / 2 - 40} {-h}', stroke=p[5], width=10)
    truss = path(f'M{-span / 2 - 60} -70 L{-span / 2 + 40} {-h} L0 -120 L{span / 2 - 40} {-h} L{span / 2 + 60} -70', stroke=p[5], width=8)
    web = ''.join(path(f'M{x} -64 L{x + 30} {-120 - 100 * (1 - abs(x) / (span / 2)) ** 1.2}', stroke=p[6], width=2, extra=' opacity=".7"') for x in range(-int(span / 2) + 60, int(span / 2) - 40, 40))
    deck = rect(-span / 2 - 80, -70, span + 160, 14, p[5]) + rect(-span / 2 - 80, -56, span + 160, 6, p[6], 0, ' opacity=".7"')
    return tow + truss + web + deck + g(rect(-span / 2 + 30, -88, 26, 18, '#f4c20d', 2), cls='drive', style='animation-duration:22s')


def ghat(p, n=6):
    out = ''.join(rect(i * 22, -(n - i) * 12, 210 - i * 22 + 10, 12, '#d7b98a' if i % 2 else '#b99668') for i in range(n))
    return out + rect(0, -n * 12 - 80, 40, 80, '#c9a572') + path(f'M-6 {-n * 12 - 80} Q20 {-n * 12 - 126} 46 {-n * 12 - 80}Z', p[6])


def cruise_ship(p):
    hull = path('M-260 -50 H280 L240 20 H-220Z', '#f4f6f8') + rect(-250, -40, 510, 8, p[6])
    decks = ''.join(rect(-220 + i * 12, -50 - (i + 1) * 28, 480 - i * 40, 26, '#f4f6f8', 3) + ''.join(rect(-210 + i * 12 + k * 28, -44 - (i + 1) * 28, 14, 10, p[1], 2, ' opacity=".8"') for k in range(int((460 - i * 40) // 28))) for i in range(3))
    return hull + decks + rect(-30, -190, 40, 34, p[6], 3) + smoke_puffs(-10, -194, p[7], 3, 10)


def ferry(p):
    hull = path('M-130 -24 H130 L104 14 H-110Z', p[6]) + rect(-100, -64, 190, 40, '#f4f6f8', 4) + ''.join(rect(-90 + i * 34, -54, 22, 18, p[1], 3) for i in range(5))
    return hull + rect(-70, -92, 90, 28, p[5], 3) + rect(-2, -120, 4, 28, p[5]) + path('M-60 -90 H10', stroke=p[3], width=3)


def indian_truck(p, color=None):
    c = color or '#e4572e'
    body = rect(-150, -120, 220, 100, '#2e86ab', 4) + ''.join(rect(-150 + i * 44, -120, 6, 100, '#ffc914') for i in range(1, 5))
    body += path('M-150 -108 H70 M-150 -30 H70', stroke='#ffc914', width=5)
    cab = path('M70 -100 H132 L156 -56 V-20 H70Z', c) + rect(96, -92, 30, 26, p[1], 3) + path('M70 -100 H132', stroke='#ffc914', width=5)
    deco = ''.join(path(f'M{x} -122 v-12', stroke='#ff9933', width=4) + circle(x, -136, 5, '#ffc914') for x in range(-130, 60, 28))
    tassels = ''.join(path(f'M{70 + i * 8} -20 v12', stroke='#ef4444', width=3) for i in range(5))
    wheels = ''.join(g(g(circle(0, 0, 18, '#111') + circle(0, 0, 7, p[5]), cls='rot'), f'translate({x} -16)') for x in (-110, -66, 40, 112))
    return body + cab + deco + tassels + wheels + text(-40, -70, 'HORN OK PLEASE', 14, '#ffc914') + tricolor_mini(120, -60)


def tricolor_mini(x, y):
    return rect(x - 9, y - 6, 18, 4, '#ff9933') + rect(x - 9, y - 2, 18, 4, '#ffffff') + rect(x - 9, y + 2, 18, 4, '#138808')


def toll_gantry(p, w=380):
    post = rect(-w / 2, -250, 16, 250, p[5]) + rect(w / 2 - 16, -250, 16, 250, p[5])
    beam = rect(-w / 2, -260, w, 36, '#138808', 4) + text(0, -242, 'NH 48 · TOLL PLAZA', 20, '#ffffff')
    lanes = ''.join(rect(-w / 2 + 40 + i * 90, -200, 52, 26, p[3], 3) + text(-w / 2 + 66 + i * 90, -187, 'FASTag', 11, p[2]) + circle(-w / 2 + 66 + i * 90, -168, 5, '#22c55e', ' class="pulse"') for i in range(4))
    return post + beam + lanes + rect(-w / 2 - 6, -6, w + 12, 8, p[3])


def nh_sign(p):
    return rect(-3, -140, 6, 140, p[5]) + path('M-42 -140 H42 V-196 H-42Z', '#2563eb', p[7], 2) + text(0, -178, 'NH', 18, '#ffffff') + text(0, -156, '44', 22, '#ffffff')


def freight_train(p, n=6):
    loco = path('M0 -96 H110 L130 -60 V-14 H0Z', '#1d4ed8') + rect(80, -86, 28, 24, p[1]) + rect(0, -96, 110, 8, '#ff9933')
    out = loco
    for i in range(1, n + 1):
        x = -i * 150
        out += rect(x, -80, 140, 64, BOX_COLORS[i % 5] if i % 2 else p[5], 4) + path(f'M{x} -50 H{x + 140}', stroke=p[0], width=2, extra=' opacity=".4"')
    return out + ''.join(circle(x, -10, 9, '#111') for x in range(-n * 150 + 20, 130, 46))


def cargo_plane(p):
    body = path('M-190 -50 Q-200 -86 -150 -90 H120 Q200 -90 220 -50 Q200 -14 110 -14 H-150Z', '#f4f6f8') + path('M-190 -50 L-216 -150 H-176 L-130 -88Z', p[6])
    wing = path('M-20 -50 L-70 20 H-10 L60 -50Z', p[5]) + ''.join(path(f'M{x} -50 V-90', stroke=p[3], width=2) for x in range(-100, 100, 40))
    nose = path('M200 -70 Q214 -50 190 -26 L170 -26 L184 -70Z', p[3]) + rect(150, -76, 26, 18, p[1], 3)
    ramp = path('M-120 -14 H-60 V-86 H-120Z', p[3], extra=' opacity=".4"')
    return body + ramp + wing + nose + circle(-10, 4, 14, p[3]) + circle(100, -6, 8, '#111') + circle(-120, -6, 8, '#111')


def india_map(p, s=1.0):
    d = ('M-20 -340 L25 -335 L45 -300 L40 -270 L90 -255 L150 -245 L140 -215 L100 -210 L85 -190 L60 -185 L40 -150 L30 -110 L5 -40 '
         'L-15 0 L-35 -50 L-60 -110 L-95 -150 L-110 -195 L-100 -230 L-135 -250 L-125 -280 L-70 -290 L-40 -310Z')
    return g(path(d, p[3], p[6], 3, ' opacity=".95"'), f'scale({f(s)})')


CITIES = {'DEL': (-25, -270), 'MUM': (-90, -170), 'KOL': (60, -200), 'CHE': (0, -60), 'BLR': (-30, -80), 'HYD': (-25, -135), 'AMD': (-95, -215), 'GAU': (115, -230)}


def route_net(p, pairs, color=None, cls='flow'):
    out = ''
    for a, b in pairs:
        (x1, y1), (x2, y2) = CITIES[a], CITIES[b]
        out += path(f'M{x1} {y1} Q{f((x1 + x2) / 2)} {f(min(y1, y2) - 60)} {x2} {y2}', stroke=color or p[2], width=2.5, extra=f' class="{cls}" opacity=".85"')
    return out + ''.join(circle(x, y, 6, p[6], ' class="pulse"') for x, y in CITIES.values())


def modal_icons(p):
    return (place(vehicle(p, 'truck'), -230, 0, .55) + place(wagon_row(p, 2), 30, 0, .45) + place(container_ship(p, 2, 5), 290, 20, .3)
            + place(cargo_plane(p), 520, 0, .3))


def rupee_bars(p, rng):
    return place(coins(p, 5), 0, 0, .9) + place(bar_chart(p, rng, 6, 360, 220), 340, -10, .8)


# Water transport
@scene('water-group', 'ocean', 'sea', (900, 120, 50))
def _(r, p):
    return (water(p, 440) + place(lighthouse(p), 130, 450, .9) + g(place(container_ship(p), 520, 450, .8), cls='bob')
            + g(place(dhow(p), 930, 470, .6), cls='bob', style=delay(-2)) + place(tricolor(p), 1100, 380, .7))


@scene('water-ports', 'steel', 'city')
def _(r, p):
    return (on_ground(p, 'wp', 500) + water(p, 520, 80) + place(gantry_crane(p), 250, 500) + place(gantry_crane(p, 200), 450, 500, .9)
            + place(port_yard(p), 640, 500) + g(place(container_ship(p, 3, 8), 300, 540, .6), cls='bob'))


@scene('water-inland', 'forest', 'hills')
def _(r, p):
    return (water(p, 440) + place(howrah_bridge(p), 520, 440, .8) + place(ghat(p), 940, 470, 1) + g(place(ferry(p), 200, 490, .7), cls='bob')
            + place(tricolor(p), 1130, 330, .6))


@scene('water-coastal', 'dusk', 'sea', (300, 150, 60))
def _(r, p):
    return (water(p, 450) + place(lighthouse(p, 280), 1000, 460) + place(gateway_india(p), 280, 460, .85) + g(place(dhow(p), 650, 480, .65), cls='bob'))


@scene('water-passenger', 'teal', 'sea', (1000, 130, 50))
def _(r, p):
    return (water(p, 440) + g(place(kettuvallam(p), 280, 475, .9), cls='bob') + g(place(water_metro(p), 700, 485, .9), cls='bob', style=delay(-3))
            + place(crowd(p, r, 4, 160), 1060, 440, .5) + place(ferry(p), 1050, 500, .5))


@scene('water-container', 'night', 'sea', (200, 110, 30))
def _(r, p):
    return (water(p, 450) + g(place(container_ship(p, 4, 14), 560, 470, 1.05), cls='bob') + place(gantry_crane(p, 220), 1060, 450, .8)
            + place(port_yard(p, 2), 960, 450, .6))


@scene('water-global', 'night', 'sea', (200, 110, 30))
def _(r, p):
    return place(globe(p, 170), 600, 300) + water(p, 480) + g(place(cruise_ship(p), 250, 500, .55), cls='bob') + g(place(container_ship(p), 950, 500, .5), cls='bob', style=delay(-2))


# Logistics
@scene('logistics-group', 'saffron', 'city', (1000, 130, 50))
def _(r, p):
    return (on_ground(p, 'lg', 520) + road(p, 520) + g(place(indian_truck(p), 300, 556, .9), cls='drive') + place(india_map(p), 900, 520, .9)
            + place(route_net(p, [('DEL', 'MUM'), ('DEL', 'KOL'), ('MUM', 'CHE')]), 900, 520, .9) + g(place(cargo_plane(p), 0, 150, .5), cls='fly'))


@scene('logistics-road', 'desert', 'hills')
def _(r, p):
    return (on_ground(p, 'lr', 500) + road(p, 520) + place(toll_gantry(p), 560, 520, .9) + place(nh_sign(p), 130, 520) + g(place(indian_truck(p, '#138808'), 200, 556, .85), cls='drive')
            + g(place(indian_truck(p), 200, 556, .75), cls='drive-r', style=delay(-6)))


@scene('logistics-rail', 'steel', 'hills')
def _(r, p):
    return on_ground(p, 'lrl', 540) + rails(p, 540) + place(pylon_line(p, 6, 220), 60, 520) + g(place(freight_train(p, 7), 900, 538, .85), cls='drive')


@scene('logistics-sea', 'ocean', 'sea')
def _(r, p):
    return (water(p, 460) + place(gantry_crane(p), 220, 460, .9) + place(port_yard(p, 2), 330, 460, .8) + g(place(container_ship(p, 3, 10), 760, 480, .85), cls='bob')
            + place(lighthouse(p, 200), 1130, 460, .6))


@scene('logistics-air', 'dusk', 'city')
def _(r, p):
    return (on_ground(p, 'la', 500) + place(control_tower(p), 220, 520, .9) + place(cargo_plane(p), 700, 520, .85) + place(vehicle(p, 'truck'), 1050, 540, .6)
            + g(place(jet(p), 0, 130, .6), cls='fly'))


@scene('logistics-modal', 'emerald', 'hills')
def _(r, p):
    return (on_ground(p, 'lm', 500) + place(india_map(p, 1.15), 420, 540) + place(route_net(p, [('DEL', 'MUM'), ('DEL', 'KOL'), ('MUM', 'CHE'), ('KOL', 'CHE'), ('DEL', 'GAU'), ('HYD', 'AMD')]), 420, 540, 1.15)
            + place(modal_icons(p), 740, 540, .55) + place(tricolor(p), 1130, 380, .6))


@scene('logistics-revenue', 'gold', 'city')
def _(r, p):
    return on_ground(p, 'lv', 520) + place(rupee_bars(p, r), 280, 520, 1) + place(freight_train(p, 4), 1050, 538, .55, 'drive') + place(line_chart(p, r, 420), 820, 250, .6)


# Dashboard expansion scenes
@scene('air-airports-top', 'emerald', 'city')
def _(r, p):
    return on_ground(p, 'aat', 520) + place(terminal(p, 560), 330, 520) + place(control_tower(p), 760, 520, .85) + place(bar_chart(p, r, 6, 300, 200), 960, 470, .6) + place(tricolor(p), 1130, 420, .6)


@scene('rail-zones', 'forest', 'hills')
def _(r, p):
    return on_ground(p, 'rz', 540) + rails(p, 540) + place(india_map(p, 1.2), 280, 520) + place(route_net(p, [('DEL', 'KOL'), ('DEL', 'MUM'), ('MUM', 'CHE'), ('KOL', 'CHE')]), 280, 520, 1.2) + place(vande_bharat(p, 2), 1000, 538, .8, 'drive')


@scene('rail-electrification', 'gold', 'hills', (1000, 130, 50))
def _(r, p):
    return on_ground(p, 're', 540) + rails(p, 540) + place(pylon_line(p, 6, 200), 80, 520, 1.05) + place(vande_bharat(p, 2), 900, 538, .85, 'drive') + place(tricolor(p), 1130, 410, .6)


@scene('air-routes', 'night', 'hills', (200, 110, 30))
def _(r, p):
    return (place(india_map(p, 1.2), 600, 560) + place(route_net(p, [('DEL', 'MUM'), ('DEL', 'KOL'), ('DEL', 'BLR'), ('MUM', 'CHE'), ('KOL', 'HYD'), ('GAU', 'DEL'), ('AMD', 'BLR')]), 600, 560, 1.2)
            + place(plane(p), 0, 130, .7) + on_ground(p, 'ar', 570))


def catalog_artwork():
    catalog_path = ROOT / 'data' / 'catalog.json'
    if not catalog_path.exists():
        return {}, set()
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    labels, files = {}, set()
    for category in catalog.get('categories', []):
        filename = str(category.get('art', '')).split('?', 1)[0].strip()
        if filename:
            files.add(filename)
            labels.setdefault(filename, category.get('name', 'India'))
        for subgroup in category.get('subgroups', []):
            filename = str(subgroup.get('art', '')).split('?', 1)[0].strip()
            if filename:
                files.add(filename)
                labels.setdefault(filename, subgroup.get('name', category.get('name', 'India')))
    return labels, files


def fallback_scene(uid, label):
    topic = f'{uid} {label}'.lower()
    if any(word in topic for word in ('election', 'ballot', 'evm', 'voter', 'vote', 'lok sabha', ' sir', ' ssr', 'sir-', 'ssr-')):
        pal, backdrop = 'saffron', 'city'
        def fg(r, p):
            hand = (circle(0, -135, 44, '#d9a178') + rect(-20, -270, 40, 168, '#d9a178', 18)
                    + path('M-16 -230 Q0 -255 16 -230', stroke='#5c2618', width=8) + circle(0, -255, 7, '#21130d'))
            return (on_ground(p, uid, 510) + place(evm(p), 310, 520, .9) + place(ballot_box(p), 800, 520, .8)
                    + place(hand, 1040, 490, .8) + place(tricolor(p), 105, 360, .48))
    elif any(word in topic for word in ('budget', 'fiscal', 'capital', 'markets', 'income', 'wealth')):
        pal, backdrop = 'gold', 'city'
        def fg(r, p):
            case = (rect(-155, -80, 310, 150, '#5b3a24', 22, ' stroke="#d5a856" stroke-width="8"')
                    + rect(-70, -118, 140, 45, 'none', 10, ' stroke="#d5a856" stroke-width="12"')
                    + circle(0, -6, 34, '#facc15') + text(0, -6, '₹', 38, '#32210e'))
            ribbons = ''.join(path(f'M{-500+i*170} {-235+i*45} C{-300+i*120} {-310-i*20} {100+i*70} {-40+i*22} {500-i*100} {-175+i*30}',
                                   stroke=(p[6], p[2], p[7])[i % 3], width=5, extra=' opacity=".8" class="flow"') for i in range(5))
            return (on_ground(p, uid, 520) + place(bank(p), 220, 520, .6) + place(case, 650, 520, 1.15)
                    + place(coins(p, 5), 980, 510, .7) + ribbons)
    elif any(word in topic for word in ('epic', 'ramayana', 'mahabharata', 'journey', 'myth', 'geography')):
        pal, backdrop = 'crimson', 'mountains'
        def fg(r, p):
            bow = path('M-145 -250 Q-15 -90 125 -250 M-145 -250 Q-18 -414 125 -250', stroke=p[6], width=8)
            arrow = path('M-190 -250 H180 M145 -263 L180 -250 L145 -237', stroke=p[7], width=5)
            chariot = (path('M-150 -90 H100 L60 -185 H-80Z', '#b77736', '#f4d28a', 5)
                       + circle(-80, -70, 38, '#21130d', ' stroke="#d5a856" stroke-width="7"')
                       + circle(55, -70, 38, '#21130d', ' stroke="#d5a856" stroke-width="7"')
                       + path('M-175 -195 Q-225 -240 -265 -180 M-265 -180 L-220 -160', stroke=p[7], width=8))
            river = ''.join(path(f'M{-520+i*95} {-60+i*26} Q{-150+i*90} {-140+i*24} {500-i*50} {-25+i*18}', stroke=(p[6], p[2])[i%2], width=3, extra=' opacity=".65"') for i in range(5))
            return (on_ground(p, uid, 520) + place(mountains(r, 480, 150, p[3], p[7], .65), 0, 530, 1)
                    + place(temple(p), 300, 520, .8) + place(chariot, 720, 520, .88) + place(bow + arrow, 1000, 340, .75) + river)
    elif any(word in topic for word in ('buddha', 'buddhist', 'stupa')):
        pal, backdrop = 'saffron', 'mountains'
        def fg(r, p):
            leaves = ''.join(path(f'M{x} {-330-i*20} q-50 -40 -15 -88 q48 20 15 88Z', p[6], extra=f' opacity="{.55+i*.1}"') for i, x in enumerate((-180, -80, 25, 115, 205)))
            petals = ''.join(path(f'M0 -42 Q{x} -125 {x*1.35} -50 Q{x} -8 0 0Z', p[6], extra=' opacity=".85"') for x in (-48, -24, 24, 48))
            return (on_ground(p, uid, 525) + place(stupa(p), 620, 520, 1.25) + place(temple(p), 250, 520, .7)
                    + leaves + place(petals + circle(0, -48, 12, p[2]), 950, 490, .75))
    elif any(word in topic for word in ('sikh', 'harmandir', 'golden temple')):
        pal, backdrop = 'royal', 'sea'
        def fg(r, p):
            shrine = (rect(-190, -120, 380, 120, '#d3a847', 4, ' stroke="#fff0bb" stroke-width="5"')
                      + path('M-190 -120 Q-175 -200 -90 -180 Q-55 -255 0 -190 Q55 -255 90 -180 Q175 -200 190 -120Z', '#e3bd65', '#fff0bb', 5)
                      + circle(0, -212, 19, '#fff0bb') + rect(-25, -40, 50, 40, '#1d2345'))
            reflection = ''.join(path(f'M{-200+i*34} {10+i*8} q22 -18 44 0 t44 0', stroke=p[6], width=3, extra=' opacity=".75"') for i in range(13))
            return water(p, 455, 160) + place(shrine, 610, 480, 1.15) + place(reflection, 610, 500, 1.05) + place(temple(p), 250, 500, .55)
    elif any(word in topic for word in ('veda', 'scripture', 'manuscript', 'verse', 'upanishad')):
        pal, backdrop = 'desert', 'hills'
        def fg(r, p):
            flame = path('M0 0 Q-100 -75 -15 -230 Q-5 -145 25 -100 Q75 -210 96 -148 Q125 -66 0 0Z', '#ff8b38', '#ffd77b', 5)
            altar = path('M-150 0 L-105 -120 H105 L150 0Z', '#9d5930', '#edbd76', 6)
            leaves = ''.join(rect(-190, -150+i*28, 380, 22, '#b98749', 3, ' stroke="#f2d69a" stroke-width="2"') + path(f'M-160 {-139+i*28} H150', stroke='#6d4029', width=2) for i in range(5))
            return on_ground(p, uid, 520) + place(altar + flame, 320, 520, .85) + place(leaves, 850, 500, .78) + place(books(p, r), 180, 520, .35)
    elif any(word in topic for word in ('map', 'atlas', 'geography', 'state')):
        pal, backdrop = 'teal', 'mountains'
        def fg(r, p):
            contours = ''.join(circle(0, 0, 185+i*26, 'none', f' stroke="{p[6]}" stroke-width="2" opacity=".4"') for i in range(5))
            compass = circle(0, 0, 70, 'none', f' stroke="{p[7]}" stroke-width="3"') + path('M0 -62 L20 0 L0 62 L-20 0Z', p[6])
            return (place(contours, 600, 330, .9) + place(india_map(p, 1.35), 610, 550, 1.0)
                    + place(route_net(p, [('DEL', 'MUM'), ('DEL', 'KOL'), ('MUM', 'CHE'), ('KOL', 'CHE'), ('GAU', 'DEL')]), 610, 550, 1.25)
                    + place(compass, 1010, 210, .55) + on_ground(p, uid, 565))
    elif any(word in topic for word in ('cricket', 'football', 'hockey', 'sport', 'athlet', 'trophy', 'racket', 'chess', 'kabaddi')):
        pal, backdrop = 'night', 'city'
        def fg(r, p):
            stands = path('M-590 -40 Q-510 -245 -300 -280 H300 Q510 -245 590 -40Z', p[3], p[6], 4)
            seats = ''.join(circle(x, y, 4, p[2], ' opacity=".8"') for y in range(-235, -55, 22) for x in range(-470, 500, 32) if (x+y)%3)
            beams = ''.join(path(f'M{x} -380 L{x+180} -78', stroke=p[2], width=3, extra=' opacity=".2"') for x in (-320, 40, 390))
            field = path('M-470 0 Q0 -125 470 0Z', '#226341', '#8ee2a6', 4)
            game = (path('M-220 -4 V-120 H-100 V-4 M100 -4 V-120 H220 V-4', stroke=p[7], width=8)
                    + circle(0, -72, 12, '#f3f5dc') + path('M-5 -70 l18 -14', stroke=p[6], width=4))
            floodlights = ''.join(g(rect(-12, -330, 24, 270, p[5]) + circle(0, -340, 26, p[2], ' class="pulse"'), f'translate({x} 0)') for x in (-420, 420))
            return on_ground(p, uid, 525) + place(stands + seats + beams, 600, 520, .9) + place(field + game, 600, 520, .95) + place(floodlights, 600, 500, .8)
    elif any(word in topic for word in ('court', 'judiciary', 'law', 'justice')):
        pal, backdrop = 'royal', 'city'
        def fg(r, p):
            courthouse = (path('M-270 -245 L0 -380 L270 -245Z', p[5], p[6], 5) + rect(-270, -245, 540, 25, p[6])
                         + ''.join(rect(-215+i*86, -220, 28, 205, p[5], 5) for i in range(6)) + rect(-285, -15, 570, 20, p[6]))
            return on_ground(p, uid, 520) + place(courthouse, 550, 520, .9) + place(scales(p), 950, 410, .65)
    else:
        pal, backdrop = 'saffron', 'city'
        def fg(r, p):
            return (on_ground(p, uid, 525) + place(bank(p), 300, 520, .8) + place(line_chart(p, r, 440), 820, 400, .75)
                    + place(tricolor(p), 1080, 380, .6))
    return pal, backdrop, fg


def main():
    for d in OUTPUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
    labels, artwork_files = catalog_artwork()
    names = set(SCENES) | {Path(filename).stem for filename in artwork_files}
    for name in sorted(names):
        filename = f'{name}.svg'
        label = labels.get(filename, name.replace('-', ' ').title())
        if name in SCENES:
            pal, backdrop, fn, sun = SCENES[name]
        else:
            pal, backdrop, fn = fallback_scene(name, label)
            sun = (980, 130, 46)
        svg = build(name, pal, backdrop, fn, sun, label)
        for d in OUTPUT_DIRS:
            (d / filename).write_text(svg, encoding='utf-8')
    print(f'Generated {len(names)} scenes into {", ".join(str(d.relative_to(ROOT)) for d in OUTPUT_DIRS)}')
    for d in OUTPUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
    for name, (pal, backdrop, fn, sun) in SCENES.items():
        svg = build(name, pal, backdrop, fn, sun)
        for d in OUTPUT_DIRS:
            (d / f'{name}.svg').write_text(svg, encoding='utf-8')
    print(f'Generated {len(SCENES)} scenes into {", ".join(str(d.relative_to(ROOT)) for d in OUTPUT_DIRS)}')


if __name__ == '__main__':
    main()
