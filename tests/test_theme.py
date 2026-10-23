"""Checks on the built theme: contrast, icons and that Qt accepts the stylesheet."""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import build  # noqa: E402
from icons import build_icons  # noqa: E402
from palette import (  # noqa: E402
    ALPHA, PALETTE, SKILL_EXCLUDED, SKILL_ROWS, SURFACES, TEXT_ON_FILLS, TEXT_ON_SURFACES,
)

# The brand skill that owns these colours. Not part of the public repo:
# the comparison is skipped where the skill isn't installed.
SKILL = Path(os.environ.get(
    "SAYNGWYN_BRAND_SKILL",
    str(Path.home() / ".claude" / "skills" / "sayngwyn-mod-style" / "SKILL.md")))


def _skill_table() -> dict[str, str]:
    """{role cell: colour cell} from the skill's "App and window theme" table."""
    if not SKILL.is_file():
        pytest.skip(f"brand skill not found at {SKILL}")
    text = SKILL.read_text(encoding="utf-8")
    section = text.split("## App and window theme", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for line in section.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 2 and cells[0] not in ("Role", "---"):
            rows[cells[0]] = cells[1]
    return rows


def _row(rows: dict[str, str], start: str) -> str:
    hits = [colour for role, colour in rows.items() if role.startswith(start)]
    assert len(hits) == 1, f"skill has no single row starting {start!r}"
    return hits[0].lower()


@pytest.mark.parametrize("key", sorted(PALETTE))
def test_every_colour_comes_from_the_skill(key: str) -> None:
    assert key in SKILL_ROWS, f"{key} has no row in the skill; add it to the brand skill first"
    cell = _row(_skill_table(), SKILL_ROWS[key])
    value = PALETTE[key].lower()
    assert value in cell or (key == "white" and "white" in cell), (
        f"{key} = {value}, but the skill's {SKILL_ROWS[key]!r} row says: {cell}")


def test_no_colours_wait_for_the_skill() -> None:
    from palette import PENDING_SKILL

    if PENDING_SKILL:
        pytest.skip(f"on trial, not in the brand skill yet: {sorted(PENDING_SKILL)}")


def test_every_skill_colour_is_in_the_palette() -> None:
    import re

    rows = _skill_table()
    ours = {v.lower() for v in PALETTE.values()}
    missing = {h.lower() for cell in rows.values() for h in re.findall(r"#[0-9a-fA-F]{6}", cell)}
    missing -= ours | SKILL_EXCLUDED
    assert not missing, f"skill colours not in palette.py: {sorted(missing)}"


def test_silver_alphas_match_the_skill() -> None:
    cell = _row(_skill_table(), "Everyday buttons")
    for key, alpha in (("silver_line", 115), ("silver_line_hover", 235),
                       ("silver_line_off", 55), ("silver_fill_hover", 28),
                       ("silver_fill_press", 52)):
        assert f"{alpha}/255" in cell and ALPHA[key].endswith(f", {alpha})"), key
    # Scrollbars: "about 35%", "about 60%" in Controls in every window.
    assert round(0.35 * 255) == int(ALPHA["scroll"].split(",")[-1].strip(" )"))
    assert round(0.60 * 255) == int(ALPHA["scroll_hover"].split(",")[-1].strip(" )"))


def _luminance(hex_colour: str) -> float:
    rgb = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


@pytest.mark.parametrize("text", TEXT_ON_SURFACES)
@pytest.mark.parametrize("surface", SURFACES)
def test_text_reads_on_every_surface(text: str, surface: str) -> None:
    ratio = contrast(PALETTE[text], PALETTE[surface])
    assert ratio >= 4.5, f"{text} on {surface} is {ratio:.2f}:1"


@pytest.mark.parametrize(("text", "fill"), TEXT_ON_FILLS)
def test_text_reads_on_fills(text: str, fill: str) -> None:
    ratio = contrast(PALETTE[text], PALETTE[fill])
    assert ratio >= 4.5, f"{text} on {fill} is {ratio:.2f}:1"


def test_alarm_is_not_the_brand_red() -> None:
    # Different hue family, so warnings never read as decoration.
    assert PALETTE["alarm"] != PALETTE["accent"]
    assert contrast(PALETTE["alarm"], PALETTE["bg"]) >= 4.5


def test_theme_file_name_is_stable() -> None:
    # MO2 saves the chosen theme as "style=sayngwyn.qss"; renaming the file
    # would silently drop every user's choice when they update.
    assert build.NAME == "sayngwyn"


def test_every_token_resolves_and_every_icon_exists() -> None:
    qss = build.render_qss()
    assert "@" not in qss.replace("@import", "")
    marks = {p.name for p in build.MARKS.iterdir()}
    assert build.referenced_icons(qss) <= build_icons().keys() | marks


def test_package_ships_only_what_the_theme_uses() -> None:
    sheets = build.build(build.ROOT / "dist" / "test-build")
    shipped = {p.name for p in (sheets / build.NAME).iterdir()}
    used = build.referenced_icons(build.render_qss())
    assert shipped == used | {"NOTICE.txt"}, shipped ^ (used | {"NOTICE.txt"})


def test_mark_ships_with_its_notice() -> None:
    # The skull is sayngwyn's, outside the code's licence: never without the notice.
    names = {p.name for p in build.MARKS.iterdir()}
    assert names == {"sayngwyn-skull.svg", "run-label.svg", "NOTICE.txt"}
    notice = " ".join((build.MARKS / "NOTICE.txt").read_text(encoding="utf-8").split())
    assert "all rights reserved" in notice and "Forks must remove or replace it" in notice


def test_icons_are_valid_svg() -> None:
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtGui import QGuiApplication
    from PyQt6.QtSvg import QSvgRenderer

    _app = QGuiApplication.instance() or QGuiApplication([])
    for name, svg in build_icons().items():
        assert QSvgRenderer(QByteArray(svg.encode())).isValid(), name


def test_qt_parses_the_stylesheet() -> None:
    from PyQt6.QtCore import QtMsgType, qInstallMessageHandler
    from PyQt6.QtWidgets import QApplication, QPushButton

    warnings: list[str] = []

    def handler(kind: QtMsgType, _ctx: object, msg: str) -> None:
        if kind != QtMsgType.QtDebugMsg:
            warnings.append(msg)

    app = QApplication.instance() or QApplication([])
    old = qInstallMessageHandler(handler)
    try:
        assert isinstance(app, QApplication)
        app.setStyleSheet(build.render_qss())
        button = QPushButton("x")
        button.ensurePolished()
        app.processEvents()
    finally:
        qInstallMessageHandler(old)
        app.setStyleSheet("")
    assert not [w for w in warnings if "stylesheet" in w.lower()], warnings
