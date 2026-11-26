"""Phase 2 firmware pictures: result screens, system screens, level-up and
no-SD animations. Registered with tools/icons.py, which renders them.

Every picture keeps the empty areas of the dolphin it replaces, because the
firmware prints its own text there. Nothing here is copied from upstream:
props and text are drawn fresh (text with tools/pixfont.py).
"""
import math

import panda
import pixfont
from pcraft import Canvas

# ---------------------------------------------------------------------------
# Shared pieces


def bust(cv, hx, hy, eyes="open", mouth="closed", brow=None, chest_h=40, ear=None):
    """Head and shoulders: russet shoulders, dark chest, the head on top."""
    cv.ell_outlined(hx - 3, hy + 19, 41, chest_h, "M")
    cv.ell(hx + 7, hy + 23, 21, chest_h, "D")
    cv.sprite(hx, hy, panda.head(eyes, mouth, ear, brow=brow))


def halo_head(cv, hx, hy, eyes="open", mouth="closed"):
    """White rim round the head, for drawing on black."""
    rows = ["".join("w" if ch != "." else "." for ch in r) for r in panda.head(eyes, mouth)]
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
        cv.sprite(hx + dx, hy + dy, rows)


def arm(cv, shoulder, hand, width=8, fill="K"):
    """A black arm with a white rim, from the shoulder to the paw."""
    panda.thick_line(cv, shoulder, hand, width, "W", outline=None)
    panda.thick_line(cv, shoulder, hand, width - 2, fill, outline=None)


def long_arm(cv, shoulder, hand):
    """A stretched foreleg: dark fur with an ink edge and a white rim, so a
    long reach doesn't read as a stick. Ends in a paw with toe pads."""
    panda.thick_line(cv, shoulder, hand, 10, "W", outline=None)
    panda.thick_line(cv, shoulder, hand, 8, "D", outline="K")
    x, y = hand
    cv.ell(x - 6, y - 5, 12, 10, "W")
    cv.ell(x - 5, y - 4, 10, 8, "K")
    cv.pixels([(x - 3, y - 2), (x - 3, y), (x - 3, y + 2), (x - 1, y - 1), (x - 1, y + 1)], "W")


