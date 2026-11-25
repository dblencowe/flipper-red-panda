"""Draw every Red Panda animation with PhotoCraft and write the source art.

Needs Python with Pillow, and PhotoCraft installed.
    python tools\\build.py

Writes art/<anim>/frame_N.png + meta.txt and art/manifest.txt, in the
standard Flipper dolphin source layout that every firmware shares, plus
preview/<anim>.png contact sheets and preview/<anim>.gif. Firmware-specific
packaging is tools/pack.py's job.
"""
import pathlib
import shutil

import panda
import preview
from pcraft import Canvas, render

ROOT = pathlib.Path(__file__).resolve().parent.parent
ANIMS = ROOT / "art"
PREVIEW = ROOT / "preview"
# Official and Unleashed always mix their built-in L1_Tv_128x47 dolphin
# (weight 3) into the idle rotation. Weight 9 on each of our five keeps it
# to about 1 in 16 animations.
WEIGHT = 9


def scene_forest(cv, leaves=0):
    """Backdrop: the branch plus distant bamboo on the left."""
    for x, top in ((6, -1), (24, 6), (40, -1)):
        panda.bamboo_stalk(cv, x, top, 56, w=4, fill="L",
                           leaves=[(top + 14 + leaves, 1, True), (top + 30, -1, False)])
    panda.branch(cv)


# Each animation: frames (list of draw functions), meta settings, bubbles.
def idle():
    def f(**kw):
        def draw(cv):
            scene_forest(cv, leaves=kw.pop("leaves", 0))
            panda.sitting_panda(cv, 74, 4, **kw)
        return draw
    frames = [
        f(),
        f(eyes="closed"),
        f(eyes="side", tail_tip=(-4, 2), leaves=1),
        f(eyes="happy", mouth="open", tail_tip=(-2, 1)),
        f(eyes="happy", mouth="closed", tail_tip=(-4, 2), leaves=1),
    ]
    meta = dict(passive=8, active=4, order="0 0 0 1 0 0 2 2 3 4 3 4", cycles=2,
                rate=2, duration=360, cooldown=5)
    bubbles = [
        (0, 2, 22, "Hi! I'm a\nred panda!", "Right", "Center", 9, 15),
        (1, 2, 22, "Not a\nraccoon.", "Right", "Center", 9, 11),
        (1, 2, 22, "Not a fox.", "Right", "Center", 12, 13),
        (1, 2, 22, "Red panda!", "Right", "Center", 14, 15),
    ]
    return "RP_Idle_128x64", frames, meta, bubbles


def sleep():
    def f(breathe, z, stars, sway=0, eyes="closed"):
        def draw(cv):
            panda.moon(cv, 104, 3)
            for i, (sx, sy) in enumerate(((10, 6), (34, 14), (60, 4), (86, 12), (120, 22))):
                panda.star(cv, sx, sy, big=(i + stars) % 3 == 0)
            panda.branch(cv)
            panda.sleeping_panda(cv, 16, 23, breathe=breathe, eyes=eyes, tail_sway=sway)
            for i, (zx, zy, size) in enumerate(z):
                panda.zzz(cv, zx, zy, size)
        return draw
    frames = [
        f(0, [(44, 18, "small")], 0),
        f(1, [(46, 14, "small"), (40, 18, "small")], 1),
        f(1, [(50, 10, "big"), (44, 15, "small")], 2, sway=1),
        f(0, [(54, 5, "big"), (48, 11, "small"), (42, 18, "small")], 0, sway=1),
        f(0, [], 1, eyes="side"),
    ]
    meta = dict(passive=4, active=2, order="0 1 2 3 4 0", cycles=2,
                rate=2, duration=360, cooldown=7)
    bubbles = [(0, 2, 20, "Five more\nminutes...", "Right", "Center", 4, 7)]
    return "RP_Sleep_128x64", frames, meta, bubbles


def bamboo():
    def f(bite, mouth, eyes="open"):
        def draw(cv):
            scene_forest(cv)
            panda.eating_panda(cv, 74, 4, bite=bite, mouth=mouth, eyes=eyes)
        return draw
    frames = [
        f(0, "closed"),
        f(0, "chew"),
        f(1, "closed", eyes="happy"),
        f(1, "chew", eyes="happy"),
        f(2, "closed", eyes="happy"),
        f(2, "chew", eyes="closed"),
    ]
    meta = dict(passive=4, active=4, order="0 1 0 1 2 3 4 5", cycles=2,
                rate=2, duration=360, cooldown=5)
    bubbles = [
        (0, 2, 22, "Nom nom\nnom...", "Right", "Center", 4, 7),
        (0, 2, 22, "Bamboo is\nthe best!", "Right", "Center", 8, 11),
    ]
    return "RP_Bamboo_128x64", frames, meta, bubbles


