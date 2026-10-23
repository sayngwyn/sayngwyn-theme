"""The theme's colours, in one place.

This is the reference sayngwyn window theme for all of sayngwyn's mods, so it
holds exactly the sayngwyn-mod-style skill's "App and window theme" table
and its "Controls in every window" rules: no more, no less.
tests/test_theme.py checks it against the skill. A value the skill lacks
is added to the skill first. Change a colour here and
rebuild; nothing else holds colour values. Templates refer to these as
@name@.
"""

PALETTE: dict[str, str] = {
    # surfaces
    "bg": "#0f0d0e",          # window background (the shirt)
    "panel": "#211a1a",       # lists, inputs, cards (black star)
    "alt": "#262020",         # alternate rows
    "raised": "#2b2324",      # headers, menus, tooltips, checkbox boxes
    "border": "#403839",
    "stripe": "#767375",      # neutral silver-grey lines
    # text
    "text": "#dededb",        # bone (white star)
    "muted": "#aca3a2",
    "silver": "#c2c2c4",
    "redtext": "#d36e6e",     # red as text, lifted for contrast
    "redtext_on_tint": "#dd8f8f",  # same hue, lifted again for tinted rows
    # accent: selected things and the one main action only
    "accent": "#812727",      # red star
    "accent_hover": "#963030",
    "sel": "#601d2c",         # selected rows (deep-red star)
    "sel_hover": "#3f1b24",   # hovered rows and menu items
    "white": "#ffffff",
    # alarms: never the brand red
    "alarm": "#ff5c7c",
    "alarm_text": "#ff7993",  # the alarm colour as text
    # the main action (Run) only
    "glow": "#45191f",        # Run's radial glow centre
    "glow_hover": "#52202a",
    "run_pressed": "#1a1415",
    "run_shadow": "#aa3f3d",  # Run label's shadows: the logo's mid red
}

# Silver outlines and fills, as alpha over whatever sits behind.
ALPHA: dict[str, str] = {
    "silver_line": "rgba(194, 194, 196, 115)",
    "silver_line_hover": "rgba(194, 194, 196, 235)",
    "silver_line_off": "rgba(194, 194, 196, 55)",
    "silver_fill_hover": "rgba(194, 194, 196, 28)",
    "silver_fill_press": "rgba(194, 194, 196, 52)",
    "scroll": "rgba(194, 194, 196, 89)",          # about 35%
    "scroll_hover": "rgba(194, 194, 196, 153)",   # about 60%
}

# Colours on trial that the skill doesn't hold yet. Each waits for a decision
# and then for the skill to hold it (when it moves into
# PALETTE); tests/test_theme.py flags this list while it isn't empty.
PENDING_SKILL: dict[str, str] = {}

TOKENS: dict[str, str] = {**PALETTE, **ALPHA, **PENDING_SKILL}

# Text/surface pairs that must reach 4.5:1 (checked by tests/test_theme.py).
SURFACES = ["bg", "panel", "alt", "raised"]
TEXT_ON_SURFACES = ["text", "muted", "silver", "redtext"]
TEXT_ON_FILLS = [
    ("text", "accent"), ("white", "accent"), ("text", "accent_hover"),
    ("text", "sel"), ("text", "sel_hover"), ("muted", "sel_hover"),
    ("redtext_on_tint", "sel_hover"), ("alarm_text", "bg"), ("alarm_text", "panel"),
]

# Where each colour comes from in the skill's "App and window theme" table
# (the start of the row's Role cell). Checked by tests/test_theme.py.
SKILL_ROWS: dict[str, str] = {
    "bg": "Window background",
    "panel": "Panels and cards",
    "alt": "Alternate rows",
    "raised": "Raised surfaces",
    "border": "Borders",
    "stripe": "Neutral side stripes",
    "text": "Main text",
    "muted": "Muted text",
    "silver": "Everyday buttons",
    "redtext": "Accent text",
    "redtext_on_tint": "Accent text",
    "accent": "Accent:",
    "accent_hover": "Accent:",
    "white": "Accent:",        # "with white or bone text only"
    "sel": "Selected row",
    "sel_hover": "Selected row",
    "alarm": "Errors and alarms",
    "alarm_text": "Errors and alarms",
    "glow": "Main action",
    "glow_hover": "Main action",
    "run_pressed": "Main action",
    "run_shadow": "Main action",
}

# Hex values in the table that name what *not* to use, so the palette
# leaves them out on purpose.
SKILL_EXCLUDED = {"#8a7f80"}  # fine-print grey, "too dark as text"
