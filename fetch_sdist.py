"""Download a python-rtmidi source distribution from PyPI, verifying the digest PyPI reports.

Every wheel this repository publishes is built from the file this fetches, so the build jobs all
start from identical bytes rather than each resolving the release for themselves.
"""

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

PACKAGE = "python-rtmidi"
PYPI_URL = "https://pypi.org/pypi/{package}/{version}/json"
CHUNK_SIZE = 1 << 16


def find_sdist(package: str, version: str) -> dict:
    """Return PyPI's record of the source distribution for one release."""
    url = PYPI_URL.format(package=package, version=version)

    with urllib.request.urlopen(url) as response:
        release = json.load(response)

    for entry in release["urls"]:
        if entry["packagetype"] == "sdist":
            return entry

    raise RuntimeError(f"{package} {version} has no source distribution on PyPI")


def download(url: str, target: Path) -> str:
    """Download a file, returning its SHA-256 digest."""
    digest = hashlib.sha256()

    with urllib.request.urlopen(url) as response, target.open("wb") as output:
        while chunk := response.read(CHUNK_SIZE):
            digest.update(chunk)
            output.write(chunk)

    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="the release to fetch, such as 1.5.8")
    parser.add_argument("directory", type=Path, help="where to write the sdist")
    arguments = parser.parse_args()

    entry = find_sdist(PACKAGE, arguments.version)
    arguments.directory.mkdir(parents=True, exist_ok=True)
    target = arguments.directory / entry["filename"]

    print(f"Downloading {entry['filename']}")
    actual = download(entry["url"], target)
    expected = entry["digests"]["sha256"]

    if actual != expected:
        target.unlink(missing_ok=True)
        print(f"Digest mismatch: PyPI reports {expected}, the download is {actual}", file=sys.stderr)
        return 1

    print(f"sha256 {actual}, matching what PyPI reports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
