"""Draw the red panda pictures that firmwares compile in, with PhotoCraft.

    python tools\\icons.py

Writes art/firmware/<path>.png, where <path> is the picture's path in the
official and Unleashed firmware source trees (same name and size as the
dolphin it replaces), plus preview/firmware.png, a 4x contact sheet.
Installing them is tools/firmware.py's job.
"""
import pathlib
import shutil

from PIL import Image

import panda
import scenes2
from pcraft import Canvas, render

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "art" / "firmware"
PREVIEW = ROOT / "preview"

INK = (40, 30, 20)
LCD = (255, 140, 40)


# ---------------------------------------------------------------------------
# Shared pieces


def bust(cv, hx, hy, eyes="open", mouth="closed", brow=None, chest_h=40):
    """Head and shoulders: russet shoulders, dark chest, the head on top."""
    cv.ell_outlined(hx - 3, hy + 19, 41, chest_h, "M")
    cv.ell(hx + 7, hy + 23, 21, chest_h, "D")
    cv.sprite(hx, hy, panda.head(eyes, mouth, brow=brow))


def tear(cv, x, y):
    """A falling tear: white drop with an ink rim."""
    cv.sprite(x, y, ["..#..", ".#w#.", "#www#", "#www#", ".###."])


def paw_up(cv, sx, sy, hx, hy):
    """An arm from the shoulder (sx, sy) to a raised paw at (hx, hy)."""
    panda.thick_line(cv, (sx, sy), (hx, hy), 9, "W", outline=None)
    panda.thick_line(cv, (sx, sy), (hx, hy), 7, "K", outline=None)
    cv.ell(hx - 5, hy - 6, 11, 10, "W")
    cv.ell(hx - 4, hy - 5, 9, 8, "K")
    # Pads: three white toe dots and a palm.
    cv.pixels([(hx - 2, hy - 3), (hx, hy - 4), (hx + 2, hy - 3)], "W")
    cv.rect(hx - 1, hy - 1, 3, 2, "W")


# ---------------------------------------------------------------------------
# Pictures


def power_off():
    """Settings > Power > Power Off: a crying panda hugging its tail."""
    cv = Canvas(49, 54)
    panda.tail(cv, (36, 50), (48, 40), (40, 24), r=5.5)
    cv.ell_outlined(8, 23, 33, 31, "M")
    cv.ell(15, 28, 19, 26, "D")
    for px in (10, 26):  # paws folded in front
        cv.ell(px - 1, 40, 13, 9, "W")
        cv.ell(px, 41, 11, 7, "K")
    cv.sprite(7, 3, panda.head("closed", "frown", brow="sad"))
    # Tears run down the white cheeks and drip off the face.
    tear(cv, 9, 18)
    tear(cv, 35, 18)
    tear(cv, 2, 26)
    tear(cv, 43, 29)
    return cv


PASSPORT_FACES = {
    "happy": dict(eyes="happy", mouth="open"),
    "okay": dict(eyes="open", mouth="closed"),
    "bad": dict(eyes="open", mouth="frown", brow="angry"),
}


def passport(mood, tier):
    """Passport portrait: bust in a black frame. Higher tiers wear more."""
    cv = Canvas(46, 49)
    bust(cv, 5, 7, **PASSPORT_FACES[mood])
    if tier >= 3:  # bandana knotted under the chin
        cv.sprite(9, 31, [
            "###########################",
            ".#wwwwwwwwwwwwwwwwwwwwwww#.",
            "..##wwwwwwwwwwwwwwwwwww##..",
            "....##wwwwwwwwwwwwwww##....",
            "......##wwwwwwwwwww##......",
            "........##wwwwwww##........",
            "..........##www##..........",
            "............###............",
        ])
    if tier >= 2:  # a bamboo leaf tucked behind the right ear
        panda.bamboo_leaf(cv, 33, 6, length=9, up=True)
        panda.bamboo_leaf(cv, 33, 9, length=6, up=False)
    # Frame last, so nothing draws over it: 1px ink, rounded corners.
    for x, y, w, h in ((0, 0, 46, 1), (0, 48, 46, 1), (0, 0, 1, 49), (45, 0, 1, 49)):
        cv.rect(x, y, w, h, "K")
    cv.pixels([(0, 0), (45, 0), (0, 48), (45, 48)], "W")
    return cv


