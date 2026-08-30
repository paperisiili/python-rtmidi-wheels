"""Assert that a directory of built wheels is exactly what this repository means to publish.

The build cannot check this itself: cibuildwheel exits green as long as something built, and the
bundling steps — auditwheel, delvewheel, inject_licenses — each see one wheel at a time. This
runs once over the merged set and fails the workflow when the set is short, a wheel belongs to a
different release, or a wheel's contents are missing what the README promises: bundled libjack
with its license files on Linux, the MSVC runtime on Windows, nothing bundled on macOS.
"""

import argparse
import sys
import zipfile
from pathlib import Path


def platform_tag(name: str) -> str:
    """Return the platform part of a wheel filename."""
    return name.removesuffix(".whl").split("-")[-1]


def check(wheel: Path, version: str) -> list[str]:
    """Return every complaint about one wheel, empty when it is as it should be."""
    complaints = []

    named_version = wheel.name.split("-")[1]
    if named_version != version:
        complaints.append(f"is python-rtmidi {named_version}, expected {version}")

    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
    platform = platform_tag(wheel.name)

    if "manylinux" in platform:
        bundled = [n for n in names if "libjack" in Path(n).name]
        if len(bundled) != 1:
            complaints.append(f"bundles {len(bundled)} libjack libraries, expected exactly 1")
        if any("libasound" in Path(n).name for n in names):
            complaints.append("bundles libasound, which should stay a system library")
        for wanted in ("licenses/jack2/COPYING.LESSER", "licenses/jack2/NOTICE"):
            if not any(n.endswith(wanted) for n in names):
                complaints.append(f"is missing {wanted}")
    elif platform.startswith("win"):
        if not any(Path(n).name.startswith("msvcp140") for n in names):
            complaints.append("does not bundle msvcp140.dll")
    elif platform.startswith("macosx"):
        if any(n.endswith(".dylib") for n in names):
            complaints.append("bundles a dylib, which no macOS wheel here should need")

    return complaints


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="the directory of wheels to check")
    parser.add_argument("version", help="the python-rtmidi release every wheel must be")
    parser.add_argument("expected", type=int, help="how many wheels there must be")
    arguments = parser.parse_args()

    wheels = sorted(arguments.directory.glob("*.whl"))
    failed = False

    for wheel in wheels:
        complaints = check(wheel, arguments.version)
        for complaint in complaints:
            print(f"FAIL {wheel.name}: {complaint}")
            failed = True
        if not complaints:
            print(f"ok   {wheel.name}")

    if len(wheels) != arguments.expected:
        print(f"FAIL expected {arguments.expected} wheels, found {len(wheels)}")
        failed = True
    else:
        print(f"{len(wheels)} wheels, as expected")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
