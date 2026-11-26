"""Drive PhotoCraft's headless engine (photocraft-cli serve) to draw 1-bit frames.

A Canvas collects drawing operations (rectangles, ellipses, pixel sprites).
render() replays them in one PhotoCraft session: each frame is a new 128x64
greyscale document, every shape becomes a selection plus an Edit > Fill, and
Image > Mode > Bitmap (pattern dither) turns it into 1-bit. Grey fills come out
as a fixed ordered-dither texture, which is how fur is shaded.
"""
import json
import pathlib
import subprocess

PHOTOCRAFT = r"C:\Program Files\PhotoCraft\photocraft-cli.exe"

# Palette. K and W stay solid; F and L dither to a fixed texture.
COLOURS = {
    "K": "#000000",  # ink (lit pixel on the Flipper)
    "W": "#ffffff",  # paper
    "F": "#c8c8c8",  # fur: sparse dot grid
    "L": "#e6e6e6",  # light: very sparse dots
    "M": "#a0a0a0",  # medium: denser grid
}

# Sprite legend: char -> palette key. Space and '.' are transparent.
LEGEND = {"#": "K", "w": "W", "f": "F", "l": "L", "m": "M"}


class Canvas:
    def __init__(self, width=128, height=64):
        self.width = width
        self.height = height
        self.ops = []

    # Primitive shapes -----------------------------------------------------
    def rect(self, x, y, w, h, c):
        if w > 0 and h > 0:
            self.ops.append(("rect", int(x), int(y), int(w), int(h), c))

    def ell(self, x, y, w, h, c):
        if w > 0 and h > 0:
            self.ops.append(("ell", int(x), int(y), int(w), int(h), c))

    def ell_outlined(self, x, y, w, h, fill, line="K"):
        self.ell(x, y, w, h, line)
        self.ell(x + 1, y + 1, w - 2, h - 2, fill)

    def rect_outlined(self, x, y, w, h, fill, line="K"):
        self.rect(x, y, w, h, line)
        self.rect(x + 1, y + 1, w - 2, h - 2, fill)

    def pixels(self, pts, c):
        pts = sorted(set((int(x), int(y)) for x, y in pts))
        if pts:
            self.ops.append(("px", pts, c))

    def line(self, x0, y0, x1, y1, c="K"):
        self.pixels(bresenham(x0, y0, x1, y1), c)

    def polyline(self, pts, c="K"):
        out = []
        for (a, b), (d, e) in zip(pts, pts[1:]):
            out += bresenham(a, b, d, e)
        self.pixels(out, c)

    def sprite(self, x, y, rows, flip=False):
        """Paint a character-grid sprite. See LEGEND."""
        by_colour = {}
        for dy, row in enumerate(rows):
            if flip:
                row = row[::-1]
            for dx, ch in enumerate(row):
                key = LEGEND.get(ch)
                if key:
                    by_colour.setdefault(key, []).append((x + dx, y + dy))
        # Paint in a fixed order so outlines win over fills where they touch.
        order = sorted(by_colour, key=lambda k: (k == "W", k == "K", k))
        for key in order:
            self.pixels(by_colour[key], key)


def bresenham(x0, y0, x1, y1):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    pts = []
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1:
            return pts
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def _runs(pts):
    """Merge sorted (x, y) pixels into horizontal runs (x, y, w)."""
    by_row = {}
    for x, y in pts:
        by_row.setdefault(y, []).append(x)
    for y, xs in by_row.items():
        xs.sort()
        start = prev = xs[0]
        for x in xs[1:]:
            if x == prev + 1:
                prev = x
                continue
            yield start, y, prev - start + 1
            start = prev = x
        yield start, y, prev - start + 1


def _requests(canvas, out_rel):
    req = [("doc.new", {"width": canvas.width, "height": canvas.height,
                        "mode": "gray", "background": "white"})]

    def cmd(name, params):
        req.append(("engine.execute", {"command": name, "params": params}))

    W, H = canvas.width, canvas.height
    for op in canvas.ops:
        kind = op[0]
        if kind in ("rect", "ell"):
            _, x, y, w, h, c = op
            if x >= W or y >= H or x + w <= 0 or y + h <= 0:
                continue  # wholly off the canvas: nothing to select
            cmd("select.rect", {"x": x, "y": y, "width": w, "height": h,
                                "ellipse": kind == "ell", "antiAlias": False})
        else:
            _, pts, c = op
            pts = [(x, y) for x, y in pts if 0 <= x < W and 0 <= y < H]
            if not pts:
                continue
            first = True
            for x, y, w in _runs(pts):
                cmd("select.rect", {"x": x, "y": y, "width": w, "height": 1,
                                    "mode": "replace" if first else "add",
                                    "antiAlias": False})
                first = False
        cmd("edit.fill", {"contents": "color", "color": COLOURS[c]})
        cmd("select.deselect", {})
    cmd("image.mode.bitmap", {"method": "pattern"})
    req.append(("doc.save", {"path": out_rel}))
    req.append(("doc.close", {}))
    return req


def render(jobs, root):
    """jobs: list of (relative_png_path, Canvas). Paths are relative to root."""
    root = pathlib.Path(root)
    lines = []
    n = 0
    for rel, canvas in jobs:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        for method, params in _requests(canvas, rel.replace("\\", "/")):
            n += 1
            lines.append(json.dumps({"id": n, "method": method, "params": params}))
    proc = subprocess.run(
        [PHOTOCRAFT, "serve", "--automation-write-root", str(root)],
        input="\n".join(lines) + "\n", capture_output=True, text=True,
        cwd=str(root), timeout=600,
    )
    errors = [l for l in proc.stdout.splitlines() if '"ok":false' in l]
    if errors or proc.returncode not in (0,):
        raise RuntimeError("PhotoCraft errors:\n" + "\n".join(errors[:10]) +
                           "\n" + proc.stderr[-2000:])
    return n
