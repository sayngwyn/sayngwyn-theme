"""Screenshot the theme in the test MO2.

    py -3.12 tests/live/run_shots.py [out_dir]

Builds and deploys the theme, copies the test-only shots plugin into
test-env/MO2/plugins, runs MO2 (--multiple) until the plugin closes it,
then removes the plugin. Refuses while Skyrim is running.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MO2 = ROOT / "test-env" / "MO2"
PLUGIN = Path(__file__).resolve().parent / "shots_plugin.py"
TARGET = MO2 / "plugins" / "sayngwyn_theme_shots.py"


def game_running() -> bool:
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq SkyrimSE.exe", "/NH"],
                         capture_output=True, text=True).stdout
    return "SkyrimSE.exe" in out


def install_zip() -> None:
    """Replace the test MO2's copy of the theme with what the release zip holds, exactly as a user would."""
    import zipfile

    sys.path.insert(0, str(ROOT / "scripts"))
    import build

    zip_path = ROOT / "dist" / f"Sayngwyn Theme {build.VERSION}.zip"
    sheets = MO2 / "stylesheets"
    (sheets / f"{build.NAME}.qss").unlink(missing_ok=True)
    if (sheets / build.NAME).exists():
        shutil.rmtree(sheets / build.NAME)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(MO2)  # the zip's paths start with stylesheets/
    print(f"installed {zip_path.name} into the test MO2")


def main() -> int:
    """[out_dir] [--2x] [--from-zip]: --2x runs MO2 at QT_SCALE_FACTOR=2 (every image at 2x, as the brand asks);
    --from-zip installs the built release zip into the test MO2 (instead of building and copying) so the
    shots prove the zip itself works."""
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    double = "--2x" in sys.argv
    from_zip = "--from-zip" in sys.argv
    out = Path(args[0]) if args else ROOT / "test-env" / ("shots-2x" if double else "shots")
    if game_running():
        print("Skyrim is running; not starting MO2.")
        return 2
    if TARGET.exists():
        print(f"{TARGET} already exists; refusing to overwrite.")
        return 2
    if from_zip:
        install_zip()
    else:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py"), "--deploy"], check=True)
    if out.exists():
        shutil.rmtree(out)
    shutil.copy2(PLUGIN, TARGET)
    try:
        env = {**os.environ, "SAYNGWYN_SHOTS": str(out)}
        if double:
            env.update({"QT_SCALE_FACTOR": "2", "SAYNGWYN_SIZE": "1240x680"})
        exe = MO2 / "ModOrganizer.exe"
        # Started from a script on purpose: the shots plugin only takes pictures and closes MO2 itself.
        # MO2 started this way sits in the shell's Windows job, so programs it launches fail (shared rule,
        # ModLabs ff9ce45): never use this run to launch a game or tool.
        proc = subprocess.Popen([str(exe), "--multiple"], cwd=str(MO2), env=env)
        try:
            proc.wait(timeout=120)
        except subprocess.TimeoutExpired:
            # never kill MO2 (shared rule): leave it open for a graceful close
            print("MO2 didn't close in time; it's still open. Close its window by hand.")
            return 1
    finally:
        TARGET.unlink(missing_ok=True)
    shots = sorted(p.name for p in out.glob("*.png")) if out.exists() else []
    print(f"{len(shots)} shots in {out}: {', '.join(shots)}")
    return 0 if shots else 1


if __name__ == "__main__":
    raise SystemExit(main())
