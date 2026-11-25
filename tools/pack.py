"""Package art/ for each firmware into dist/.

Needs Python with Pillow and heatshrink2 (pip install pillow heatshrink2).
    python tools\\pack.py

Outputs:
  dist/sd-dolphin/dolphin/       official, Unleashed, and Momentum with Asset
                                 Pack set to Default. Copy to SD/dolphin.
  dist/momentum-asset-pack/RedPanda/
                                 Momentum asset pack. Copy to SD/asset_packs.

Frames are converted the same way as official firmware's
scripts/flipper/assets/icon.py file2image (checked against 1.5.1, and
Unleashed unlshd-095 is identical): PNG to 1-bit XBM, heatshrink with window
8 and lookahead 4, header 01 00 + 2-byte length, or 00 + raw bits if
compressing doesn't help. Every output is decoded again and compared with
its PNG before the script reports success.
"""
import io
import pathlib
import shutil

import heatshrink2
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART = ROOT / "art"
DIST = ROOT / "dist"


def png_to_bm(path):
    with Image.open(path) as im:
        bw = ImageOps.invert(im.convert("1"))
        with io.BytesIO() as out:
            bw.save(out, format="XBM")
            xbm = out.getvalue().decode().strip()
    data = xbm.replace("\n", "").replace(" ", "").split("=")[1][:-1]
    raw = bytearray.fromhex(data[1:-1].replace(",", " ").replace("0x", ""))
    enc = bytearray(heatshrink2.compress(raw, window_sz2=8, lookahead_sz2=4))
    enc = bytearray([len(enc) & 0xFF, len(enc) >> 8]) + enc
    if len(enc) + 2 < len(raw) + 1:
        return bytes(b"\x01\x00" + enc)
    return bytes(b"\x00" + raw)


def check_bm(bm, png):
    """Decode a .bm the way the firmware does and compare it with the PNG."""
    raw = bm.read_bytes()
    with Image.open(png) as im:
        im = im.convert("L")
        w, h = im.size
        stride = (w + 7) // 8
        assert len(raw) <= stride * h + 1, f"{bm}: larger than the firmware accepts"
        if raw[0] == 1:
            data = heatshrink2.decompress(raw[4:], window_sz2=8, lookahead_sz2=4)
        else:
            data = raw[1:]
        assert len(data) == stride * h, f"{bm}: wrong decoded size"
        for y in range(h):
            for x in range(w):
                lit = (data[y * stride + x // 8] >> (x % 8)) & 1
                assert lit == (im.getpixel((x, y)) < 128), f"{bm}: pixel {x},{y}"


def anim_names():
    text = (ART / "manifest.txt").read_text()
    return [l.split(":", 1)[1].strip() for l in text.splitlines() if l.startswith("Name:")]


def write_tree(out):
    """manifest.txt plus one folder per animation with meta.txt and frame_N.bm."""
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    lf = lambda p: p.read_bytes().replace(b"\r\n", b"\n")  # noqa: E731
    (out / "manifest.txt").write_bytes(lf(ART / "manifest.txt"))
    frames = 0
    for name in anim_names():
        src, dst = ART / name, out / name
        dst.mkdir()
        (dst / "meta.txt").write_bytes(lf(src / "meta.txt"))
        for png in sorted(src.glob("frame_*.png")):
            bm = dst / (png.stem + ".bm")
            bm.write_bytes(png_to_bm(png))
            check_bm(bm, png)
            frames += 1
    return frames


def main():
    targets = {
        "official / Unleashed (SD/dolphin)": DIST / "sd-dolphin" / "dolphin",
        "Momentum asset pack (SD/asset_packs/RedPanda/Anims)":
            DIST / "momentum-asset-pack" / "RedPanda" / "Anims",
    }
    for label, out in targets.items():
        n = write_tree(out)
        print(f"{label}: {n} frames in {len(anim_names())} animations -> "
              f"{out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
