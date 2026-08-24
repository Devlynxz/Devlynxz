# -*- coding: utf-8 -*-
"""Generates the animated monochrome profile hero (dark + light) as pure SVG/SMIL."""
import math
import os
import random

# --------------------------------------------------------------------------
# ASCII portrait
# --------------------------------------------------------------------------
AW, AH = 38, 20
RAMP = " .`:;+*oO#@"


def _norm(v):
    x, y, z = v
    l = math.sqrt(x * x + y * y + z * z) or 1.0
    return (x / l, y / l, z / l)


LIGHT_DIR = _norm((-0.55, -0.75, 0.75))


def _shade(nx, ny, nz):
    d = max(0.0, nx * LIGHT_DIR[0] + ny * LIGHT_DIR[1] + nz * LIGHT_DIR[2])
    return 0.34 + 0.66 * (d ** 0.8)


def _ramp(b):
    idx = int(b * (len(RAMP) - 1) + 0.5)
    return RAMP[max(0, min(len(RAMP) - 1, idx))]


def build_ascii():
    rows = []
    for j in range(AH):
        line = []
        v = (j + 0.5) / AH * 2 - 1
        for i in range(AW):
            u = (i + 0.5) / AW * 2 - 1
            ch = " "

            hx, hy = (u - 0.02) / 0.40, (v + 0.34) / 0.52
            r2 = hx * hx + hy * hy
            if r2 <= 1.0:
                nz = math.sqrt(max(0.0, 1.0 - r2))
                b = _shade(hx, hy, nz)
                for ex in (-0.16, 0.20):
                    if abs(u - ex) < 0.075 and abs(v + 0.40) < 0.055:
                        b = 0.06
                if abs(v + 0.50) < 0.03 and abs(u - 0.02) < 0.26:
                    b *= 0.55
                if abs(v + 0.10) < 0.035 and abs(u - 0.02) < 0.13:
                    b *= 0.45
                ch = _ramp(b)

            if ch == " " and 0.10 < v <= 0.42:
                nxu = (u - 0.02) / 0.20
                if abs(nxu) <= 1.0:
                    nz = math.sqrt(max(0.0, 1.0 - nxu * nxu))
                    ch = _ramp(_shade(nxu, 0.10, nz) * 0.66)

            if ch == " " and v > 0.40:
                sx = (u - 0.02) / (0.46 + 0.62 * (v - 0.40))
                if abs(sx) <= 1.0:
                    nz = math.sqrt(max(0.0, 1.0 - sx * sx))
                    ch = _ramp(_shade(sx * 0.95, -0.28, nz) * 0.86)

            line.append(ch)
        rows.append("".join(line))
    return rows


try:
    # ASCII derived from the real photo (photo_to_ascii.py)
    from portrait import PORTRAIT as ASCII_ROWS, COLS as AW, ROWS as AH, DARK
except ImportError:
    ASCII_ROWS = build_ascii()
    DARK = None


# --------------------------------------------------------------------------
# Pixel cat
# --------------------------------------------------------------------------
# Sits to the right of the name. '#' fur, ':' shade, '^' inner ear + nose,
# 'o' eye, '.' transparent. Rows 0-1 are the ears and are drawn separately so
# they can twitch; the tail is not in the grid at all for the same reason.
CAT = [
    "...##........##.....",
    "..#^##......##^#....",
    "..##############....",
    ".################...",
    ".###oo######oo###...",
    ".###oo######oo###...",
    ".#######^^#######...",
    ".######::::######...",
    "..##############....",
    "...############.....",
    "...####::::####.....",
    "...####::::####.....",
    "...####::::####.....",
    "..#####::::#####....",
    "..#####::::#####....",
    "..##############....",
    "...############.....",
    "...####::::####.....",
]

CAT_TAIL = [(16, 14), (17, 14), (18, 13), (19, 12), (19, 11), (18, 10), (17, 10)]
CAT_EYES = ((4, 4), (12, 4))          # top-left of each 2x2 eye
CAT_EAR_SPLIT = 9                     # column that divides left ear from right


def cat_runs(row):
    """Merge horizontal runs of one glyph so each becomes a single rect."""
    runs = []
    for i, ch in enumerate(row):
        if ch == ".":
            continue
        if runs and runs[-1][0] == ch and runs[-1][2] == i:
            runs[-1][2] = i + 1
        else:
            runs.append([ch, i, i + 1])
    return runs


def ascii_runs(row):
    """Split a row into (is_shadow, text) runs.

    The quantised shadow glyphs carry the silhouette but must not compete
    with the face, so they get their own dimmer fill rather than sharing the
    accent gradient with the lit areas.
    """
    runs = []
    for ch in row:
        shadow = (ch == DARK or ch == " ")
        if runs and runs[-1][0] == shadow:
            runs[-1][1].append(ch)
        else:
            runs.append((shadow, [ch]))
    return [(s, "".join(cs)) for s, cs in runs]

# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------
NAME = "Erlyn Quimson"
HANDLE = "Devlynxz"
TERM_TITLE = "devlynxz@github  —  ~/profile"

ROLES = [
    "Developer",
    "React + FastAPI Developer",
    "Flutter App Developer",
    "Product-Minded Builder",
    "Ships Real Projects",
]

# Keep these rows about the craft, never the workplace — no employer, team,
# client, project or location names. The banner is public on the profile.
INFO = [
    ("FOCUS", "React · FastAPI · Flutter · PostgreSQL"),
    ("EXPLORING", "System design · Clean architecture · DX"),
    ("CRAFT", "Idea → shipped, one commit at a time"),
    ("GITHUB", "github.com/Devlynxz"),
    ("EMAIL", "erlynquimson@gmail.com"),
]

SKILLS = [
    "JavaScript", "React", "Tailwind", "Flutter", "Dart", "Python",
    "FastAPI", "Node.js", "Angular", "PHP", "PostgreSQL", "Firebase", "Git",
]

# --------------------------------------------------------------------------
# Geometry
# --------------------------------------------------------------------------
CW, CH = 1180, 610
CARD = (10, 10, 1160, 590, 26)

LX, LY, LW, LH = 34, 34, 452, 542
RX, RY, RW, RH = 502, 34, 644, 542

CX = RX + 34            # right-panel content left edge  -> 536
CR = RX + RW - 34       # right-panel content right edge -> 1112
CWD = CR - CX           # 576

# The cat sits in the gap between the end of the name (~x832 worst case at
# 38px bold) and the panel's right edge, vertically between the header rule
# (y82) and the rule under the roles (y258).
CAT_PX = 8.0
CAT_X, CAT_Y = 935.0, 92.0

ASCII_X = 49
ASCII_Y0 = 110
ASCII_LH = 14.8
ASCII_FS = 12.6
ASCII_CLIP_W = 440
ASCII_STAGGER = 0.062

ROLE_FS = 16
ROLE_CH = 9.6
ROLE_X = CX + 26
ROLE_BASE = 234
LOOP = 21.0
SLOT = LOOP / len(ROLES)

# --------------------------------------------------------------------------
# Themes
# --------------------------------------------------------------------------
THEMES = {
    "dark": dict(
        bg0="#050505", bg1="#0B0B0C", bg2="#101012",
        panel="#0D0D0E", panel2="#121214",
        stroke="rgba(255,255,255,.075)", stroke2="rgba(255,255,255,.14)",
        text="#FAFAFA", muted="#8B8B92", dim="#55555C",
        gA="#FFFFFF", gB="#C2C2C8", gC="#6E6E76",
        glow="#FFFFFF", glowOp=".30", glowStd="2.6", asciiGlowOp=".34", asciiDim="#2E2E33",
        blobOp=".16", blob="#FFFFFF",
        scanOp=".16", noiseOp=".055",
        pillFill="rgba(255,255,255,.045)", pillStroke="rgba(255,255,255,.13)",
        shimmerOp=".85", partOp=".5", dotFill="rgba(255,255,255,.16)",
        glassOp=".05",
    ),
    "light": dict(
        bg0="#FFFFFF", bg1="#F6F6F7", bg2="#EFEFF1",
        panel="#FBFBFC", panel2="#F4F4F5",
        stroke="rgba(9,9,11,.09)", stroke2="rgba(9,9,11,.18)",
        text="#09090B", muted="#5A5A62", dim="#9A9AA2",
        gA="#09090B", gB="#3F3F46", gC="#8A8A93",
        glow="#09090B", glowOp=".13", glowStd="2.2", asciiGlowOp=".16", asciiDim="#D2D2D8",
        blobOp=".07", blob="#09090B",
        scanOp=".05", noiseOp=".035",
        pillFill="rgba(9,9,11,.035)", pillStroke="rgba(9,9,11,.11)",
        shimmerOp=".45", partOp=".28", dotFill="rgba(9,9,11,.16)",
        glassOp=".55",
    ),
}

MONO = "ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace"
SANS = "ui-sans-serif,-apple-system,BlinkMacSystemFont,Segoe UI,Inter,Helvetica,Arial,sans-serif"


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def f(x):
    return ("%.4f" % x).rstrip("0").rstrip(".")


# --------------------------------------------------------------------------
# Pill packing
# --------------------------------------------------------------------------
def pack_pills():
    fs, pad, gap = 11.5, 13.0, 8.0
    rows, cur, curw = [], [], 0.0
    for s in SKILLS:
        tw = len(s) * fs * 0.585
        w = tw + pad * 2
        if cur and curw + gap + w > CWD:
            rows.append((cur, curw))
            cur, curw = [], 0.0
        curw += (gap if cur else 0) + w
        cur.append((s, w, tw))
    if cur:
        rows.append((cur, curw))
    return rows, fs


