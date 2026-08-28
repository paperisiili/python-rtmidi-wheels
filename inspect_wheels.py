"""List what each wheel in a directory contains, largest member first.

A diagnostic rather than part of the build: it answers what a wheel actually ended up carrying,
which the build log does not show.
"""

import argparse
import zipfile
from pathlib import Path


def report(wheel: Path) -> None:
    """Print one wheel's members and their sizes."""
    with zipfile.ZipFile(wheel) as archive:
        members = sorted(archive.infolist(), key=lambda i: i.file_size, reverse=True)
        total = sum(info.file_size for info in members)

        print(f"\n{wheel.name}")
        print(f"  {total / 1024:.1f} kB uncompressed, {wheel.stat().st_size / 1024:.1f} kB on disk")

        for info in members:
            print(f"  {info.file_size / 1024:10.1f} kB  {info.filename}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="the directory of wheels to inspect")
    arguments = parser.parse_args()

    wheels = sorted(arguments.directory.glob("*.whl"))

    if not wheels:
        raise RuntimeError(f"no wheels found in {arguments.directory}")

    for wheel in wheels:
        report(wheel)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
