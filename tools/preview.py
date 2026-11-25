"""Make an upscaled contact sheet of PNG frames, drawn like the Flipper LCD."""
import sys
import pathlib
from PIL import Image

INK = (40, 30, 20)
LCD = (255, 140, 40)


def sheet(pngs, out, scale=4, cols=2):
    frames = [Image.open(p).convert("1") for p in pngs]
    w, h = 128 * scale, 64 * scale
    pad = 6
    rows = (len(frames) + cols - 1) // cols
    img = Image.new("RGB", (cols * (w + pad) + pad, rows * (h + pad) + pad), (30, 30, 30))
    for i, f in enumerate(frames):
        f = f.resize((w, h), Image.NEAREST)
        tile = Image.new("RGB", (w, h), LCD)
        tile.paste(INK, mask=Image.eval(f.convert("L"), lambda v: 255 - v))
        img.paste(tile, (pad + (i % cols) * (w + pad), pad + (i // cols) * (h + pad)))
    img.save(out)


def gif(pngs, order, out, fps=2, scale=3):
    """Play the frames in the meta.txt order, coloured like the LCD."""
    tiles = []
    for p in pngs:
        f = Image.open(p).convert("1").resize((128 * scale, 64 * scale), Image.NEAREST)
        tile = Image.new("RGB", f.size, LCD)
        tile.paste(INK, mask=Image.eval(f.convert("L"), lambda v: 255 - v))
        tiles.append(tile.convert("P", palette=Image.ADAPTIVE, colors=4))
    seq = [tiles[i] for i in order]
    seq[0].save(out, save_all=True, append_images=seq[1:],
                duration=int(1000 / fps), loop=0)


if __name__ == "__main__":
    out = sys.argv[1]
    sheet([pathlib.Path(p) for p in sys.argv[2:]], out)