def warning():
    """Warnings: the panda holds up a paw. Upstream ships a mirrored copy."""
    cv = Canvas(45, 42)
    cv.ell_outlined(2, 25, 37, 30, "M")
    cv.ell(11, 29, 19, 26, "D")
    paw_up(cv, 30, 32, 37, 10)
    cv.sprite(1, 6, panda.head("wide", "open"))
    # Alert marks above the paw.
    cv.line(37, 0, 37, 1)
    cv.line(32, 1, 33, 2)
    cv.line(42, 1, 41, 2)
    return cv


def mafia():
    """Deleted / PIN removed: sharp-dressed panda, shades and a thumbs up.

    The top right (x >= 70, y <= 22) stays clear: the screens print
    "Deleted" and "Removed" there.
    """
    cv = Canvas(119, 62)
    hx, hy = 30, 13
    panda.tail(cv, (hx + 4, hy + 46), (hx - 26, hy + 52), (hx - 22, hy + 24), r=6.0)
    # Suit: black jacket with white lapel edges, white shirt, black tie.
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
    # Thumbs up on the right, below the caption area: sleeve, white cuff,
    # then a black paw with the thumb raised.
    sx, sy = hx + 32, hy + 36
    px, py = hx + 42, hy + 26  # top-left of the fist
    panda.thick_line(cv, (sx, sy), (px + 2, py + 8), 10, "K", outline="W")
    cv.rect_outlined(px - 1, py + 2, 3, 9, "W")
    cv.sprite(px + 2, py - 7, [
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
        "#w#wwwwww#",
        "#w#######w",
        "#wwwwwwww#",
        ".########.",
    ])
    # Head, then shades and the fedora over it.
    cv.sprite(hx, hy, panda.head("open", "closed"))
    for ex in (hx + 5, hx + 20):
        cv.rect(ex, hy + 11, 10, 5, "K")
        cv.rect(ex + 1, hy + 16, 8, 1, "K")
        cv.pixels([(ex + 2, hy + 12), (ex + 3, hy + 12)], "W")
    cv.rect(hx + 15, hy + 12, 5, 1, "K")
    cv.rect(hx + 3, hy + 12, 2, 1, "K")
    cv.rect(hx + 30, hy + 12, 2, 1, "K")
    # Fedora: dark crown with a pinch, white band, wide black brim.
    cv.ell_outlined(hx + 6, hy - 12, 23, 16, "D")
    cv.rect_outlined(hx + 6, hy - 4, 23, 4, "W")
    cv.ell(hx - 5, hy, 45, 7, "K")
    cv.rect(hx + 16, hy - 12, 3, 4, "W")
    cv.rect(hx + 17, hy - 12, 1, 4, "K")
    return cv


# The TV animation keeps upstream's name and meta.txt timing:
# 6 passive frames, then 2 active frames while the bubble shows.
TV_FRAMES = [
    dict(),
    dict(eyes="closed"),
    dict(reach=True),
    dict(snack=True, mouth="chew"),
    dict(eyes="happy", mouth="chew"),
    dict(tail=3),
    dict(eyes="wide", mouth="open"),
    dict(eyes="happy", mouth="open", tail=2),
]


