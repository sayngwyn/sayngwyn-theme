"""Draw the Run button's label: sayngwyn's skull plus "RUN" in Sayngwyn Serif.

    .venv\\Scripts\\python.exe scripts\\make_run_label.py

MO2 can't load a font from a theme, and a stylesheet can't change case, so
the lettering is turned into outlines here and saved with the skull as one
image, src/marks/run-label.svg. The theme then hides MO2's own "Run" text.
Re-run this only when the skull, the font or the colours change; the
result is committed beside the skull it's made from.

The skull is copied unchanged (sayngwyn's mark, never redrawn). The font is
Sayngwyn Serif under the SIL Open Font License (src/fonts/OFL.txt); text
drawn with it carries no restriction.
"""

import re
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from palette import PALETTE  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SKULL = ROOT / "src" / "marks" / "sayngwyn-skull.svg"
FONT = ROOT / "src" / "fonts" / "SayngwynSerif-Regular.ttf"
OUT = ROOT / "src" / "marks" / "run-label.svg"

HEIGHT = 64.0       # the label's height; the skull fills it
EM = 38.0           # the lettering's font size, in the same units
GAP = 12.0          # between skull and word
SHADOW = 0.06       # the brand's offset shadow, as a share of the font size
# Shadow colour on the Run button only (brand guide, 2026-10-22: the brand's #601d2c shadow vanishes on the dark glow, so
# Run's label uses a brighter palette red; offset geometry unchanged).
SHADOW_COLOUR = PALETTE["run_shadow"]
BRAND_SHADOW = "#601d2c"   # the shadow colour inside the logo file


def skull_group(height: float, shadow: str) -> tuple[str, float]:
    """The skull's own drawing, scaled to the given height, its shadow in `shadow`."""
    svg = SKULL.read_text(encoding="utf-8")
    assert svg.count(f'fill="{BRAND_SHADOW}"') == 1, "logo's shadow layer not found"
    svg = svg.replace(f'fill="{BRAND_SHADOW}"', f'fill="{shadow}"')
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    inner = svg[svg.index(">", svg.index("<svg")) + 1:svg.rindex("</svg>")]
    scale = height / vb[3]
    return (f'<g transform="scale({scale:.6f}) translate({-vb[0]} {-vb[1]})">{inner}</g>',
            vb[2] * scale)


def word_path(text: str, em: float, x: float, baseline: float) -> tuple[str, float]:
    """SVG path data for text set in the font, and its advance width."""
    font = TTFont(str(FONT))
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = em / font["head"].unitsPerEm
    pen = SVGPathPen(glyphs)
    cursor = 0.0
    for ch in text:
        name = cmap[ord(ch)]
        # font units are y-up; SVG is y-down
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x + cursor, baseline)))
        cursor += glyphs[name].width * scale
    return pen.getCommands(), cursor


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Draw the Run button's label.")
    parser.add_argument("--shadow", default=SHADOW_COLOUR, help="shadow colour (mock-ups)")
    parser.add_argument("--out", type=Path, default=OUT, help="where to write (mock-ups)")
    args = parser.parse_args()
    shadow_colour = args.shadow
    skull, skull_w = skull_group(HEIGHT, shadow_colour)
    font = TTFont(str(FONT))
    cap = font["OS/2"].sCapHeight / font["head"].unitsPerEm * EM
    baseline = (HEIGHT + cap) / 2          # caps centred on the skull
    x = skull_w + GAP
    d, width = word_path("RUN", EM, x, baseline)
    off = SHADOW * EM
    total = x + width + off + 1
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total:.1f}" height="{HEIGHT:.0f}" '
        f'viewBox="0 0 {total:.2f} {HEIGHT:.2f}">'
        f"{skull}"
        f'<path transform="translate({off:.2f} {off:.2f})" fill="{shadow_colour}" d="{d}"/>'
        f'<path fill="{PALETTE["text"]}" d="{d}"/>'
        "</svg>\n"
    )
    args.out.write_bytes(svg.encode("utf-8"))
    print(f"wrote {args.out} ({total:.0f} x {HEIGHT:.0f})")


if __name__ == "__main__":
    main()
