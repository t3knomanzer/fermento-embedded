import subprocess
from pathlib import Path
import sys

# -------- CONFIG --------
MPY_CROSS = "mpy-cross"  # or full path to mpy-cross(.exe)
ROOT = Path(__file__).resolve().parent.parent / "gui"
OPT_LEVEL = "-O2"

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".firmware",
}
# ------------------------


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def compile_file(py_file: Path):
    mpy_file = py_file.with_suffix(".mpy")

    print(f"Compiling {py_file} → {mpy_file.name}")

    subprocess.run(
        [MPY_CROSS, OPT_LEVEL, str(py_file)],
        check=True,
    )


def main():
    if not ROOT.exists():
        print(f"Error: directory not found: {ROOT}")
        sys.exit(1)

    for py_file in ROOT.rglob("*.py"):
        if should_skip(py_file):
            continue

        try:
            compile_file(py_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed compiling {py_file}")
            raise e

    print("✅ Compilation complete")


if __name__ == "__main__":
    main()