def tv(n):
    f = TV_FRAMES[n]
    cv = Canvas(128, 47)
    # Floor line.
    cv.rect(0, 46, 128, 1, "K")
    # TV on a low stand, antenna on top, the screen flickers.
    cv.line(14, 4, 21, 13)
    cv.line(30, 2, 23, 13)
    cv.ell(17, 11, 10, 5, "K")
    cv.rect_outlined(2, 15, 42, 28, "W")
    cv.rect_outlined(5, 18, 30, 22, "K")
    cv.rect(7, 20, 26, 18, "F" if n % 2 else "L")
    cv.rect(36, 20, 5, 5, "K")
    cv.rect(37, 28, 4, 1, "K")
    cv.rect(37, 31, 4, 1, "K")
    cv.rect(37, 34, 4, 1, "K")
    cv.rect(6, 43, 4, 3, "K")
    cv.rect(36, 43, 4, 3, "K")
    # Armchair: tall back behind the panda.
    cv.rect_outlined(78, 6, 44, 41, "L")
    cv.rect(80, 8, 40, 2, "W")
    # Panda in the chair, tail curled up the right-hand side.
    hx, hy = 82, 2
    panda.tail(cv, (hx + 26, hy + 38), (hx + 46, hy + 38), (hx + 38 + f.get("tail", 0), hy + 18), r=5.0)
    cv.ell_outlined(hx + 4, hy + 19, 27, 28, "M")
    cv.ell(hx + 9, hy + 24, 17, 22, "D")
    cv.sprite(hx, hy, panda.head(f.get("eyes", "open"), f.get("mouth", "closed")))
    # Seat cushion and the two arms of the chair, in front of the body.
    cv.rect_outlined(74, 38, 54, 9, "W")
    cv.rect_outlined(72, 28, 10, 19, "W")
    cv.rect_outlined(119, 28, 9, 19, "W")
    cv.line(74, 31, 79, 31)
    cv.line(121, 31, 126, 31)
    # Bowl of berries on a little table beside the chair.
    cv.rect_outlined(50, 40, 22, 3, "W")
    cv.rect(53, 43, 2, 3, "K")
    cv.rect(67, 43, 2, 3, "K")
    for bx, by in ((53, 29), (57, 27), (61, 29), (65, 28), (55, 31), (63, 31)):
        cv.ell(bx, by, 5, 5, "K")
        cv.pixels([(bx + 1, by + 1)], "W")
    cv.ell(51, 31, 18, 10, "K")
    cv.ell(52, 31, 16, 8, "W")
    cv.rect(51, 31, 18, 2, "W")
    cv.rect(52, 33, 16, 1, "K")
    # Paw: resting on the chair arm, in the bowl, or bringing a berry up.
    shoulder = (hx + 8, hy + 27)
    if f.get("reach"):
        hand = (62, 30)
    elif f.get("snack"):
        hand = (hx + 12, hy + 24)
    else:
        hand = None
    if hand is None:  # paw resting on the chair arm
        cv.ell(73, 24, 10, 7, "W")
        cv.ell(74, 25, 8, 5, "K")
        return cv
    panda.thick_line(cv, shoulder, hand, 8, "W", outline=None)
    panda.thick_line(cv, shoulder, hand, 6, "K", outline=None)
    cv.ell(hand[0] - 4, hand[1] - 3, 8, 6, "K")
    if f.get("snack"):  # the berry, held up to the mouth
        cv.ell(hand[0] - 2, hand[1] - 7, 5, 5, "K")
        cv.pixels([(hand[0] - 1, hand[1] - 6)], "W")
    return cv


JOBS = {
    "assets/icons/Settings/dolph_cry_49x54.png": power_off,
    "assets/icons/Dolphin/WarningDolphin_45x42.png": warning,
    "assets/icons/Dolphin/DolphinMafia_119x62.png": mafia,
}
for _mood in ("happy", "okay", "bad"):
    for _tier in (1, 2, 3):
        JOBS[f"assets/icons/Passport/passport_{_mood}{_tier}_46x49.png"] = (
            lambda m=_mood, t=_tier: passport(m, t))
for _n in range(len(TV_FRAMES)):
    JOBS[f"assets/dolphin/internal/L1_Tv_128x47/frame_{_n}.png"] = lambda n=_n: tv(n)

PHASE1 = list(JOBS)
JOBS.update(scenes2.STATIC)
JOBS.update(scenes2.ANIMATED)

MIRRORED = {  # upstream ships these as left-right mirrors of another picture
    "assets/icons/Dolphin/WarningDolphinFlip_45x42.png":
        "assets/icons/Dolphin/WarningDolphin_45x42.png",
}