# --------------------------------------------------------------------------
# Cat rendering
# --------------------------------------------------------------------------
def cat_group(T):
    """The pixel cat beside the name.

    Split into nested groups because each part moves on its own clock: the
    whole cat rides a slow bob, the tail swings from its base, the ears twitch
    about the point where they meet the skull, and the lids drop over the eyes.
    Rotating a part inside the bob keeps the two transforms from fighting.
    """
    px = CAT_PX
    ink = {"#": T["text"], ":": T["muted"], "^": T["dim"], "o": T["panel"]}
    o = []
    a = o.append

    def rect(cx0, cy0, w, h, fill):
        a('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>'
          % (f(CAT_X + cx0 * px), f(CAT_Y + cy0 * px), f(w * px), f(h * px), fill))

    def spin(vals, cx0, cy0, dur, keytimes=None):
        cx, cy = f(CAT_X + cx0 * px), f(CAT_Y + cy0 * px)
        kt = ' keyTimes="%s"' % keytimes if keytimes else ""
        return ('<animateTransform attributeName="transform" type="rotate" '
                'values="%s"%s dur="%ss" repeatCount="indefinite"/>'
                % (";".join("%s %s %s" % (f(v), cx, cy) for v in vals), kt, f(dur)))

    # arrives just after the name lands
    a('<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".6s" '
      'begin="1.05s" fill="freeze"/>')

    # ground shadow — tightens as the cat lifts, so the bob reads as weight
    a('<ellipse cx="%s" cy="%s" ry="%s" fill="%s" opacity=".16">'
      '<animate attributeName="rx" values="%s;%s;%s" dur="3.2s" '
      'repeatCount="indefinite" calcMode="spline" '
      'keySplines=".4 0 .6 1;.4 0 .6 1"/></ellipse>'
      % (f(CAT_X + 8.5 * px), f(CAT_Y + 18.7 * px), f(1.05 * px), T["dim"],
         f(6.4 * px), f(5.3 * px), f(6.4 * px)))

    a('<g filter="url(#asciiGlow)">')
    a('<g><animateTransform attributeName="transform" type="translate" '
      'values="0 0;0 -4;0 0" dur="3.2s" repeatCount="indefinite" '
      'calcMode="spline" keySplines=".4 0 .6 1;.4 0 .6 1"/>')

    # tail — drawn first so it sits behind the body
    a('<g>' + spin((-9, 10, -9), 16, 14.5, 1.9))
    for (cx0, cy0) in CAT_TAIL:
        rect(cx0, cy0, 1, 1, T["text"])
    a('</g>')

    # ears, each on its own clock so the twitches never sync up
    for c0, c1, ox, dur in ((0, CAT_EAR_SPLIT, 3.5, 5.0),
                            (CAT_EAR_SPLIT, len(CAT[0]), 14.0, 6.3)):
        a('<g>' + spin((0, 0, -8, 6, 0, 0), ox, 2, dur,
                       keytimes="0;.72;.78;.84;.9;1"))
        for j in (0, 1):
            for ch, i0, i1 in cat_runs(CAT[j][c0:c1]):
                rect(c0 + i0, j, i1 - i0, 1, ink[ch])
        a('</g>')

    # head + body (ear rows already drawn above)
    for j, row in enumerate(CAT):
        if j < 2:
            continue
        for ch, i0, i1 in cat_runs(row):
            rect(i0, j, i1 - i0, 1, ink[ch])

    # blink — fur-coloured lids dropped over the eyes for a few frames
    for (ex, ey) in CAT_EYES:
        a('<g opacity="0"><animate attributeName="opacity" values="0;1;0" '
          'keyTimes="0;.94;.97" calcMode="discrete" dur="4.4s" '
          'repeatCount="indefinite"/>')
        rect(ex, ey, 2, 2, T["text"])
        a('</g>')

    a('</g></g></g>')
    return "".join(o)


