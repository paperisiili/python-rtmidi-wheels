"""Add the bundled libjack's license text and provenance notice to each Linux wheel.

auditwheel copies the shared library into the wheel but adds no license file, and the LGPL asks
for its text and notices to accompany the library — inside the artifact, since a wheel circulates
detached from any page describing it. This rewrites each manylinux wheel with licenses/jack2/
under its dist-info directory, using `wheel unpack` and `wheel pack` so RECORD stays correct.

Runs on the build host after cibuildwheel finishes; wheels for other platforms carry no libjack
and are left alone.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def inject(wheel: Path, license_dir: Path) -> None:
    """Rewrite one wheel with the license directory's files under dist-info/licenses/jack2/."""
    with tempfile.TemporaryDirectory() as scratch:
        unpack_dir = Path(scratch, "unpacked")
        pack_dir = Path(scratch, "packed")
        pack_dir.mkdir()

        subprocess.run(
            [sys.executable, "-m", "wheel", "unpack", "--dest", str(unpack_dir), str(wheel)],
            check=True,
        )
        [tree] = unpack_dir.iterdir()
        [dist_info] = tree.glob("*.dist-info")

        target = dist_info / "licenses" / "jack2"
        target.mkdir(parents=True)
        for source in sorted(license_dir.iterdir()):
            shutil.copy(source, target / source.name)

        subprocess.run(
            [sys.executable, "-m", "wheel", "pack", "--dest-dir", str(pack_dir), str(tree)],
            check=True,
        )
        [packed] = pack_dir.iterdir()
        if packed.name != wheel.name:
            raise RuntimeError(f"repacking {wheel.name} produced {packed.name}")
        shutil.move(packed, wheel)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="the directory of wheels to rewrite")
    parser.add_argument("licenses", type=Path, help="the directory of files to add")
    arguments = parser.parse_args()

    wheels = [path for path in sorted(arguments.directory.glob("*.whl")) if "manylinux" in path.name]
    if not wheels:
        print(f"No manylinux wheels in {arguments.directory}", file=sys.stderr)
        return 1

    for wheel in wheels:
        inject(wheel, arguments.licenses)
        print(f"Added {arguments.licenses} to {wheel.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
