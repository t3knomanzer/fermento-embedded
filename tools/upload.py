import subprocess
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    ".venv",
    ".git",
    "firmware",
    "sandbox",
    "tools",
    "_lib",
    "lib",
    "_drivers",
    "drivers",
}

INCLUDE_EXTENSIONS = {".mpy", ".css", ".xbm", ".dat"}

# (local relative path, remote path)
FORCE_FILES = [("main.py", ":/main.py"), ("boot.py", ":/boot.py")]

MPREMOTE = ["mpremote"]


def run_cmd(cmd: list[str], *, allow_fail: bool = False) -> subprocess.CompletedProcess:
    """Run a command; print output on failure."""
    r = subprocess.run(cmd, text=True, capture_output=True)
    if r.returncode != 0 and not allow_fail:
        print("\nCommand failed:", " ".join(cmd))
        if r.stdout:
            print("stdout:\n", r.stdout)
        if r.stderr:
            print("stderr:\n", r.stderr)
        raise SystemExit(r.returncode)
    return r


def is_excluded(path: Path) -> bool:
    """Exclude anything under any directory in EXCLUDE_DIRS."""
    return any(part in EXCLUDE_DIRS for part in path.parts)


def ensure_remote_dirs(rel_path: Path) -> None:
    """Create remote directory chain for rel_path (file path)."""
    parts = rel_path.parent.parts
    if not parts:
        return

    accum = []
    for p in parts:
        accum.append(p)
        run_cmd(MPREMOTE + ["fs", "mkdir", ":/" + "/".join(accum)], allow_fail=True)


def iter_files(root: Path, exts: set[str]) -> Iterable[Path]:
    """Yield files under root matching extensions, excluding directories."""
    for ext in sorted(exts):
        for p in root.rglob(f"*{ext}"):
            if p.is_file() and not is_excluded(p):
                yield p


def upload_file(local_path: Path, remote_path: str) -> None:
    rel = local_path.relative_to(ROOT).as_posix()
    print(f"Uploading: {rel} -> {remote_path}")
    run_cmd(MPREMOTE + ["fs", "cp", str(local_path), remote_path])


def main() -> None:
    # Upload assets / compiled modules
    for file in sorted(set(iter_files(ROOT, INCLUDE_EXTENSIONS))):
        rel_path = file.relative_to(ROOT)
        ensure_remote_dirs(rel_path)
        upload_file(file, ":/" + rel_path.as_posix())

    # Always upload boot.py / main.py to root (needed for auto-run)
    for local_rel, remote in FORCE_FILES:
        local_path = ROOT / local_rel
        upload_file(local_path, remote)


if __name__ == "__main__":
    main()