# --------------------------------------------------------------------------
# SVG
# --------------------------------------------------------------------------
def build(theme_name):
    T = THEMES[theme_name]
    o = []
    a = o.append

    a('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
      'viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
      'aria-label="%s — %s profile banner">' % (CW, CH, CW, CH, esc(NAME), theme_name))

    # ---------------- defs ----------------
    a('<defs>')

    a('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
      '<stop offset="0" stop-color="%(bg0)s"/><stop offset=".55" stop-color="%(bg1)s"/>'
      '<stop offset="1" stop-color="%(bg2)s"/></linearGradient>' % T)

    a('<linearGradient id="panel" x1="0" y1="0" x2=".4" y2="1">'
      '<stop offset="0" stop-color="%(panel2)s"/><stop offset="1" stop-color="%(panel)s"/>'
      '</linearGradient>' % T)

    # animated accent gradient (ASCII + name)
    a('<linearGradient id="accent" gradientUnits="userSpaceOnUse" spreadMethod="reflect" '
      'x1="0" y1="0" x2="300" y2="220">'
      '<stop offset="0" stop-color="%(gA)s"/><stop offset=".45" stop-color="%(gB)s"/>'
      '<stop offset="1" stop-color="%(gC)s"/>'
      '<animateTransform attributeName="gradientTransform" type="translate" '
      'values="-170 -60;170 60;-170 -60" dur="9s" repeatCount="indefinite"/>'
      '</linearGradient>' % T)

    a('<linearGradient id="accent2" gradientUnits="userSpaceOnUse" spreadMethod="reflect" '
      'x1="480" y1="170" x2="900" y2="215">'
      '<stop offset="0" stop-color="%(gA)s"/><stop offset=".5" stop-color="%(gB)s"/>'
      '<stop offset="1" stop-color="%(gC)s"/>'
      '<animateTransform attributeName="gradientTransform" type="translate" '
      'values="-220 0;220 0;-220 0" dur="11s" repeatCount="indefinite"/>'
      '</linearGradient>' % T)

    # border shimmer
    a('<linearGradient id="shimmer" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="420" y2="0">'
      '<stop offset="0" stop-color="%(glow)s" stop-opacity="0"/>'
      '<stop offset=".5" stop-color="%(glow)s" stop-opacity="%(shimmerOp)s"/>'
      '<stop offset="1" stop-color="%(glow)s" stop-opacity="0"/>'
      '<animateTransform attributeName="gradientTransform" type="translate" '
      'values="-460 0;1220 0" dur="7s" repeatCount="indefinite"/>'
      '</linearGradient>' % T)

    # glass reflection + scanline
    a('<linearGradient id="glass" x1="0" y1="0" x2=".35" y2="1">'
      '<stop offset="0" stop-color="#FFFFFF" stop-opacity="%(glassOp)s"/>'
      '<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>' % T)

    a('<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0" stop-color="%(glow)s" stop-opacity="0"/>'
      '<stop offset=".5" stop-color="%(glow)s" stop-opacity="%(scanOp)s"/>'
      '<stop offset="1" stop-color="%(glow)s" stop-opacity="0"/></linearGradient>' % T)

    for i, (cxp, cyp, rr) in enumerate(((0.18, 0.16, 340), (0.88, 0.30, 300), (0.55, 0.95, 380))):
        a('<radialGradient id="blob%d"><stop offset="0" stop-color="%s" stop-opacity="%s"/>'
          '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>'
          % (i, T["blob"], T["blobOp"], T["blob"]))

    # filters
    a('<filter id="glow" x="-40%%" y="-40%%" width="180%%" height="180%%">'
      '<feGaussianBlur stdDeviation="%(glowStd)s" result="b"/>'
      '<feFlood flood-color="%(glow)s" flood-opacity="%(glowOp)s" result="c"/>'
      '<feComposite in="c" in2="b" operator="in" result="g"/>'
      '<feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/>'
      '</feMerge></filter>' % T)

    # the portrait needs a far lighter touch — a wide blur turns 11px glyphs
    # into mush, so this one only lifts the edges
    a('<filter id="asciiGlow" x="-25%%" y="-25%%" width="150%%" height="150%%">'
      '<feGaussianBlur stdDeviation="1" result="b"/>'
      '<feFlood flood-color="%(glow)s" flood-opacity="%(asciiGlowOp)s" result="c"/>'
      '<feComposite in="c" in2="b" operator="in" result="g"/>'
      '<feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/>'
      '</feMerge></filter>' % T)

    a('<filter id="softglow" x="-60%%" y="-60%%" width="220%%" height="220%%">'
      '<feGaussianBlur stdDeviation="6" result="b"/>'
      '<feFlood flood-color="%(glow)s" flood-opacity=".28" result="c"/>'
      '<feComposite in="c" in2="b" operator="in"/></filter>' % T)

    a('<filter id="noise" x="0" y="0" width="100%" height="100%">'
      '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" stitchTiles="stitch"/>'
      '<feColorMatrix type="saturate" values="0"/></filter>')

    a('<filter id="blur24" x="-30%" y="-30%" width="160%" height="160%">'
      '<feGaussianBlur stdDeviation="24"/></filter>')

    # clips
    a('<clipPath id="cardClip"><rect x="%d" y="%d" width="%d" height="%d" rx="%d"/></clipPath>'
      % CARD)
    a('<clipPath id="leftClip"><rect x="%d" y="%d" width="%d" height="%d" rx="20"/></clipPath>'
      % (LX, LY, LW, LH))
    a('<clipPath id="rightClip"><rect x="%d" y="%d" width="%d" height="%d" rx="20"/></clipPath>'
      % (RX, RY, RW, RH))

    # per-line ASCII typing clips
    for i in range(AH):
        y = ASCII_Y0 + ASCII_LH * i - 10
        a('<clipPath id="tc%d"><rect x="%d" y="%s" width="0" height="%s">'
          '<animate attributeName="width" from="0" to="%d" dur=".45s" '
          'begin="%ss" fill="freeze" calcMode="spline" keySplines=".2 .7 .3 1"/>'
          '</rect></clipPath>'
          % (i, ASCII_X - 4, f(y), f(ASCII_LH + 1.5), ASCII_CLIP_W,
             f(0.25 + i * ASCII_STAGGER)))

    # role typing clips
    for i, r in enumerate(ROLES):
        w = len(r) * ROLE_CH
        t0, t1 = i * SLOT, i * SLOT + 1.7
        t2, t3 = i * SLOT + 3.3, i * SLOT + 4.05
        kt = [0.0, t0 / LOOP, t1 / LOOP, t2 / LOOP, t3 / LOOP, 1.0]
        kt = [max(k, 0.000001 if 0 < n < 5 else k) for n, k in enumerate(kt)]
        a('<clipPath id="rc%d"><rect x="%d" y="%d" width="0" height="26">'
          '<animate attributeName="width" values="0;0;%s;%s;0;0" keyTimes="%s" '
          'dur="%ss" repeatCount="indefinite"/></rect></clipPath>'
          % (i, ROLE_X - 2, ROLE_BASE - 19, f(w), f(w),
             ";".join(f(k) for k in kt), f(LOOP)))
    a('</defs>')

    # ---------------- styles ----------------
    a('<style>'
      '.pill{transform-box:fill-box;transform-origin:center;transition:transform .28s cubic-bezier(.2,.8,.2,1)}'
      '.pill:hover{transform:scale(1.07)}'
      '.pill:hover rect{stroke:%(stroke2)s}'
      '.ico{transition:transform .28s cubic-bezier(.2,.8,.2,1),opacity .28s ease;'
      'transform-box:fill-box;transform-origin:center;opacity:.82}'
      '.ico:hover{transform:scale(1.12);opacity:1}'
      '</style>' % T)

    # ---------------- background ----------------
    a('<rect width="%d" height="%d" rx="%d" fill="url(#bg)"/>' % (CW, CH, 26))
    a('<g clip-path="url(#cardClip)">')

    blobs = ((210, 120, 300, 200, "0"), (1010, 190, 280, 190, "1"), (640, 600, 340, 210, "2"))
    for k, (bx, by, brx, bry, gid) in enumerate(blobs):
        a('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="url(#blob%s)">'
          '<animateTransform attributeName="transform" type="translate" '
          'values="0 0;%d %d;%d %d;0 0" dur="%ds" repeatCount="indefinite"/>'
          '<animate attributeName="opacity" values="1;.62;1" dur="%ds" repeatCount="indefinite"/>'
          '</ellipse>'
          % (bx, by, brx, bry, gid, 34 - k * 22, -26 + k * 18, -20 + k * 16, 30 - k * 12,
             22 + k * 5, 9 + k * 3))

    # particles
    rnd = random.Random(7)
    a('<g fill="%s" opacity="%s">' % (T["glow"], T["partOp"]))
    for i in range(22):
        px = rnd.uniform(30, CW - 30)
        py = rnd.uniform(40, CH - 40)
        r = rnd.uniform(0.7, 1.9)
        dur = rnd.uniform(11, 24)
        rise = rnd.uniform(60, 170)
        a('<circle cx="%s" cy="%s" r="%s">'
          '<animate attributeName="cy" values="%s;%s;%s" dur="%ss" repeatCount="indefinite"/>'
          '<animate attributeName="opacity" values="0;.9;0" dur="%ss" '
          'begin="-%ss" repeatCount="indefinite"/></circle>'
          % (f(px), f(py), f(r), f(py), f(py - rise), f(py), f(dur),
             f(dur * 0.5), f(rnd.uniform(0, dur))))
    a('</g>')

    # ---------------- left panel ----------------
    a('<g>')
    a('<rect x="%d" y="%d" width="%d" height="%d" rx="20" fill="url(#panel)" '
      'stroke="%s" stroke-width="1"/>' % (LX, LY, LW, LH, T["stroke"]))
    a('<g clip-path="url(#leftClip)">')
    a('<rect x="%d" y="%d" width="%d" height="120" fill="url(#glass)" opacity=".5"/>'
      % (LX, LY, LW))

    # panel header
    a('<text x="%d" y="64" font-family="%s" font-size="10.5" letter-spacing="2.2" '
      'fill="%s">PORTRAIT.ASCII</text>' % (LX + 20, MONO, T["dim"]))
    a('<circle cx="%d" cy="60" r="3" fill="%s"><animate attributeName="opacity" '
      'values="1;.25;1" dur="2.4s" repeatCount="indefinite"/></circle>'
      % (LX + LW - 22, T["muted"]))
    a('<rect x="%d" y="80" width="%d" height="1" fill="%s"/>' % (LX + 20, LW - 40, T["stroke"]))

    # ascii block (floating + glow + gradient)
    a('<g filter="url(#asciiGlow)">')
    a('<g><animateTransform attributeName="transform" type="translate" '
      'values="0 0;0 -5;0 0" dur="7s" repeatCount="indefinite" calcMode="spline" '
      'keySplines=".4 0 .6 1;.4 0 .6 1"/>')
    for i, row in enumerate(ASCII_ROWS):
        y = ASCII_Y0 + ASCII_LH * i
        a('<text clip-path="url(#tc%d)" x="%d" y="%s" xml:space="preserve" '
          'font-family="%s" font-size="%s" fill="url(#accent)">'
          % (i, ASCII_X, f(y), MONO, f(ASCII_FS)))
        for shadow, run in ascii_runs(row):
            if shadow:
                a('<tspan fill="%s">%s</tspan>' % (T["asciiDim"], esc(run)))
            else:
                a('<tspan>%s</tspan>' % esc(run))
        a('</text>')
    a('</g></g>')

    # ascii scanline sweep
    a('<rect x="%d" y="110" width="%d" height="46" fill="url(#scan)" opacity=".9">'
      '<animate attributeName="y" values="110;486;110" dur="6.5s" repeatCount="indefinite"/>'
      '</rect>' % (LX, LW))

    # prompt under portrait
    a('<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".6s" '
      'begin="2.4s" fill="freeze"/>')
    a('<text x="%d" y="522" font-family="%s" font-size="12" fill="%s">'
      '<tspan fill="url(#accent)">$</tspan> render --portrait</text>'
      % (LX + 20, MONO, T["muted"]))
    a('<rect x="%s" y="511" width="8" height="14" fill="%s">'
      '<animate attributeName="opacity" values="1;1;0;0" dur="1.05s" '
      'calcMode="discrete" repeatCount="indefinite"/></rect>' % (f(LX + 161), T["text"]))
    a('<rect x="%d" y="540" width="%d" height="1" fill="%s"/>' % (LX + 20, LW - 40, T["stroke"]))
    a('<text x="%d" y="562" font-family="%s" font-size="10" letter-spacing="1.4" '
      'fill="%s">%d × %d · SMIL · NO-JS</text>' % (LX + 20, MONO, T["dim"], AW, AH))
    a('</g>')
    a('</g></g>')

    # ---------------- right panel ----------------
    a('<g>')
    a('<rect x="%d" y="%d" width="%d" height="%d" rx="20" fill="url(#panel)" '
      'stroke="%s" stroke-width="1"/>' % (RX, RY, RW, RH, T["stroke"]))
    a('<g clip-path="url(#rightClip)">')
    a('<rect x="%d" y="%d" width="%d" height="140" fill="url(#glass)" opacity=".5"/>'
      % (RX, RY, RW))

    # title bar
    for k in range(3):
        a('<circle cx="%d" cy="60" r="5.5" fill="none" stroke="%s" stroke-width="1.2" '
          'opacity="%s"/>' % (RX + 32 + k * 19, T["muted"], 0.85 - k * 0.22))
    a('<text x="%d" y="64" text-anchor="middle" font-family="%s" font-size="11" '
      'fill="%s">%s</text>' % (RX + RW // 2, MONO, T["dim"], esc(TERM_TITLE)))
    a('<rect x="%d" y="82" width="%d" height="1" fill="%s"/>' % (CX, CWD, T["stroke"]))

    # command
    a('<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".5s" begin=".3s" '
      'fill="freeze"/><text x="%d" y="114" font-family="%s" font-size="12.5" fill="%s">'
      '<tspan fill="url(#accent2)" font-weight="600">❯</tspan> whoami --profile</text></g>'
      % (CX, MONO, T["muted"]))

    # greeting + name
    a('<g opacity="0"><animateTransform attributeName="transform" type="translate" '
      'values="0 10;0 0" dur=".7s" begin=".7s" fill="freeze" calcMode="spline" '
      'keySplines=".2 .8 .2 1"/><animate attributeName="opacity" values="0;1" dur=".7s" '
      'begin=".7s" fill="freeze"/>')
    a('<text x="%d" y="154" font-family="%s" font-size="15" fill="%s">Hi \U0001F44B '
      '<tspan fill="%s">I’m</tspan></text>' % (CX, SANS, T["muted"], T["dim"]))
    a('<text x="%d" y="197" font-family="%s" font-size="38" font-weight="700" '
      'letter-spacing="-.8" fill="url(#accent2)" filter="url(#glow)">%s</text>'
      % (CX, SANS, esc(NAME)))
    a('</g>')

    # pixel cat, in the gap to the right of the name
    a(cat_group(T))

    # typing roles
    a('<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".6s" begin="1.4s" '
      'fill="freeze"/>')
    a('<text x="%d" y="%d" font-family="%s" font-size="%d" fill="url(#accent2)">▸</text>'
      % (CX, ROLE_BASE, MONO, ROLE_FS))
    for i, r in enumerate(ROLES):
        w = len(r) * ROLE_CH
        t0, t3 = i * SLOT, i * SLOT + 4.05
        a('<text clip-path="url(#rc%d)" x="%d" y="%d" font-family="%s" font-size="%d" '
          'textLength="%s" lengthAdjust="spacingAndGlyphs" fill="%s" opacity="0">%s'
          '<animate attributeName="opacity" values="0;1;0" keyTimes="0;%s;%s" '
          'calcMode="discrete" dur="%ss" repeatCount="indefinite"/></text>'
          % (i, ROLE_X, ROLE_BASE, MONO, ROLE_FS, f(w), T["text"], esc(r),
             f(t0 / LOOP), f(t3 / LOOP), f(LOOP)))

    # role cursor
    cvals, ckeys = [], []
    for i, r in enumerate(ROLES):
        w = len(r) * ROLE_CH
        for t, val in ((i * SLOT, 0), (i * SLOT + 1.7, w), (i * SLOT + 3.3, w),
                       (i * SLOT + 4.05, 0)):
            ckeys.append(min(0.999999, max(0.0, t / LOOP)))
            cvals.append(ROLE_X + 4 + val)
    ckeys = [0.0] + ckeys + [1.0]
    cvals = [ROLE_X + 4] + cvals + [ROLE_X + 4]
    a('<rect x="%d" y="%d" width="9" height="19" fill="url(#accent2)">'
      '<animate attributeName="x" values="%s" keyTimes="%s" dur="%ss" '
      'repeatCount="indefinite"/>'
      '<animate attributeName="opacity" values="1;1;.15;.15" dur="1.05s" '
      'calcMode="discrete" repeatCount="indefinite"/></rect>'
      % (ROLE_X + 4, ROLE_BASE - 15,
         ";".join(f(v) for v in cvals), ";".join(f(k) for k in ckeys), f(LOOP)))
    a('</g>')

    a('<rect x="%d" y="258" width="%d" height="1" fill="%s"/>' % (CX, CWD, T["stroke"]))

    # info rows
    for i, (label, value) in enumerate(INFO):
        y = 284 + i * 26
        a('<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".55s" '
          'begin="%ss" fill="freeze"/>'
          '<animateTransform attributeName="transform" type="translate" values="-10 0;0 0" '
          'dur=".55s" begin="%ss" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/>'
          % (f(1.7 + i * 0.16), f(1.7 + i * 0.16)))
        a('<rect x="%d" y="%d" width="3" height="3" fill="%s"/>' % (CX, y - 8, T["dim"]))
        a('<text x="%d" y="%d" font-family="%s" font-size="10.5" letter-spacing="1.5" '
          'fill="%s">%s</text>' % (CX + 14, y, MONO, T["dim"], label))
        a('<text x="%d" y="%d" font-family="%s" font-size="12.5" fill="%s">%s</text>'
          % (CX + 112, y, MONO, T["muted"], esc(value)))
        a('</g>')

    # skills
    a('<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".5s" begin="2.5s" '
      'fill="freeze"/><text x="%d" y="418" font-family="%s" font-size="10" '
      'letter-spacing="2.2" fill="%s">STACK</text></g>' % (CX, MONO, T["dim"]))

    rows, pfs = pack_pills()
    n = 0
    for ri, (row, roww) in enumerate(rows):
        px = CX
        ry = 430 + ri * 32
        for (label, w, tw) in row:
            beg = f(2.65 + n * 0.06)
            a('<g class="pill" opacity="0">'
              '<animate attributeName="opacity" values="0;1" dur=".45s" begin="%ss" fill="freeze"/>'
              % beg)
            a('<rect x="%s" y="%d" width="%s" height="24" rx="12" fill="%s" stroke="%s" '
              'stroke-width="1"><animate attributeName="stroke-opacity" values="1;.45;1" '
              'dur="%ss" begin="-%ss" repeatCount="indefinite"/></rect>'
              % (f(px), ry, f(w), T["pillFill"], T["pillStroke"], f(4.2), f(n * 0.31)))
            a('<text x="%s" y="%d" text-anchor="middle" font-family="%s" font-size="%s" '
              'fill="%s">%s</text>'
              % (f(px + w / 2), ry + 16, SANS, f(pfs), T["muted"], esc(label)))
            a('</g>')
            px += w + 8
            n += 1

    a('<rect x="%d" y="534" width="%d" height="1" fill="%s"/>' % (CX, CWD, T["stroke"]))

    # socials
    gh = ("M12 .3a12 12 0 0 0-3.8 23.4c.6.1.8-.3.8-.6v-2.2c-3.3.7-4-1.6-4-1.6-.6-1.4-1.4-1.8-1.4-1.8"
          "-1.1-.8.1-.8.1-.8 1.2.1 1.9 1.3 1.9 1.3 1.1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.8-1.6-2.7-.3"
          "-5.5-1.3-5.5-5.9 0-1.3.5-2.4 1.2-3.2-.1-.3-.5-1.5.1-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 0 1 6 0"
          "c2.3-1.5 3.3-1.2 3.3-1.2.6 1.7.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.6-5.5 5.9.4.4.8 1.1.8 2.2"
          "v3.3c0 .3.2.7.8.6A12 12 0 0 0 12 .3z")
    socials = [
        (gh, "github.com/Devlynxz", "https://github.com/Devlynxz"),
        (None, "erlynquimson@gmail.com", "mailto:erlynquimson@gmail.com"),
    ]
    sx = CX
    a('<g opacity="0"><animate attributeName="opacity" values="0;1" dur=".6s" begin="3.3s" '
      'fill="freeze"/>')
    for path, label, href in socials:
        a('<a xlink:href="%s" target="_blank"><g class="ico">' % esc(href))
        if path:
            a('<g transform="translate(%d,550) scale(.71)"><path d="%s" fill="%s"/></g>'
              % (sx, path, T["text"]))
        else:
            a('<g transform="translate(%d,551)" fill="none" stroke="%s" stroke-width="1.6">'
              '<rect x=".8" y="1.6" width="15.4" height="12.8" rx="2.4"/>'
              '<path d="M1.6 3.2 8.5 8.6 15.4 3.2"/></g>' % (sx, T["text"]))
        a('<text x="%d" y="562" font-family="%s" font-size="12" fill="%s">%s</text>'
          % (sx + 26, MONO, T["muted"], esc(label)))
        a('</g></a>')
        sx += 26 + len(label) * 7.2 + 42
    # status
    status = "open to collab"
    sdot = CR - len(status) * 6.9 - 15
    a('<circle cx="%s" cy="558" r="3.5" fill="%s"><animate attributeName="opacity" '
      'values="1;.2;1" dur="2s" repeatCount="indefinite"/></circle>' % (f(sdot), T["text"]))
    a('<circle cx="%s" cy="558" r="3.5" fill="none" stroke="%s" stroke-width="1">'
      '<animate attributeName="r" values="3.5;9" dur="2s" repeatCount="indefinite"/>'
      '<animate attributeName="opacity" values=".7;0" dur="2s" repeatCount="indefinite"/>'
      '</circle>' % (f(sdot), T["text"]))
    a('<text x="%d" y="562" text-anchor="end" font-family="%s" font-size="11.5" '
      'letter-spacing=".6" fill="%s">%s</text>' % (CR, MONO, T["dim"], status))
    a('</g>')

    a('</g></g>')

    # ---------------- overlays ----------------
    # global scanline
    a('<rect x="0" y="-110" width="%d" height="110" fill="url(#scan)" opacity=".8">'
      '<animate attributeName="y" values="-110;%d" dur="8s" repeatCount="indefinite"/></rect>'
      % (CW, CH))
    # noise
    a('<rect width="%d" height="%d" filter="url(#noise)" opacity="%s"/>'
      % (CW, CH, T["noiseOp"]))
    a('</g>')

    # ---------------- borders ----------------
    a('<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="none" stroke="%s" '
      'stroke-width="1"/>' % (CARD[0], CARD[1], CARD[2], CARD[3], CARD[4], T["stroke"]))
    a('<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="none" stroke="url(#shimmer)" '
      'stroke-width="1.4"/>' % (CARD[0], CARD[1], CARD[2], CARD[3], CARD[4]))

    a('</svg>')
    return "".join(o)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
    out = os.environ.get("HERO_OUT", out)
    os.makedirs(out, exist_ok=True)
    for name in ("dark", "light"):
        p = os.path.join(out, "hero-%s.svg" % name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(build(name))
        print("wrote", p, os.path.getsize(p), "bytes")
