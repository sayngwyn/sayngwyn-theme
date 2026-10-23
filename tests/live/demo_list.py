"""Give the test MO2 a believable demo mod list for screenshots.

    py -3.12 tests/live/demo_list.py

Separators, ordinary-sounding mod names (not real mods, so no one else's work is shown), versions and real
file conflicts, so MO2 draws its conflict flags and, for a selected mod, its overwrite highlights. Writes only
under test-env/MO2 (git-ignored): demo mod folders and the Default profile's modlist.txt (game and Creation
Club entries are kept).
"""

from pathlib import Path

MO2 = Path(__file__).resolve().parents[2] / "test-env" / "MO2"
MODS = MO2 / "mods"
PROFILE = MO2 / "profiles" / "Default" / "modlist.txt"

# Lowest priority first, as MO2 orders them on screen. (name, version, files, enabled)
LIST = [
    ("Fixes_separator", None, [], True),
    ("Engine Fixes Collection", "7.2", ["SKSE/plugins/enginefixes.dll"], True),
    ("Crash Logger", "1.14", ["SKSE/plugins/crashlogger.dll"], True),
    ("Quest Bug Fixes", "2.3", ["scripts/questfix.pex", "textures/ui/menu.dds"], True),
    ("Interface_separator", None, [], True),
    ("Cleaner Menus", "5.2", ["interface/menus.swf", "textures/ui/menu.dds"], True),
    ("Map Markers Plus", "1.6", ["interface/map.swf"], True),
    ("Readable Fonts", "3.0", ["interface/fonts.swf", "interface/menus.swf"], True),
    ("Visuals_separator", None, [], True),
    ("Landscape Textures", "4.1", ["textures/landscape/dirt.dds", "textures/landscape/grass.dds",
                                   "textures/landscape/rock.dds"], True),
    ("Better Water", "2.0", ["textures/water/water.dds", "meshes/water/water.nif"], True),
    ("Lighting Overhaul", "1.9", ["meshes/lights/torch.nif", "textures/landscape/rock.dds"], True),
    ("Snowy Rocks", "1.2", ["textures/landscape/rock.dds", "textures/landscape/snow.dds"], True),
    ("Old Texture Pack", "0.9", ["textures/landscape/grass.dds"], False),
    ("Gameplay_separator", None, [], True),
    ("Simple Survival", "3.4", ["scripts/survival.pex"], True),
    ("Faster Workbenches", "1.1", ["scripts/workbench.pex"], True),
    ("Follower Tweaks", "2.7", ["scripts/follower.pex", "scripts/questfix.pex"], True),
    ("Patches_separator", None, [], True),
    ("Lighting and Snow Patch", "1.0", ["textures/landscape/snow.dds", "meshes/lights/torch.nif"], True),
]


def main() -> None:
    for name, version, files, _ in LIST:
        folder = MODS / name
        folder.mkdir(parents=True, exist_ok=True)
        meta = "[General]\r\nmodid=0\r\ninstalled=true\r\n"
        if version:
            meta += f"version={version}\r\n"
        (folder / "meta.ini").write_bytes(meta.encode())
        for rel in files:
            path = folder / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"{name}:{rel}".encode())
    kept = [line for line in PROFILE.read_text(encoding="utf-8").splitlines()
            if line.startswith("*") or line.startswith("#")]
    header = [line for line in kept if line.startswith("#")]
    unmanaged = [line for line in kept if line.startswith("*")]
    # modlist.txt lists the highest priority first
    ours = [("+" if enabled else "-") + name for name, _, _, enabled in reversed(LIST)]
    PROFILE.write_text("\n".join(header + ours + unmanaged) + "\n", encoding="utf-8")
    print(f"{len(LIST)} demo entries in {PROFILE}")


if __name__ == "__main__":
    main()