def contact_sheet(paths, out, scale=4, width=1100, pad=8):
    ims = [Image.open(p).convert("1") for p in paths]
    x = y = pad
    row_h = 0
    places = []
    for im in ims:
        w, h = im.size[0] * scale, im.size[1] * scale
        if x + w > width:
            x, y, row_h = pad, y + row_h + pad, 0
        places.append((x, y))
        x += w + pad
        row_h = max(row_h, h)
    sheet = Image.new("RGB", (width, y + row_h + pad), (30, 30, 30))
    for im, pos in zip(ims, places):
        big = im.resize((im.size[0] * scale, im.size[1] * scale), Image.NEAREST)
        tile = Image.new("RGB", big.size, LCD)
        tile.paste(INK, mask=Image.eval(big.convert("L"), lambda v: 255 - v))
        sheet.paste(tile, pos)
    sheet.save(out)


def anim_gif(folder, names, order, out, scale=3, fps=2):
    """Play animation frames in the firmware's order, coloured like the LCD."""
    tiles = []
    for name in names:
        im = Image.open(folder / name).convert("1")
        big = im.resize((im.size[0] * scale, im.size[1] * scale), Image.NEAREST)
        tile = Image.new("RGB", big.size, LCD)
        tile.paste(INK, mask=Image.eval(big.convert("L"), lambda v: 255 - v))
        tiles.append(tile.convert("P", palette=Image.ADAPTIVE, colors=4))
    seq = [tiles[i] for i in order]
    seq[0].save(out, save_all=True, append_images=seq[1:],
                duration=int(1000 / fps), loop=0)


GIFS = {  # folder: (frame names, play order)
    "assets/dolphin/internal/L1_Tv_128x47":
        ([f"frame_{n}.png" for n in range(8)], (0, 1, 2, 3, 4, 5, 6, 7, 6, 7)),
    "assets/dolphin/internal/L1_NoSd_128x49":
        ([f"frame_{n}.png" for n in range(6)], (0, 1, 0, 1, 0, 2, 3, 4, 3, 5)),
    "assets/icons/Animations/Levelup1_128x64":
        ([f"frame_{n:02d}.png" for n in range(11)], tuple(range(11)) + (8, 9, 10) * 2),
    "assets/icons/Animations/Levelup2_128x64":
        ([f"frame_{n:02d}.png" for n in range(11)], tuple(range(11)) + (8, 9, 10) * 2),
}


def main(only=None):
    """Render everything, or with an argument only the jobs whose path
    contains it (written in place, preview in preview/_wip.png)."""
    if only:
        picked = {k: v for k, v in JOBS.items() if only in k}
        render([(str(pathlib.Path("art/firmware") / k), fn()) for k, fn in picked.items()], ROOT)
        contact_sheet([OUT / k for k in picked], PREVIEW / "_wip.png", width=1600)
        print(f"{len(picked)} pictures -> preview/_wip.png")
        return
    if OUT.exists():
        shutil.rmtree(OUT)
    jobs = [(str(pathlib.Path("art/firmware") / rel), fn()) for rel, fn in JOBS.items()]
    render(jobs, ROOT)
    for dst, src in MIRRORED.items():
        Image.open(OUT / src).transpose(Image.FLIP_LEFT_RIGHT).save(OUT / dst)
    # Keep the TV animation's upstream meta.txt next to its frames.
    meta = ROOT / "tools" / "L1_Tv_128x47.meta.txt"
    shutil.copyfile(meta, OUT / "assets/dolphin/internal/L1_Tv_128x47/meta.txt")
    PREVIEW.mkdir(exist_ok=True)
    phase1 = PHASE1 + list(MIRRORED)
    phase1.sort(key=lambda p: ("L1_Tv" in p, p))
    contact_sheet([OUT / p for p in phase1], PREVIEW / "firmware.png")
    contact_sheet([OUT / p for p in scenes2.STATIC], PREVIEW / "firmware2.png", width=1600)
    for folder, (names, order) in GIFS.items():
        anim_gif(OUT / folder, names, order, PREVIEW / (pathlib.Path(folder).name + ".gif"))
    print(f"{len(JOBS) + len(MIRRORED)} pictures in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
