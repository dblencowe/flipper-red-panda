"""Red panda parts: head sprite, bodies, tail, branch and props.

The head is authored as the left half plus the centre column and mirrored,
so the face stays symmetric. Legend: '#' ink, 'w' white, 'd' dark russet
fur, 'm' russet fur, 'f' pale fur, '.' transparent.
"""
import math

import pcraft

pcraft.COLOURS["D"] = "#404040"  # dark russet: dense ordered dither
pcraft.LEGEND["d"] = "D"

# Left half, cols 0..17; col 17 is the centre line. Mirrored to 35 wide.
HEAD_LEFT = [
    "....###...........",  # 0  ear tip
    "...#www#..........",  # 1
    "..#ww#ww#....#####",  # 2  top of head
    "..#w###w#..#dddddd",  # 3
    ".#w#####w##ddddddd",  # 4
    ".#w#####w#dddddddd",  # 5
    ".#w####w#ddddddddd",  # 6
    ".#ww##ww#ddddddddd",  # 7
    "..#wwww#dddddddddd",  # 8
    "..#dddddwwwwwddddd",  # 9  white brow
    ".#dddddwwwwwwwdddd",  # 10
    ".#ddddww####wwdddd",  # 11 eye
    ".#ddddww#w##wwdddd",  # 12
    ".#wdddww####wwdddd",  # 13
    ".#wwwddww##wwdddww",  # 14
    "#wwwwwdddd##dddwww",  # 15 tear mark
    ".#wwwwwwd##dwwwwww",  # 16
    "#wwwwwwwww##www###",  # 17 nose
    ".#wwwwwwww##wwww##",  # 18
    ".#wwwwwwwww##wwww#",  # 19
    "..#wwwwwwww##ww##w",  # 20 mouth
    "..#wwwwwwwww#wwwww",  # 21
    "...#wwwwwwwwwwwwww",  # 22
    "....##wwwwwwwwwwww",  # 23
    "......############",  # 24 chin
]
CX = 17
HEAD_W = 2 * CX + 1
HEAD_H = len(HEAD_LEFT)

EYES = {  # rows 11..14, cols 6..13 of the left half
    "open":   ["ww####ww", "ww#w##ww", "ww####ww", "dww##wwd"],
    "closed": ["wwwwwwww", "w#wwww#w", "ww####ww", "dww##wwd"],
    "happy":  ["www##www", "ww#ww#ww", "w#wwww#w", "dww##wwd"],
    "wide":   ["w######w", "w#w####w", "w######w", "dw####wd"],
    "side":   ["ww####ww", "ww####ww", "ww##w#ww", "dww##wwd"],  # glancing
}


def _patch(rows, row, col, text):
    r = rows[row]
    rows[row] = r[:col] + text + r[col + len(text):]


def head(eyes="open", mouth="closed", ear=None):
    left = list(HEAD_LEFT)
    for i, text in enumerate(EYES[eyes]):
        _patch(left, 11 + i, 6, text)
    rows = [r + r[:CX][::-1] for r in left]
    if mouth == "open":
        _patch(rows, 20, 15, "#####")
        _patch(rows, 21, 15, "#####")
        _patch(rows, 22, 16, "###")
    elif mouth == "chew":
        _patch(rows, 20, 15, "#####")
        _patch(rows, 21, 16, "###")
    if ear == "flick":  # right ear bends outward
        for r in range(0, 9):
            rows[r] = rows[r][:26] + "." * 9
        art = [
            (1, 28, "#####"),
            (2, 26, "##wwwww#"),
            (3, 25, "dw#####w#"),
            (4, 25, "ddw####w#"),
            (5, 25, "dddw###w#"),
            (6, 25, "ddddwwww#"),
            (7, 25, "dddddd##."),
            (8, 25, "ddddd#..."),
        ]
        for r, c, t in art:
            rows[r] = (rows[r][:c] + t + rows[r][c + len(t):])[:HEAD_W]
        rows[2] = rows[2][:17] + "#########" + rows[2][26:]
        rows[3] = rows[3][:17] + "dddddddd" + rows[3][25:]
    return [r[:HEAD_W].ljust(HEAD_W, ".") for r in rows]


def bezier(p0, p1, p2, steps=80):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        a, b, c = (1 - t) ** 2, 2 * (1 - t) * t, t * t
        pts.append((a * p0[0] + b * p1[0] + c * p2[0],
                    a * p0[1] + b * p1[1] + c * p2[1]))
    return pts