def paw(cv, x, y, w=8, h=6):
    """A black paw centred on (x, y), white rim."""
    cv.ell(x - w // 2 - 1, y - h // 2 - 1, w + 2, h + 2, "W")
    cv.ell(x - w // 2, y - h // 2, w, h, "K")


THUMB = [  # black fist, thumb up, white rim; top-left of the thumb is the anchor
    ".####.....",
    "#wwww#....",
    "#w##w#....",
    "#w##w#....",
    "#w##w#....",
    "#w##w####.",
    "#w##wwwww#",
    "#w#######w",
    "#w#wwwwww#",
    "#w#######w",
    "#w#wwwwww#",
    "#w#######w",
    "#wwwwwwww#",
    ".########.",
]


def thumbs_up(cv, x, y, flip=False):
    cv.sprite(x, y, THUMB, flip=flip)


def arc(cv, cx, cy, r, a0, a1, c="K"):
    """Circle arc from angle a0 to a1 in degrees (0 = right, 90 = down)."""
    pts = []
    for i in range(int(abs(a1 - a0) * r / 20) + 8):
        a = math.radians(a0 + (a1 - a0) * i / (int(abs(a1 - a0) * r / 20) + 7))
        pts.append((round(cx + r * math.cos(a)), round(cy + r * math.sin(a))))
    cv.pixels(pts, c)


def waves(cv, cx, cy, radii, facing="right", c="K"):
    """Radio waves: arcs round (cx, cy) opening to one side."""
    span = {"right": (-40, 40), "left": (140, 220), "up": (230, 310)}[facing]
    for r in radii:
        arc(cv, cx, cy, r, *span, c=c)


def sparkle(cv, x, y, big=False, c="K"):
    n = 3 if big else 2
    pts = [(x + i, y) for i in range(-n, n + 1)] + [(x, y + i) for i in range(-n, n + 1)]
    if big:
        pts += [(x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1), (x + 1, y + 1)]
    cv.pixels(pts, c)


def rays(cv, x, y, r0=5, r1=8, angles=(200, 240, 270, 300, 340)):
    """Short lines bursting out of (x, y): excitement or glow."""
    for a in angles:
        t = math.radians(a)
        cv.line(round(x + r0 * math.cos(t)), round(y + r0 * math.sin(t)),
                round(x + r1 * math.cos(t)), round(y + r1 * math.sin(t)))


def chip(cv, x, y, s=12):
    """A chip with pins on every side."""
    cv.rect_outlined(x, y, s, s, "W")
    cv.rect_outlined(x + 3, y + 3, s - 6, s - 6, "L")
    for i in range(2, s - 1, 3):
        cv.rect(x + i, y - 2, 1, 2, "K")
        cv.rect(x + i, y + s, 1, 2, "K")
        cv.rect(x - 2, y + i, 2, 1, "K")
        cv.rect(x + s, y + i, 2, 1, "K")


# ---------------------------------------------------------------------------
# P02-01 result screens


def done():
    """Done: thumbs up. The firmware prints "Done" to the left of it."""
    cv = Canvas(80, 58)
    hx, hy = 38, 6
    bust(cv, hx, hy, eyes="happy", mouth="open")
    arm(cv, (hx + 6, hy + 34), (hx - 8, hy + 34), width=9)
    thumbs_up(cv, hx - 18, hy + 22)
    return cv


def reading_success():
    """Card read: delighted, with a burst of excitement."""
    cv = Canvas(59, 63)
    hx, hy = 6, 12
    bust(cv, hx, hy, eyes="wide", mouth="open", chest_h=44)
    rays(cv, 47, 12, 4, 9, angles=(200, 235, 270, 305, 340))
    rays(cv, 6, 12, 4, 8, angles=(200, 240, 270))
    return cv


def floppy(cv, x, y):
    cv.rect_outlined(x, y, 14, 14, "W")
    cv.rect(x + 3, y + 1, 7, 4, "K")
    cv.rect(x + 7, y + 2, 2, 2, "W")
    cv.rect_outlined(x + 2, y + 7, 10, 6, "W")
    cv.rect(x + 4, y + 9, 6, 1, "K")
    cv.pixels([(x + 13, y)], "W")


def saved():
    """Saved: holds out a floppy disk. "Saved" is printed to the left."""
    cv = Canvas(92, 58)
    hx, hy = 44, 6
    bust(cv, hx, hy, eyes="happy", mouth="closed")
    arm(cv, (hx + 6, hy + 34), (hx - 10, hy + 32), width=9)
    floppy(cv, hx - 26, hy + 20)
    paw(cv, hx - 11, hy + 32, 9, 8)
    return cv


def card(cv, x, y):
    cv.rect_outlined(x, y, 15, 10, "W")
    cv.rect_outlined(x + 2, y + 3, 5, 4, "L")
    cv.rect(x + 9, y + 3, 4, 1, "K")
    cv.rect(x + 9, y + 5, 3, 1, "K")


def success():
    """Success: holds up a glowing card on the right."""
    cv = Canvas(91, 55)
    hx, hy = 10, 6
    bust(cv, hx, hy, eyes="happy", mouth="open")
    arm(cv, (hx + 30, hy + 34), (hx + 46, hy + 26), width=9)
    card(cv, hx + 42, hy + 11)
    paw(cv, hx + 47, hy + 25, 9, 8)
    rays(cv, hx + 49, hy + 15, 10, 14, angles=(190, 225, 270, 315, 350))
    return cv


HOURGLASS = [
    "#########",
    "#wwwwwww#",
    ".#wwwww#.",
    "..#www#..",
    "...#w#...",
    "...#w#...",
    "..#w#w#..",
    ".#wwwww#.",
    "#ww###ww#",
    "#########",
]


def wait():
    """Wait: holds up an hourglass and watches the sand run."""
    cv = Canvas(59, 54)
    hx, hy = 4, 6
    bust(cv, hx, hy, eyes="side", mouth="closed", chest_h=44)
    arm(cv, (hx + 30, hy + 34), (hx + 42, hy + 28), width=9)
    cv.sprite(hx + 38, hy + 14, HOURGLASS)
    paw(cv, hx + 42, hy + 28, 9, 7)
    for dx, dy in ((50, 4), (53, 2), (56, 0)):
        cv.rect(dx, dy + 2, 2, 2, "K")
    return cv


def key_fob(cv, x, y):
    """An iButton key: a round tablet on a fob with a ring."""
    cv.ell(x + 3, y - 6, 7, 7, "K")
    cv.ell(x + 5, y - 4, 3, 3, "W")
    cv.rect_outlined(x, y, 13, 9, "W")
    cv.ell(x + 2, y + 1, 9, 7, "K")
    cv.ell(x + 4, y + 2, 5, 4, "W")


def ibutton_success():
    """iButton read: holds up a key fob, sparkling."""
    cv = Canvas(92, 55)
    hx, hy = 10, 6
    bust(cv, hx, hy, eyes="happy", mouth="open")
    arm(cv, (hx + 30, hy + 34), (hx + 46, hy + 26), width=9)
    key_fob(cv, hx + 41, hy + 15)
    paw(cv, hx + 47, hy + 25, 9, 8)
    sparkle(cv, hx + 66, hy + 6, big=True)
    sparkle(cv, hx + 38, hy + 2)
    sparkle(cv, hx + 68, hy + 24)
    return cv


def nfc_emulation():
    """Emulating: holding very still, eyes wide. Waves in the corner."""
    cv = Canvas(51, 64)
    hx, hy = 4, 16
    bust(cv, hx, hy, eyes="wide", mouth="closed", chest_h=44)
    waves(cv, 50, 0, (4, 7, 10), facing="left")
    return cv


def rfid(send):
    """RFID: the panda, a chip, and waves between them."""
    cv = Canvas(97, 61)
    hx, hy = 4, 10
    bust(cv, hx, hy, eyes="open", mouth="closed", chest_h=44)
    chip(cv, 80, 14)
    if send:
        waves(cv, 40, 21, (12, 17, 22), facing="right")
    else:
        waves(cv, 78, 21, (12, 17, 22), facing="left")
    return cv


def rod_line(cv, tip, end):
    (x0, y0), (x1, y1) = tip, end
    pts = panda.bezier(tip, (x1, y0 - 2), end, steps=40)
    cv.pixels([(round(x), round(y)) for x, y in pts], "K")
    cv.pixels([(x1, y1 + 1), (x1, y1 + 2), (x1 - 1, y1 + 3), (x1 - 2, y1 + 2)], "K")


def fishing():
    """Sub-GHz read (external radio): fishing with a bamboo rod.

    Bottom right (x >= 57, y >= 34) stays clear for "Hopper scan..." and
    "Decoding...".
    """
    cv = Canvas(123, 52)
    hx, hy = 6, 4
    bust(cv, hx, hy, eyes="side", mouth="closed", chest_h=40)
    panda.thick_line(cv, (hx + 24, hy + 40), (88, 6), 4, "L", nodes=8)
    arm(cv, (hx + 30, hy + 33), (hx + 34, hy + 31), width=9)
    paw(cv, hx + 35, hy + 30, 9, 8)
    rod_line(cv, (88, 6), (96, 26))
    waves(cv, 104, 17, (5, 9, 13), facing="right")
    return cv


def scanning(width=123):
    """Sub-GHz read (internal radio): pointing a Yagi antenna.

    Official firmware uses a 96 px wide version with a shorter antenna and
    no waves.
    """
    cv = Canvas(width, 52)
    hx, hy = 6, 4
    short = width < 123
    end = 84 if short else 92
    bust(cv, hx, hy, eyes="side", mouth="closed", chest_h=40)
    cv.rect_outlined(hx + 30, 21, end - hx - 32, 3, "W")
    for x in range(hx + 44, end, 9):
        cv.rect(x, 13, 2, 19, "K")
    cv.rect_outlined(hx + 28, 17, 7, 11, "L")
    arm(cv, (hx + 28, hy + 33), (hx + 32, 26), width=9)
    paw(cv, hx + 32, 25, 9, 8)
    if not short:
        waves(cv, 96, 22, (6, 10, 14), facing="right")
    return cv


# ---------------------------------------------------------------------------
# P02-02 system screens


HAND = [  # a person's hand, index finger out to the right
    "...............",
    ".......####....",
    "......#wwww###.",
    "#######wwwwwww#",
    "wwwwwwwwww####.",
    "wwwwwww#www#...",
    "wwwwwww#www#...",
    "#####wwwwww#...",
    ".....######....",
]


def ble_pairing():
    """Bluetooth pairing: a hand and a paw reach for the Bluetooth sign.

    Top centre stays clear for the PIN code the firmware prints.
    """
    cv = Canvas(128, 64)
    # Person's arm in from the left, sleeve with a cuff.
    panda.thick_line(cv, (-4, 47), (34, 43), 9, "W")
    cv.rect_outlined(-1, 40, 8, 13, "L")
    cv.sprite(30, 37, HAND)
    # Bluetooth sign.
    bx, by = 60, 34
    cv.line(bx, by, bx, by + 16)
    cv.line(bx, by, bx + 4, by + 4)
    cv.line(bx + 4, by + 4, bx - 4, by + 12)
    cv.line(bx, by + 16, bx + 4, by + 12)
    cv.line(bx + 4, by + 12, bx - 4, by + 4)
    # The panda leans in from the top right and reaches with a paw.
    panda.tail(cv, (120, 60), (126, 48), (116, 40), r=5.0)
    cv.ell_outlined(94, 22, 40, 44, "M")
    cv.ell(104, 28, 22, 40, "D")
    long_arm(cv, (104, 40), (74, 44))
    cv.sprite(92, 2, panda.head("wide", "open"))
    return cv


def dfu():
    """Update & recovery mode: the panda dashes to the right.

    Top left stays clear: the firmware prints two lines there.
    """
    cv = Canvas(128, 50)
    for y, x0, x1 in ((20, 4, 50), (27, 0, 44), (34, 10, 52), (41, 2, 40), (46, 22, 56)):
        cv.line(x0, y, x1, y)
    panda.tail(cv, (60, 30), (44, 22), (34, 30), r=5.5)
    cv.ell_outlined(54, 20, 50, 22, "M")
    cv.ell(62, 30, 34, 10, "D")
    for lx in (58, 72):  # hind legs streaming back
        arm(cv, (lx + 6, 38), (lx - 6, 44), width=7)
    arm(cv, (96, 34), (120, 44), width=7)  # front paw reaching ahead
    paw(cv, 121, 44, 7, 6)
    cv.sprite(90, 12, panda.head("wide", "open"))
    return cv


def erase_pin():
    """Reset PIN: panda in shades and a suit holding a memory-wipe flasher,
    with the screen's text and button drawn in."""
    cv = Canvas(128, 64)
    hx, hy = 8, 12
    cv.ell(hx - 5, hy + 19, 45, 48, "W")
    cv.ell(hx - 4, hy + 20, 43, 46, "K")
    cv.sprite(hx + 8, hy + 25, [
        "#wwwwwww###wwwwwww#",
        ".#wwwwww###wwwwww#.",
        "..#wwwww###wwwww#..",
        "...#wwww###wwww#...",
        "....#www###www#....",
        ".....#ww###ww#.....",
        "......#w###w#......",
        ".......#####.......",
        "........###........",
    ])
    cv.sprite(hx, hy, panda.head("open", "closed"))
    for ex in (hx + 5, hx + 20):  # shades
        cv.rect(ex, hy + 11, 10, 5, "K")
        cv.rect(ex + 1, hy + 16, 8, 1, "K")
        cv.pixels([(ex + 2, hy + 12), (ex + 3, hy + 12)], "W")
    cv.rect(hx + 15, hy + 12, 5, 1, "K")
    cv.rect(hx + 3, hy + 12, 2, 1, "K")
    cv.rect(hx + 30, hy + 12, 2, 1, "K")
    # The flasher, held up in a white-rimmed paw, with a flash.
    cv.rect_outlined(46, 30, 4, 16, "W")
    cv.rect(45, 28, 6, 3, "K")
    paw(cv, 48, 44, 9, 8)
    rays(cv, 48, 26, 3, 7, angles=(200, 240, 270, 300, 340))
    # Text and the inverted "Hold to reset" button.
    pixfont.draw(cv, "Reset PIN and all", 58, 2)
    pixfont.draw(cv, "internal storage?", 56, 13)
    pixfont.draw(cv, "Exit = v", 73, 27)
    cv.rect(59, 52, 69, 12, "K")
    cv.rect(58, 53, 1, 10, "K")
    pixfont.draw(cv, "Hold to reset", 63, 54, colour="W")
    pixfont.draw(cv, ">", 122, 54, colour="W")
    return cv


def u2f(prop):
    """U2F: the panda's head and a prop on the right."""
    cv = Canvas(62, 31)
    face = {"auth": ("open", "closed"), "connect": ("wide", "open"),
            "connected": ("happy", "open"), "error": ("closed", "frown")}[prop]
    cv.sprite(1, 4, panda.head(*face, brow="sad" if prop == "error" else None))
    x = 44
    if prop == "auth":  # a key, bit downwards
        cv.ell(x + 2, 3, 10, 10, "K")
        cv.ell(x + 5, 6, 4, 4, "W")
        cv.rect(x + 6, 12, 2, 14, "K")
        cv.rect(x + 8, 20, 3, 2, "K")
        cv.rect(x + 8, 24, 4, 2, "K")
    elif prop == "connect":  # a USB plug on its cable
        cv.rect_outlined(x + 3, 2, 8, 7, "W")
        cv.rect(x + 5, 4, 1, 2, "K")
        cv.rect(x + 8, 4, 1, 2, "K")
        cv.rect(x + 2, 9, 10, 8, "K")
        cv.line(x + 7, 17, x + 7, 24)
        cv.line(x + 7, 24, x + 13, 30)
    elif prop == "connected":  # plug in a socket, and a tick
        cv.rect_outlined(x, 16, 16, 9, "L")
        cv.rect(x + 4, 6, 8, 11, "K")
        cv.line(x + 8, 0, x + 8, 6)
        cv.polyline([(x + 1, 28), (x + 4, 30), (x + 12, 26)])
    else:  # a cross
        for d in range(12):
            cv.rect(x + d, 8 + d, 2, 2, "K")
            cv.rect(x + 11 - d, 8 + d, 2, 2, "K")
    return cv


MINI_PANDA = [  # the panda's face at Flipper-screen size
    "#........#",
    "##......##",
    "#w######w#",
    "#dddddddd#",
    "dwwddddwwd",
    "dw#wddw#wd",
    "wwwww#wwww",
    ".www###ww.",
    "..wwwwww..",
]


def infrared_learn():
    """Infrared learn: a remote, its signal, and a Flipper showing the panda."""
    cv = Canvas(128, 31)
    # Remote control.
    cv.rect_outlined(0, 9, 40, 14, "W")
    cv.rect(2, 11, 1, 10, "K")
    for bx in (6, 10, 14):
        cv.rect(bx, 13, 2, 2, "K")
        cv.rect(bx, 17, 2, 2, "K")
    for bx in range(20, 37, 3):
        cv.rect(bx, 12, 2, 3, "K")
        cv.rect(bx, 17, 2, 3, "K")
    cv.rect_outlined(40, 12, 3, 8, "K")
    waves(cv, 44, 16, (4, 7), facing="right")
    # The Flipper: body, screen with the panda, d-pad.
    cv.rect_outlined(62, 2, 68, 28, "W")
    cv.pixels([(62, 2), (62, 29)], "W")
    cv.rect_outlined(72, 6, 30, 19, "K")
    cv.rect(73, 7, 28, 17, "L")
    cv.rect(82, 10, 12, 11, "W")
    cv.sprite(83, 11, MINI_PANDA)
    cv.ell(106, 8, 15, 15, "K")
    cv.ell(108, 10, 11, 11, "W")
    cv.ell(111, 13, 5, 5, "K")
    return cv


# ---------------------------------------------------------------------------
# P02-03 level-up animations


def leaf_burst(cv, cx, cy, r, n=8, phase=0, c="W"):
    for i in range(n):
        a = math.radians(360 * i / n + phase)
        x, y = round(cx + r * math.cos(a)), round(cy + r * math.sin(a))
        cv.ell(x - 3, y - 2, 6, 4, c)
        cv.pixels([(x, y)], "K")


def bust_on_black(cv, hx, hy, eyes, mouth, tier):
    cv.ell(hx - 5, hy + 17, 45, 50, "W")
    halo_head(cv, hx, hy, eyes, mouth)
    if tier >= 2:  # leaf behind the right ear, on a white rim
        cv.ell(hx + 27, hy - 3, 14, 10, "W")
        panda.bamboo_leaf(cv, hx + 28, hy + 1, length=9, up=True)
        panda.bamboo_leaf(cv, hx + 28, hy + 4, length=6, up=False)
    bust(cv, hx, hy, eyes=eyes, mouth=mouth, chest_h=46)
    if tier >= 3:  # bandana knotted under the chin
        cv.sprite(hx + 4, hy + 24, [
            "###########################",
            ".#wwwwwwwwwwwwwwwwwwwwwww#.",
            "..##wwwwwwwwwwwwwwwwwww##..",
            "....##wwwwwwwwwwwwwww##....",
            "......##wwwwwwwwwww##......",
            "........##wwwwwww##........",
            "..........##www##..........",
            "............###............",
        ])


LEVELUP_FRAMES = [
    dict(look="old", eyes="open", mouth="closed"),
    dict(look="old", eyes="wide", mouth="open", sparks=1),
    dict(look="old", eyes="closed", mouth="closed", burst=27),
    dict(look="old", eyes="closed", mouth="closed", burst=33, flash=29),
    dict(flash=70),
    dict(look="new", eyes="closed", mouth="closed", flash=36, burst=40),
    dict(look="new", eyes="wide", mouth="open", burst=46),
    dict(look="new", eyes="happy", mouth="open", sparks=2),
    dict(look="new", eyes="happy", mouth="open", sparks=1, text=True),
    dict(look="new", eyes="happy", mouth="closed", sparks=2, text=True),
    dict(look="new", eyes="happy", mouth="open", sparks=3, text=True),
]

SPARKS = {
    1: [(8, 10, True), (56, 6, False), (60, 40, False), (6, 44, False)],
    2: [(10, 18, False), (58, 12, True), (4, 36, True), (62, 50, False)],
    3: [(6, 8, False), (54, 4, True), (60, 30, True), (10, 52, False)],
}


def levelup(n, new_tier):
    f = LEVELUP_FRAMES[n]
    cv = Canvas(128, 64)
    cv.rect(0, 0, 128, 64, "K")
    hx, hy = 14, 12
    cx, cy = hx + 17, hy + 22
    if f.get("flash"):
        r = f["flash"]
        cv.ell(cx - r, cy - r, 2 * r, 2 * r, "W")
    if f.get("burst"):
        leaf_burst(cv, cx, cy, f["burst"], n=10, phase=n * 9)
    if f.get("look"):
        tier = new_tier if f["look"] == "new" else new_tier - 1
        bust_on_black(cv, hx, hy, f["eyes"], f["mouth"], tier)
    for x, y, big in SPARKS.get(f.get("sparks"), []):
        sparkle(cv, x, y, big, c="W")
    if f.get("text"):
        pixfont.draw(cv, "NEW", 80, 6, colour="W", bold=True)
        pixfont.draw(cv, "LEVEL!!!", 68, 16, colour="W", bold=True)
        cv.rect(86, 30, 26, 13, "W")
        cv.rect(87, 31, 24, 11, "K")
        cv.rect(88, 32, 22, 9, "W")
        pixfont.draw(cv, "OK", 91, 33)
        pixfont.draw(cv, ">", 104, 33)
        sx = {8: 72, 9: 118, 10: 76}[n]
        sparkle(cv, sx, 46, big=True, c="W")
    return cv


# ---------------------------------------------------------------------------
# P02-04 no SD card animation

NOSD_FRAMES = [
    dict(),
    dict(eyes="closed"),
    dict(eyes="side"),
    dict(reach=6),
    dict(reach=6, eyes="wide", mouth="open"),
    dict(reach=6, eyes="closed"),
]


def sd_card(cv, x, y):
    cv.polyline([(x, y + 6), (x + 6, y), (x + 24, y), (x + 24, y + 38),
                 (x, y + 38), (x, y + 6)])
    cv.rect(x + 1, y + 7, 23, 31, "W")
    for i in range(6):
        cv.rect(x + 7 + i * 3, y + 3, 2, 6, "K")
    cv.rect(x + 3, y + 14, 19, 15, "K")
    pixfont.draw(cv, "SD", x + 7, y + 18, colour="W")


def no_sd(n):
    """No SD card: the panda reaches across for an SD card.

    x 40-90, y 18-40 stays clear for the firmware's "Need an SD card" bubble.
    """
    f = NOSD_FRAMES[n]
    cv = Canvas(128, 49)
    sd_card(cv, 3, 4)
    hx, hy = 90, 2
    cv.ell_outlined(hx + 2, hy + 20, 40, 34, "M")
    cv.ell(hx + 10, hy + 26, 22, 30, "D")
    reach = f.get("reach", 0)
    long_arm(cv, (hx + 6, hy + 34), (38 - reach, 42))
    cv.sprite(hx, hy, panda.head(f.get("eyes", "open"), f.get("mouth", "closed")))
    return cv


# ---------------------------------------------------------------------------
# Registry: firmware path -> draw function (static) and animated folders.

STATIC = {
    "assets/icons/Dolphin/DolphinDone_80x58.png": done,
    "assets/icons/Dolphin/DolphinReadingSuccess_59x63.png": reading_success,
    "assets/icons/Dolphin/DolphinSaved_92x58.png": saved,
    "assets/icons/Dolphin/DolphinSuccess_91x55.png": success,
    "assets/icons/Dolphin/DolphinWait_59x54.png": wait,
    "assets/icons/iButton/iButtonDolphinVerySuccess_92x55.png": ibutton_success,
    "assets/icons/NFC/NFC_dolphin_emulation_51x64.png": nfc_emulation,
    "assets/icons/RFID/RFIDDolphinReceive_97x61.png": lambda: rfid(False),
    "assets/icons/RFID/RFIDDolphinSend_97x61.png": lambda: rfid(True),
    "assets/icons/SubGhz/Fishing_123x52.png": fishing,
    "assets/icons/SubGhz/Scanning_123x52.png": scanning,
    "assets/icons/SubGhz/Scanning_short_96x52.png": lambda: scanning(96),
    "assets/icons/BLE/BLE_Pairing_128x64.png": ble_pairing,
    "assets/icons/Common/DFU_128x50.png": dfu,
    "assets/icons/ErasePin/Erase_pin_128x64.png": erase_pin,
    "assets/icons/U2F/Auth_62x31.png": lambda: u2f("auth"),
    "assets/icons/U2F/Connect_me_62x31.png": lambda: u2f("connect"),
    "assets/icons/U2F/Connected_62x31.png": lambda: u2f("connected"),
    "assets/icons/U2F/Error_62x31.png": lambda: u2f("error"),
    "assets/icons/Infrared/InfraredLearnShort_128x31.png": infrared_learn,
}

ANIMATED = {}
for _i in range(len(LEVELUP_FRAMES)):
    ANIMATED[f"assets/icons/Animations/Levelup1_128x64/frame_{_i:02d}.png"] = (
        lambda i=_i: levelup(i, 2))
    ANIMATED[f"assets/icons/Animations/Levelup2_128x64/frame_{_i:02d}.png"] = (
        lambda i=_i: levelup(i, 3))
for _i in range(len(NOSD_FRAMES)):
    ANIMATED[f"assets/dolphin/internal/L1_NoSd_128x49/frame_{_i}.png"] = lambda i=_i: no_sd(i)
