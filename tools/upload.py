import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".venv", "firmware", "sandbox", "tools", "_lib", "lib", ".git"}

MPREMOTE_BASE = ["mpremote"]


def should_exclude(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def run_cmd(cmd, *, allow_fail=False):
    """Run a command and show mpremote output on failure."""
    r = subprocess.run(cmd, text=True, capture_output=True)
    if r.returncode != 0 and not allow_fail:
        print("\nCommand failed:", " ".join(cmd))
        print("stdout:\n", r.stdout)
        print("stderr:\n", r.stderr)
        raise SystemExit(r.returncode)
    return r


def ensure_remote_dirs(rel_path: Path):
    """
    Create remote directories one level at a time:
      rel_path = gui/core/colors.py -> mkdir :/gui then mkdir :/gui/core
    """
    parts = rel_path.parent.parts
    if not parts:
        return

    accum = ""
    for p in parts:
        accum = f"{accum}/{p}" if accum else p
        run_cmd(MPREMOTE_BASE + ["fs", "mkdir", f":/{accum}"], allow_fail=True)


for py_file in sorted(ROOT.rglob("*.*")):
    if should_exclude(py_file):
        continue

    rel_path = py_file.relative_to(ROOT)
    remote_path = f":/{rel_path.as_posix()}"

    ensure_remote_dirs(rel_path)

    print(f"Uploading: {rel_path.as_posix()} to {remote_path}")
    run_cmd(MPREMOTE_BASE + ["fs", "cp", str(py_file), remote_path])
