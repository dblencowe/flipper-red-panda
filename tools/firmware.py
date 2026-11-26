"""Put the red panda into a firmware source tree before you build it.

    python tools\\firmware.py <path to an official or Unleashed checkout>

Copies art/firmware/** over the matching dolphin pictures (each must exist
in the tree with the same size), and makes the red panda animations the
firmware's SD resources: art/RP_* go to assets/dolphin/external/ and
art/manifest.txt replaces its manifest, so an update installs the pandas to
SD/dolphin itself. Stock animation folders stay in the tree, unlisted.

Use --icons-only to leave the SD resources alone. Momentum is not supported
here: its pictures differ, and its asset packs swap them without a build
(see dist/momentum-asset-pack).
"""
import argparse
import pathlib
import shutil
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART = ROOT / "art"
PICTURES = ART / "firmware"


def lf_copy(src, dst):
    dst.write_bytes(src.read_bytes().replace(b"\r\n", b"\n"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("tree", type=pathlib.Path)
    ap.add_argument("--icons-only", action="store_true")
    args = ap.parse_args()
    tree = args.tree.resolve()

    if not (tree / "assets" / "icons" / "Passport" / "passport_happy1_46x49.png").exists():
        sys.exit(f"{tree} doesn't look like an official or Unleashed checkout "
                 "(no assets/icons/Passport/passport_happy1_46x49.png). For "
                 "Momentum, use the asset pack instead.")

    problems, copied = [], 0
    for src in sorted(PICTURES.rglob("*.png")):
        rel = src.relative_to(PICTURES)
        dst = tree / rel
        if not dst.exists():
            problems.append(f"missing in tree: {rel.as_posix()}")
            continue
        with Image.open(src) as a, Image.open(dst) as b:
            if a.size != b.size:
                problems.append(f"size differs: {rel.as_posix()} {a.size} vs {b.size}")
    if problems:
        sys.exit("Nothing copied:\n  " + "\n  ".join(problems))
    for src in sorted(PICTURES.rglob("*.png")):
        shutil.copyfile(src, tree / src.relative_to(PICTURES))
        copied += 1
    print(f"pictures: {copied} replaced")

    if args.icons_only:
        return
    external = tree / "assets" / "dolphin" / "external"
    names = [l.split(":", 1)[1].strip()
             for l in (ART / "manifest.txt").read_text().splitlines()
             if l.startswith("Name:")]
    for name in names:
        dst = external / name
        if dst.exists():
            shutil.rmtree(dst)
        dst.mkdir(parents=True)
        lf_copy(ART / name / "meta.txt", dst / "meta.txt")
        for png in sorted((ART / name).glob("frame_*.png")):
            shutil.copyfile(png, dst / png.name)
    lf_copy(ART / "manifest.txt", external / "manifest.txt")
    print(f"SD animations: {len(names)} copied, manifest lists only them")


if __name__ == "__main__":
    main()
