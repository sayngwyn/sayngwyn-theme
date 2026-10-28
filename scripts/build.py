"""Build the MO2 theme from src/theme.qss, palette.py and icons.py.

    py -3.12 scripts/build.py            # writes dist/<name>/stylesheets/...
    py -3.12 scripts/build.py --deploy   # also copies it into test-env/MO2

Output is laid out like MO2's own stylesheets folder, so the zip installs
by dropping `stylesheets` into MO2's folder.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from icons import build_icons  # noqa: E402
from palette import TOKENS  # noqa: E402

NAME = "sayngwyn"  # theme name: file names and MO2's style list
VERSION = "1.0.0"

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "theme.qss"
MARKS = ROOT / "src" / "marks"  # brand marks, from the brand's assets
DIST = ROOT / "dist" / NAME
TEST_MO2 = ROOT / "test-env" / "MO2"


def render_qss() -> str:
    tokens = {**TOKENS, "name": NAME, "version": VERSION, "dir": f"./{NAME}"}
    text = SRC.read_text(encoding="utf-8")

    def sub(m: re.Match[str]) -> str:
        key = m.group(1)
        if key not in tokens:
            raise KeyError(f"unknown token @{key}@ in {SRC.name}")
        return tokens[key]

    return re.sub(r"@([a-z_]+)@", sub, text)


def referenced_icons(qss: str) -> set[str]:
    return set(re.findall(rf'url\("\./{re.escape(NAME)}/([^"]+)"\)', qss))


def build(out: Path) -> Path:
    qss = render_qss()
    icons = build_icons()
    missing = referenced_icons(qss) - icons.keys() - {p.name for p in MARKS.iterdir()}
    if missing:
        raise SystemExit(f"stylesheet uses icons that aren't drawn: {sorted(missing)}")

    sheets = out / "stylesheets"
    if out.exists():
        shutil.rmtree(out)
    (sheets / NAME).mkdir(parents=True)
    # LF line endings and no BOM, byte for byte the same on every build
    (sheets / f"{NAME}.qss").write_bytes(qss.encode("utf-8"))
    for name, svg in sorted(icons.items()):
        (sheets / NAME / name).write_bytes(svg.encode("utf-8"))
    # sayngwyn's mark, copied as is (it isn't ours to redraw), with its notice.
    # Only what the stylesheet uses ships (the skull alone is the label's source).
    used = referenced_icons(qss) | {"NOTICE.txt"}
    for mark in sorted(MARKS.iterdir()):
        if mark.name in used:
            shutil.copy2(mark, sheets / NAME / mark.name)
    # the licence travels with the theme (LF line endings, so the zip stays byte-identical on every build)
    licence = (ROOT / "LICENSE").read_text(encoding="utf-8").replace("\r\n", "\n")
    (sheets / NAME / "LICENSE.txt").write_bytes(licence.encode("utf-8"))
    return sheets


def deploy_targets() -> list[Path]:
    """The test MO2, plus any MO2 folders listed in deploy-targets.txt
    (one per line; git-ignored, so personal paths stay out of the repo)."""
    targets = [TEST_MO2]
    extra = ROOT / "deploy-targets.txt"
    if extra.is_file():
        for line in extra.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                targets.append(Path(line))
    return targets


def deploy(sheets: Path, mo2: Path) -> None:
    """Copy the theme into one MO2. Touches only its own qss and folder."""
    target = mo2 / "stylesheets"
    if not (mo2 / "ModOrganizer.exe").is_file() or not target.is_dir():
        raise SystemExit(f"not an MO2 folder: {mo2}")
    shutil.copy2(sheets / f"{NAME}.qss", target / f"{NAME}.qss")
    if (target / NAME).exists():
        shutil.rmtree(target / NAME)
    shutil.copytree(sheets / NAME, target / NAME)


def package(sheets: Path) -> Path:
    """The release zip: the stylesheets folder, byte-identical for the same build."""
    import zipfile

    out = ROOT / "dist" / f"Sayngwyn Theme {VERSION}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(sheets.rglob("*")):
            if path.is_file():
                info = zipfile.ZipInfo(path.relative_to(sheets.parent).as_posix(), (2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, path.read_bytes())
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--deploy", action="store_true",
                        help="copy into test-env/MO2 and deploy-targets.txt")
    parser.add_argument("--zip", action="store_true", help="also make the release zip in dist/")
    args = parser.parse_args()
    sheets = build(DIST)
    print(f"built {sheets}")
    if args.zip:
        print(f"packaged {package(sheets)}")
    if args.deploy:
        for mo2 in deploy_targets():
            deploy(sheets, mo2)
            print(f"deployed to {mo2 / 'stylesheets'}")


if __name__ == "__main__":
    main()
