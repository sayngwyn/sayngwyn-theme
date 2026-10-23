"""The theme's icons, drawn here as simple line SVGs.

Every icon is original: a 24 px grid (16 px for check boxes and radios),
1.5 px rounded strokes, no fill. Colours come from palette.py by role:
toolbar icons are bone, small icons silver, warnings use the alarm colour.
"""

import math

from palette import PALETTE

LINE = 'fill="none" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"'


def _svg(body: str, colour: str, size: int = 24, width: float = 1.5) -> str:
    style = LINE.format(w=width)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">'
        f'<g stroke="{colour}" {style}>{body}</g></svg>\n'
    )


def _gear(cx: float = 12, cy: float = 12, teeth: int = 8, r_out: float = 9.5,
          r_in: float = 7.3) -> str:
    """A cog outline: flat-topped teeth around a ring."""
    points = []
    step = 2 * math.pi / teeth
    for i in range(teeth):
        a = i * step - math.pi / 2
        for da, r in ((-0.30, r_in), (-0.17, r_out), (0.17, r_out), (0.30, r_in)):
            angle = a + da * step / 0.5 * 0.5
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    d = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in points) + "Z"
    return f'<path d="{d}"/><circle cx="{cx}" cy="{cy}" r="3"/>'


def _wrench() -> str:
    # Ring of radius 5 at (16, 8) with a notch facing up-right, and a handle
    # running down-left.
    def at(deg: float) -> str:
        r = math.radians(deg)
        return f"{16 + 5 * math.cos(r):.2f} {8 - 5 * math.sin(r):.2f}"
    head = (f'<path d="M{at(18)} L18.3 7.2 L16.8 5.7 L{at(72)} '
            f'A5 5 0 1 0 {at(18)}"/>')
    handle = '<path d="M12.7 11.3 4.9 19.1a1.5 1.5 0 0 0 2.1 2.1l7.8-7.8"/>'
    return head + handle


# name: (body, colour role, grid size, stroke width)
_ICONS: dict[str, tuple[str, str, int, float]] = {
    # toolbar
    "instances": ('<path d="M4 8h15"/><path d="M15.5 4.5 19 8l-3.5 3.5"/>'
                  '<path d="M20 16H5"/><path d="M8.5 12.5 5 16l3.5 3.5"/>',
                  "text", 24, 1.5),
    "install": ('<path d="M12 3v11"/><path d="M7.5 9.5 12 14l4.5-4.5"/>'
                '<path d="M4 14v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"/>',
                "text", 24, 1.5),
    "globe": ('<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>'
              '<path d="M12 3c2.4 2.6 3.7 5.6 3.7 9s-1.3 6.4-3.7 9'
              'c-2.4-2.6-3.7-5.6-3.7-9S9.6 5.6 12 3z"/>',
              "text", 24, 1.5),
    "profiles": ('<circle cx="12" cy="8" r="4"/>'
                 '<path d="M4.5 20c0-3.9 3.4-6.3 7.5-6.3s7.5 2.4 7.5 6.3"/>',
                 "text", 24, 1.5),
    "refresh": ('<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3"/><path d="M19.5 4.5v4h-4"/>',
                "text", 24, 1.5),
    "executables": ('<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 8h18"/>'
                    '<path d="M10 11.2v5.6l4.6-2.8z"/>',
                    "text", 24, 1.5),
    "tools": (_wrench(), "text", 24, 1.5),
    "settings": (_gear(), "text", 24, 1.5),
    "heart": ('<path d="M12 19.5s-7.5-4.4-7.5-10A4.2 4.2 0 0 1 12 7.1a4.2 4.2 0 0 1 7.5 2.4'
              'c0 5.6-7.5 10-7.5 10z"/>',
              "text", 24, 1.5),
    "warning": ('<path d="M12 3.8 21 19.5H3z"/><path d="M12 10v4.3"/>'
                '<circle cx="12" cy="17" r=".4"/>',
                "alarm", 24, 1.5),
    "update": ('<circle cx="12" cy="12" r="9"/><path d="M12 16.5v-9"/>'
               '<path d="M8 11.5l4-4 4 4"/>',
               "text", 24, 1.5),
    "help": ('<circle cx="12" cy="12" r="9"/>'
             '<path d="M9.6 9.6a2.4 2.4 0 1 1 3.4 2.2c-.6.3-1 .9-1 1.6v.5"/>'
             '<circle cx="12" cy="16.9" r=".4"/>',
             "text", 24, 1.5),
    # buttons
    "shortcut": ('<path d="M14 4h6v6"/><path d="M20 4l-8.5 8.5"/>'
                 '<path d="M18 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4"/>',
                 "text", 24, 1.5),
    "dots": ('<circle cx="6" cy="12" r="1"/><circle cx="12" cy="12" r="1"/>'
             '<circle cx="18" cy="12" r="1"/>',
             "silver", 24, 2.0),
    "folder": ('<path d="M3 7a2 2 0 0 1 2-2h4l2 2.5h8a2 2 0 0 1 2 2V17a2 2 0 0 1-2 2H5'
               'a2 2 0 0 1-2-2z"/>',
               "silver", 24, 1.5),
    "restore": ('<path d="M4.5 12a7.5 7.5 0 1 0 2.2-5.3"/><path d="M4.5 4.5v4h4"/>',
                "silver", 24, 1.5),
    "save": ('<path d="M5 4h11l3 3v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1z"/>'
             '<path d="M8.5 4v4.5h6V4"/><rect x="8" y="13" width="8" height="7"/>',
             "silver", 24, 1.5),
    "broom": ('<path d="M20 4l-7.5 7.5"/>'
              '<path d="M10.2 9.8l4 4-1.6 5.7a1 1 0 0 1-1.6.5L4 13a1 1 0 0 1 .5-1.6z"/>'
              '<path d="M7.6 15.6l2.2-2.2M10.4 18.2l1.8-1.8"/>',
              "silver", 24, 1.5),
    "sort": ('<path d="M4 7h16M4 12h11M4 17h6"/>', "text", 24, 1.5),
    "plus": ('<path d="M12 5v14M5 12h14"/>', "silver", 24, 1.8),
    "minus": ('<path d="M5 12h14"/>', "silver", 24, 1.8),
    "cross": ('<path d="M7 7l10 10M17 7 7 17"/>', "silver", 24, 1.8),
    "restore-window": ('<rect x="4" y="8" width="12" height="12" rx="1.5"/>'
                       '<path d="M8 8V5.5A1.5 1.5 0 0 1 9.5 4h9A1.5 1.5 0 0 1 20 5.5v9'
                       'a1.5 1.5 0 0 1-1.5 1.5H16"/>',
                       "silver", 24, 1.5),
    # arrows
    "chevron-down": ('<path d="M6 9.5l6 6 6-6"/>', "silver", 24, 2.2),
    "chevron-up": ('<path d="M6 14.5l6-6 6 6"/>', "silver", 24, 2.2),
    "chevron-right": ('<path d="M9.5 6l6 6-6 6"/>', "silver", 24, 2.2),
}