def tail(cv, p0, p1, p2, r=6.0, band=5.0, light="f", tip=True):
    """Bushy ringed tail along a quadratic curve, coloured pixel by pixel.

    Each pixel takes the arc length of the nearest curve point; alternate
    stretches are dark rings. The rim is ink so the tail reads as one shape.
    """
    pts = bezier(p0, p1, p2)
    arc, total = [0.0], 0.0
    for (a, b), (c, d) in zip(pts, pts[1:]):
        total += math.hypot(c - a, d - b)
        arc.append(total)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = int(min(xs) - r - 2), int(max(xs) + r + 2)
    y0, y1 = int(min(ys) - r - 2), int(max(ys) + r + 2)
    grid = {}
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            best, bi = 1e9, 0
            for i, (px, py) in enumerate(pts):
                d = (px - x - 0.5) ** 2 + (py - y - 0.5) ** 2
                if d < best:
                    best, bi = d, i
            d = math.sqrt(best)
            if d > r:
                continue
            if d > r - 1.2:
                ch = "#"
            elif tip and arc[bi] > total - 1.5:
                ch = "#"
            else:
                ch = "#" if int(arc[bi] // band) % 2 else light
            grid[(x, y)] = ch
    lines = ["".join(grid.get((x, y), ".") for x in range(x0, x1 + 1))
             for y in range(y0, y1 + 1)]
    cv.sprite(x0, y0, lines)


def branch(cv, top=55, knots=(8, 52, 96), leaf=None):
    cv.rect(-1, top, 130, 64 - top + 1, "K")
    cv.rect(-1, top + 1, 130, 64 - top, "L")
    for k in knots:  # bark marks
        cv.line(k, top + 3, k + 6, top + 3)
        cv.line(k + 3, top + 6, k + 11, top + 6)


def leaf(cv, x, y, flip=False, droop=0):
    rows = [
        "....####",
        "..##wwww#",
        ".#ww##ww#",
        "#ww#wwww#",
        "##w#ww##.",
        ".#####...",
    ]
    cv.sprite(x, y + droop, rows, flip=flip)


def sitting_panda(cv, hx, hy, eyes="open", mouth="closed", ear=None,
                  tail_tip=(0, 0), paws="down", breathe=0):
    """Panda sitting on the branch, facing out. (hx, hy) is the head's top-left."""
    by = hy + breathe
    tx, ty = tail_tip
    # Tail behind the body, curling up the right-hand side.
    tail(cv, (hx + 26, hy + 47), (hx + 50, hy + 50), (hx + 44 + tx, hy + 24 + ty))
    # Body: russet fur with a darker chest.
    cv.ell_outlined(hx + 4, by + 19, 27, 33, "M")
    cv.ell(hx + 9, by + 24, 17, 26, "D")
    # Hind feet at the sides, kept apart from the body by a white rim.
    for fx in (hx + 1, hx + 23):
        cv.ell(fx - 1, hy + 43, 13, 8, "W")
        cv.ell(fx, hy + 44, 11, 6, "K")
    if paws == "down":
        front_legs(cv, hx, by + 30, hy + 51)
    cv.sprite(hx, hy + (1 if breathe > 0 else 0), head(eyes, mouth, ear))


def front_legs(cv, hx, top, bottom):
    """Two black front legs with paws, outlined in white so they separate."""
    for lx in (hx + 10, hx + 19):
        cv.rect(lx - 1, top, 8, bottom - top, "W")
        cv.ell(lx - 2, bottom - 5, 10, 6, "W")
    for lx in (hx + 10, hx + 19):
        cv.rect(lx, top, 6, bottom - top - 2, "K")
        cv.ell(lx - 1, bottom - 4, 8, 4, "K")


# ---------------------------------------------------------------------------
# Shapes used by the other poses


def thick_line(cv, p0, p1, width, fill, outline="K", nodes=0):
    """A rounded thick stroke from p0 to p1, ink rim, optional node rings."""
    (x0, y0), (x1, y1) = p0, p1
    length = math.hypot(x1 - x0, y1 - y0) or 1.0
    r = width / 2.0
    grid = {}
    for y in range(int(min(y0, y1) - r - 1), int(max(y0, y1) + r + 2)):
        for x in range(int(min(x0, x1) - r - 1), int(max(x0, x1) + r + 2)):
            px, py = x + 0.5, y + 0.5
            t = ((px - x0) * (x1 - x0) + (py - y0) * (y1 - y0)) / (length ** 2)
            t = max(0.0, min(1.0, t))
            d = math.hypot(px - (x0 + t * (x1 - x0)), py - (y0 + t * (y1 - y0)))
            if d > r:
                continue
            if d > r - 1.0 and outline:
                grid[(x, y)] = outline
            elif nodes and int(t * length) % nodes == nodes - 1:
                grid[(x, y)] = "K"
            else:
                grid[(x, y)] = fill
    by_colour = {}
    for p, c in grid.items():
        by_colour.setdefault(c, []).append(p)
    for c in sorted(by_colour, key=lambda k: k == "K"):
        cv.pixels(by_colour[c], c)


LEAF = {  # stem at the left end of the middle row, tip at the right
    "long": ["......####..",
             "...###wwww##",
             "###wwww###..",
             "..####......"],
    "short": ["....###.",
              ".###ww##",
              "##ww##..",
              ".##....."],
}


def bamboo_leaf(cv, x, y, length=9, up=False, flip=False):
    """A pointed leaf whose stem sits at (x, y). up=False droops it."""
    rows = LEAF["long" if length >= 8 else "short"]
    if not up:
        rows = rows[::-1]
    w = len(rows[0])
    sx = x - w + 1 if flip else x
    sy = y - 2 if up else y - 1
    cv.sprite(sx, sy, rows, flip=flip)


def bamboo_stalk(cv, x, top, bottom, w=5, fill="L", leaves=()):
    cv.rect_outlined(x, top, w, bottom - top, fill)
    for ny in range(top + 9, bottom - 2, 11):
        cv.rect(x, ny, w, 1, "K")
        cv.rect(x - 1, ny, 1, 1, "K")
        cv.rect(x + w, ny, 1, 1, "K")
    for (ly, side, up) in leaves:
        lx = x + w if side > 0 else x - 1
        bamboo_leaf(cv, lx, ly, length=9, up=up, flip=side < 0)


def zzz(cv, x, y, size):
    n = 7 if size == "big" else 5
    pts = [(x + i, y) for i in range(n)] + [(x + i, y + n - 1) for i in range(n)]
    pts += [(x + n - 1 - i, y + i) for i in range(1, n - 1)]
    cv.pixels(pts, "K")


def star(cv, x, y, big=False):
    if big:
        cv.pixels([(x, y - 2), (x, y - 1), (x, y), (x, y + 1), (x, y + 2),
                   (x - 2, y), (x - 1, y), (x + 1, y), (x + 2, y)], "K")
    else:
        cv.pixels([(x, y)], "K")


def moon(cv, x, y, r=7):
    cv.ell(x, y, 2 * r, 2 * r, "K")
    cv.ell(x + 4, y - 2, 2 * r, 2 * r, "W")


def sleeping_panda(cv, x, y, breathe=0, eyes="closed", tail_sway=0):
    """Panda draped over the branch, chin on its paws. (x, y) is the head's top-left."""
    b = breathe
    # Hind legs dangling over the front of the branch.
    for lx in (x + 48, x + 64):
        cv.rect(lx - 1, y + 26, 8, 64 - y - 26 + 1, "W")
        cv.rect(lx, y + 26, 6, 64 - y - 26, "K")
    cv.ell_outlined(x + 18, y + 6 - b, 64, 28 + b, "M")
    cv.ell(x + 30, y + 18 - b, 40, 14 + b, "D")
    # Tail hangs down over the front of the branch.
    tail(cv, (x + 74, y + 20), (x + 90, y + 24), (x + 88 + tail_sway, y + 46), r=5.5)
    # Front paws under the chin, then the head.
    for px in (x + 6, x + 20):
        cv.ell(px - 1, y + 21, 11, 7, "W")
        cv.ell(px, y + 22, 9, 5, "K")
    cv.sprite(x, y, head(eyes))


def standing_panda(cv, hx, hy, arms="up", eyes="wide", mouth="open", sway=0):
    """Panda up on its hind legs. (hx, hy) is the head's top-left."""
    tail(cv, (hx + 24, hy + 50), (hx + 46, hy + 54), (hx + 48 + sway, hy + 34), r=5.5)
    for lx in (hx + 10, hx + 19):  # hind legs
        cv.rect(lx - 1, hy + 40, 8, 53 - hy - 40 + 2, "W")
        cv.ell(lx - 3, hy + 47, 12, 7, "W")
    cv.ell_outlined(hx + 6, hy + 18, 23, 30, "M")
    cv.ell(hx + 10, hy + 23, 15, 22, "D")
    for lx in (hx + 10, hx + 19):
        cv.rect(lx, hy + 40, 6, 53 - hy - 40, "K")
        cv.ell(lx - 2, hy + 48, 10, 5, "K")
    shoulders = ((hx + 9, hy + 27), (hx + 26, hy + 27))
    if arms == "up":
        hands = ((hx - 3, hy + 8), (hx + 38, hy + 8))
    elif arms == "half":
        hands = ((hx - 4, hy + 20), (hx + 39, hy + 20))
    else:
        hands = ((hx + 7, hy + 40), (hx + 28, hy + 40))
    for s, h in zip(shoulders, hands):
        thick_line(cv, s, h, 8, "W", outline=None)
    for s, h in zip(shoulders, hands):
        thick_line(cv, s, h, 6, "K", outline=None)
        if arms != "down":  # claws
            hx2, hy2 = h
            cv.pixels([(hx2 - 2, hy2 - 4), (hx2 - 2, hy2 - 5), (hx2, hy2 - 5),
                       (hx2, hy2 - 6), (hx2 + 2, hy2 - 4), (hx2 + 2, hy2 - 5)], "K")
    cv.sprite(hx, hy, head(eyes, mouth))


def eating_panda(cv, hx, hy, bite=0, mouth="closed", eyes="open"):
    """Sitting panda holding a bamboo stalk up to its mouth."""
    sitting_panda(cv, hx, hy, eyes=eyes, mouth=mouth, paws="none")
    # Stalk runs up across the chest to the corner of the mouth. Each bite
    # takes a leaf off the top.
    base, top = (hx + 5, 55), (hx + 14, hy + 19)

    def along(t):
        return (int(base[0] + t * (top[0] - base[0])),
                int(base[1] + t * (top[1] - base[1])))

    thick_line(cv, base, top, 6, "W", nodes=9)
    # Leaves sprout below the chin and fan out to the left of the face.
    (ax, ay), (bx, by_) = along(0.74), along(0.86)
    leaves = [(bx - 3, by_, True, True, 9), (ax - 3, ay + 1, False, True, 9),
              (ax - 3, ay - 1, True, True, 6)]
    for lx, ly, up, flip, n in leaves[bite:]:
        bamboo_leaf(cv, lx, ly, length=n, up=up, flip=flip)

    # Short arms from the shoulders, paws gripping the stalk.
    grips = (((hx + 8, hy + 30), along(0.55)), ((hx + 25, hy + 31), along(0.4)))
    for s, g in grips:
        thick_line(cv, s, g, 8, "W", outline=None)
    for s, g in grips:
        thick_line(cv, s, g, 6, "K", outline=None)
        cv.ell(g[0] - 4, g[1] - 3, 8, 6, "K")


def laptop_panda(cv, hx, hy, phase=0, eyes="open", screen=0):
    """Panda behind a laptop, paws on the keys. phase alternates the paws."""
    sitting_panda(cv, hx, hy, eyes=eyes, paws="none")
    # Lid (we see its back) and the base.
    lid_x, lid_y, lid_w, lid_h = hx + 2, hy + 29, 31, 22
    cv.rect_outlined(lid_x, lid_y, lid_w, lid_h, "W")
    cv.rect(lid_x + 2, lid_y + 2, lid_w - 4, lid_h - 4, "L")
    # A paw-print logo on the lid.
    cx, cy = lid_x + lid_w // 2, lid_y + 12
    cv.ell(cx - 3, cy - 1, 7, 5, "K")
    for tx, ty in ((-4, -4), (-1, -6), (2, -6), (5, -4)):
        cv.rect(cx + tx - 1, cy + ty, 2, 2, "K")
    cv.rect(hx - 4, lid_y + lid_h, 43, 4, "K")
    cv.rect(hx - 3, lid_y + lid_h + 1, 41, 2, "W")
    # Paws on the keys either side of the lid.
    lp = 0 if phase == 0 else -2
    rp = -2 if phase == 0 else 0
    for px, dy in ((hx - 4, lp), (hx + 32, rp)):
        cv.ell(px - 1, lid_y + lid_h - 5 + dy, 10, 8, "W")
        cv.ell(px, lid_y + lid_h - 4 + dy, 8, 6, "K")
    if screen:  # activity light blinking on the lid
        cv.rect(lid_x + lid_w - 5, lid_y + 2, 2, 2, "K")
