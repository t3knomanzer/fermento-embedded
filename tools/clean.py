import os
import subprocess
from pathlib import Path
import sys

# -------- CONFIG --------
ROOT = Path(__file__).resolve().parent.parent


def main():
    if not ROOT.exists():
        print(f"Error: directory not found: {ROOT}")
        sys.exit(1)

    for py_file in ROOT.rglob("*.mpy"):
        try:
            print(f"Deleting file {py_file}")
            os.remove(py_file)
        except Exception as e:
            print(f"❌ Failed deleting {py_file}")
            raise e

    print("✅ Cleaning complete")


if __name__ == "__main__":
    main()