def _box(stroke_opacity: float, inner: str = "", fill: str = "raised") -> str:
    p = PALETTE
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">'
        f'<rect x="1.5" y="1.5" width="13" height="13" rx="2.5" fill="{p[fill]}" '
        f'stroke="{p["silver"]}" stroke-opacity="{stroke_opacity}" stroke-width="1"/>'
        f"{inner}</svg>\n"
    )


def _circle(stroke_opacity: float, inner: str = "", fill: str = "raised") -> str:
    p = PALETTE
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">'
        f'<circle cx="8" cy="8" r="6.5" fill="{p[fill]}" '
        f'stroke="{p["silver"]}" stroke-opacity="{stroke_opacity}" stroke-width="1"/>'
        f"{inner}</svg>\n"
    )


def _tick(colour: str) -> str:
    return (f'<path d="M4.6 8.2 7 10.6l4.6-5" fill="none" stroke="{colour}" '
            'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')


def _dot(colour: str) -> str:
    return f'<circle cx="8" cy="8" r="3" fill="{colour}"/>'


def build_icons() -> dict[str, str]:
    """Return {file name: SVG text} for every icon the theme uses."""
    p = PALETTE
    out = {f"{name}.svg": _svg(body, p[role], size, width)
           for name, (body, role, size, width) in _ICONS.items()}
    bar = f'<path d="M5 8h6" stroke="{p["text"]}" stroke-width="1.8" stroke-linecap="round"/>'
    out.update({
        "check-off.svg": _box(0.45),
        "check-off-hover.svg": _box(0.92),
        "check-on.svg": _box(0.45, _tick(p["text"])),
        "check-on-hover.svg": _box(0.92, _tick(p["text"])),
        "check-partial.svg": _box(0.45, bar),
        "check-disabled.svg": _box(0.22, fill="panel"),
        "check-on-disabled.svg": _box(0.22, _tick(p["muted"]), fill="panel"),
        "radio-off.svg": _circle(0.45),
        "radio-off-hover.svg": _circle(0.92),
        "radio-on.svg": _circle(0.45, _dot(p["text"])),
        "radio-disabled.svg": _circle(0.22, fill="panel"),
    })
    return out
