"""Download a python-rtmidi source distribution from PyPI, verifying its digest.

Every wheel this repository publishes is built from the file this fetches, so the build jobs all
start from identical bytes rather than each resolving the release for themselves.

For releases named in PINNED the digest to match is written down here, in the repository, so a
build reproduces known bytes even if PyPI's metadata were tampered with. Any other version falls
back to the digest PyPI reports — which still catches transit corruption, and lets a new release
be tried before its pin lands — and the fallback is called out loudly in the output.
"""

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PACKAGE = "python-rtmidi"
PYPI_URL = "https://pypi.org/pypi/{package}/{version}/json"
CHUNK_SIZE = 1 << 16
TIMEOUT_SECONDS = 30
ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5

# Known sdist digests, keyed by release. Add a line here when moving DEFAULT_RTMIDI_VERSION in
# the workflow to a new upstream release.
PINNED = {
    "1.5.8": "7f9ade68b068ae09000ecb562ae9521da3a234361ad5449e83fc734544d004fa",
}


def fetch(url: str, handle):
    """Open a URL and pass the response to handle, retrying transient failures."""
    for attempt in range(1, ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
                return handle(response)
        except urllib.error.URLError as error:
            # A 404 is an answer, not a fault worth retrying.
            if isinstance(error, urllib.error.HTTPError) and error.code == 404:
                raise
            if attempt == ATTEMPTS:
                raise
            print(f"Attempt {attempt} failed ({error}); retrying", file=sys.stderr)
            time.sleep(RETRY_DELAY_SECONDS)


def find_sdist(package: str, version: str) -> dict:
    """Return PyPI's record of the source distribution for one release."""
    url = PYPI_URL.format(package=package, version=version)

    try:
        release = fetch(url, json.load)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            raise RuntimeError(f"{package} {version} does not exist on PyPI") from error
        raise

    for entry in release["urls"]:
        if entry["packagetype"] == "sdist":
            return entry

    raise RuntimeError(f"{package} {version} has no source distribution on PyPI")


def download(url: str, target: Path) -> str:
    """Download a file, returning its SHA-256 digest."""

    def save(response) -> str:
        digest = hashlib.sha256()
        with target.open("wb") as output:
            while chunk := response.read(CHUNK_SIZE):
                digest.update(chunk)
                output.write(chunk)
        return digest.hexdigest()

    return fetch(url, save)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="the release to fetch, such as 1.5.8")
    parser.add_argument("directory", type=Path, help="where to write the sdist")
    arguments = parser.parse_args()

    try:
        entry = find_sdist(PACKAGE, arguments.version)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1

    # The filename comes from PyPI's metadata; it names the file inside the output directory and
    # nothing else. PyPI has no reason to send a path, so one is refused rather than resolved.
    filename = entry["filename"]
    if filename != Path(filename).name:
        print(f"Refusing a filename with a path in it: {filename!r}", file=sys.stderr)
        return 1

    if arguments.version in PINNED:
        expected = PINNED[arguments.version]
        source = "the pin in this repository"
    else:
        expected = entry["digests"]["sha256"]
        source = "PyPI's own metadata — NOT pinned in this repository yet"
    print(f"Expecting sha256 {expected}\n  (from {source})")

    arguments.directory.mkdir(parents=True, exist_ok=True)
    target = arguments.directory / filename

    print(f"Downloading {filename}")
    actual = download(entry["url"], target)

    if actual != expected:
        target.unlink(missing_ok=True)
        print(f"Digest mismatch: expected {expected}, the download is {actual}", file=sys.stderr)
        return 1

    print(f"sha256 {actual}, as expected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
