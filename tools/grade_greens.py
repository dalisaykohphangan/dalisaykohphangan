#!/usr/bin/env python3
"""Grade the greens (plants, grass, leaves) in site photos towards the site's
deeper, cooler green, leaving everything else untouched.

Only pixels whose hue is yellow-green to green AND that are reasonably
saturated are changed; the change fades out softly at the edges so the photo
still looks natural. Originals are kept in tools/photo-originals/ (not served)
so the grade can always be re-run from scratch or undone.

    python3 tools/grade_greens.py assets/img/ext-01.jpg ...   # grade these
    python3 tools/grade_greens.py --all                       # every site photo
    python3 tools/grade_greens.py --restore                   # put originals back
"""
import glob
import os
import shutil
import sys

from PIL import Image, ImageChops, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(ROOT, "tools", "photo-originals")

# PIL HSV hue runs 0-255 for 0-360 degrees.
HUE_SHIFT = 12       # about +17 degrees: yellow-green moves towards a deeper green
SAT = 0.78           # less saturated (less "neon" yellow)
VAL = 0.80           # darker
# Green band: starts above the yellows (flowers stay untouched), full strength
# from yellow-green to green, fading out before teal/sky.
LO, FULL_LO, FULL_HI, HI = 37, 48, 100, 118   # ~52, 68, 140, 165 degrees


def hue_weight(h):
    """0 outside the green band, 255 in its middle, soft ramps either side."""
    if h <= LO or h >= HI:
        return 0
    if h < FULL_LO:
        return int(255 * (h - LO) / (FULL_LO - LO))
    if h > FULL_HI:
        return int(255 * (HI - h) / (HI - FULL_HI))
    return 255


def grade(path):
    im = Image.open(path)
    exif = im.info.get("exif")
    rgb = im.convert("RGB")
    h, s, v = rgb.convert("HSV").split()

    # Where to apply: green hues, scaled by saturation so greys/whites are left alone.
    mask = ImageChops.multiply(h.point([hue_weight(i) for i in range(256)]),
                               s.point([min(255, int(i * 255 / 70)) for i in range(256)]))
    mask = mask.filter(ImageFilter.GaussianBlur(2))

    graded = Image.merge("HSV", (
        h.point([(i + HUE_SHIFT) % 256 for i in range(256)]),
        s.point([int(i * SAT) for i in range(256)]),
        v.point([int(i * VAL) for i in range(256)]),
    )).convert("RGB")

    out = Image.composite(graded, rgb, mask)
    kw = {"quality": 82, "optimize": True}
    if exif:
        kw["exif"] = exif
    out.save(path, **kw)


def site_photos():
    return sorted(p for p in glob.glob(os.path.join(ROOT, "assets", "img", "*.jpg")))


def main(args):
    os.makedirs(ORIG, exist_ok=True)
    if args == ["--restore"]:
        for p in site_photos():
            o = os.path.join(ORIG, os.path.basename(p))
            if os.path.exists(o):
                shutil.copy2(o, p)
        print("restored originals")
        return
    paths = site_photos() if args == ["--all"] else [os.path.abspath(a) for a in args]
    for p in paths:
        o = os.path.join(ORIG, os.path.basename(p))
        if not os.path.exists(o):
            shutil.copy2(p, o)          # keep the untouched original once
        shutil.copy2(o, p)              # always grade from the original
        grade(p)
        print("graded", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main(sys.argv[1:])