def rawr():
    def f(arms, eyes, mouth, sway=0):
        def draw(cv):
            scene_forest(cv)
            panda.standing_panda(cv, 72, 2, arms=arms, eyes=eyes, mouth=mouth, sway=sway)
        return draw
    frames = [
        f("down", "open", "closed"),
        f("down", "side", "closed", sway=-2),
        f("half", "wide", "closed"),
        f("up", "wide", "open"),
        f("up", "wide", "open", sway=-2),
        f("up", "happy", "closed"),
    ]
    meta = dict(passive=4, active=6, order="0 0 1 0 2 3 4 3 4 5", cycles=1,
                rate=2, duration=360, cooldown=7)
    bubbles = [
        (0, 2, 22, "RAWR!", "Right", "Center", 5, 8),
        (1, 2, 22, "Was that\nscary?", "Right", "Center", 9, 9),
    ]
    return "RP_Rawr_128x64", frames, meta, bubbles


def laptop():
    def f(phase, eyes="open", screen=0):
        def draw(cv):
            scene_forest(cv)
            panda.laptop_panda(cv, 76, 4, phase=phase, eyes=eyes, screen=screen)
        return draw
    frames = [
        f(0),
        f(1),
        f(0, screen=1),
        f(1, eyes="side", screen=1),
        f(0, eyes="happy", screen=1),
    ]
    meta = dict(passive=4, active=4, order="0 1 0 1 2 3 2 4", cycles=2,
                rate=2, duration=360, cooldown=7)
    bubbles = [
        (0, 2, 22, "Hacking the\nbamboo grid", "Right", "Center", 4, 7),
        (0, 2, 22, "Access\ngranted!", "Right", "Center", 8, 11),
    ]
    return "RP_Laptop_128x64", frames, meta, bubbles


ALL = [idle, sleep, bamboo, rawr, laptop]


def meta_txt(meta, bubbles):
    lines = [
        "Filetype: Flipper Animation", "Version: 1", "",
        "Width: 128", "Height: 64",
        f"Passive frames: {meta['passive']}",
        f"Active frames: {meta['active']}",
        f"Frames order: {meta['order']}",
        f"Active cycles: {meta['cycles']}",
        f"Frame rate: {meta['rate']}",
        f"Duration: {meta['duration']}",
        f"Active cooldown: {meta['cooldown']}", "",
        f"Bubble slots: {len({b[0] for b in bubbles})}",
    ]
    for slot, x, y, text, ah, av, start, end in bubbles:
        lines += ["", f"Slot: {slot}", f"X: {x}", f"Y: {y}",
                  "Text: " + text.replace("\n", "\\n"),
                  f"AlignH: {ah}", f"AlignV: {av}",
                  f"StartFrame: {start}", f"EndFrame: {end}"]
    return "\n".join(lines) + "\n"


def manifest_txt(names):
    lines = ["Filetype: Flipper Animation Manifest", "Version: 1"]
    for name in names:
        lines += ["", f"Name: {name}", "Min butthurt: 0", "Max butthurt: 14",
                  "Min level: 1", "Max level: 30", f"Weight: {WEIGHT}"]
    return "\n".join(lines) + "\n"


def check(name, frames, meta, bubbles):
    order = [int(i) for i in meta["order"].split()]
    assert len(order) == meta["passive"] + meta["active"], name
    assert max(order) == len(frames) - 1 and min(order) == 0, name
    assert set(order) == set(range(len(frames))), (name, "unused frame")
    total = meta["passive"] + meta["active"] * meta["cycles"]
    for b in bubbles:
        assert 0 <= b[6] <= b[7] < total, (name, b)


def main():
    if ANIMS.exists():
        shutil.rmtree(ANIMS)
    ANIMS.mkdir(parents=True)
    PREVIEW.mkdir(exist_ok=True)
    jobs, names, sheets = [], [], []
    for make in ALL:
        name, frames, meta, bubbles = make()
        check(name, frames, meta, bubbles)
        names.append(name)
        (ANIMS / name).mkdir()
        (ANIMS / name / "meta.txt").write_text(meta_txt(meta, bubbles), newline="\n")
        rels = []
        for i, draw in enumerate(frames):
            cv = Canvas()
            draw(cv)
            rel = f"art/{name}/frame_{i}.png"
            jobs.append((rel, cv))
            rels.append(ROOT / rel)
        order = [int(i) for i in meta["order"].split()]
        passive, active = order[:meta["passive"]], order[meta["passive"]:]
        sheets.append((name, rels, passive * 2 + active * meta["cycles"] + passive))
    (ANIMS / "manifest.txt").write_text(manifest_txt(names), newline="\n")
    n = render(jobs, ROOT)
    for name, rels, timeline in sheets:
        preview.sheet(rels, PREVIEW / f"{name}.png", scale=3, cols=3)
        preview.gif(rels, timeline, PREVIEW / f"{name}.gif")
    print(f"Rendered {len(jobs)} frames in {len(names)} animations "
          f"({n} PhotoCraft requests)")


if __name__ == "__main__":
    main()
