"""Write the Pages index that pip reads when this repository is used as a --find-links source.

The wheels themselves live as GitHub release assets; this page is only links to them, freshly
regenerable at any time from the list of releases. pip needs nothing but the anchors — each
carries its wheel's SHA-256 in the fragment, which pip verifies on download and matches against
hash-pinned requirements — and the surrounding prose is for whoever opens the page in a browser.

Wheels are grouped by release, newest first. Every wheel's filename carries its release number
as the wheel build tag, so wheels for the same python-rtmidi version from different releases
coexist here under distinct names: installers prefer the highest build number on their own,
which makes the newest release the default while nothing older ever changes or disappears.

A .nojekyll file is written alongside the page, without which GitHub Pages filters parts of what
gets uploaded.
"""

import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

TITLE = "python-rtmidi wheels (unofficial)"

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
</head>
<body>
<h1>{title}</h1>
<p>Unofficial builds of <a href="https://pypi.org/project/python-rtmidi/">python-rtmidi</a> for
CPython versions upstream does not publish wheels for. Built and published by
<a href="{repo}">{repo_name}</a>, which holds the build configuration and describes what goes
into each wheel.</p>
<p>Install with:</p>
<pre>pip install --only-binary python-rtmidi --find-links {url} python-rtmidi</pre>
<p>pip picks the wheel matching the interpreter it runs under; --only-binary makes a missing
wheel an error instead of a silent fall back to compiling the source distribution from PyPI,
which needs the compiler and headers these wheels exist to spare. Wheels differing only in the
build number after the version are rebuilds of the same release, newest preferred
automatically.</p>
<h2>Releases</h2>
{releases}
<h2>Verifying</h2>
<p>Each link names its wheel's SHA-256 in the fragment, which pip checks on download and matches
when an install pins hashes. Every release also carries a SHA256SUMS file, and each wheel a
sigstore attestation:
<code>gh attestation verify &lt;wheel&gt; --repo {repo_name}</code>.</p>
<h2>Bundled libraries</h2>
<p>The Linux wheels bundle libjack, the <a href="https://github.com/jackaudio/jack2">jack2</a>
client library, under the GNU Lesser General Public License v2.1 or later; the license text and
a provenance notice travel inside each wheel, and the exact source tree is attached to its
release. The Windows wheels bundle msvcp140.dll, Microsoft's C++ runtime, so they work without
the Visual C++ redistributable installed. python-rtmidi itself is MIT, and its license travels
inside every wheel.</p>
<p><small>Generated from commit {commit} by <a href="{run_url}">this run</a>, {date}.</small></p>
</body>
</html>
"""

RELEASE = """<h3>{tag}: python-rtmidi {versions}</h3>
<p>Published {date} — <a href="{release_url}">release page</a>.</p>
{notes}
<ul>
{links}
</ul>
"""

LINK = '<li><a href="{href}#sha256={digest}">{name}</a></li>'


def repository_name(url: str) -> str:
    """Return the owner and name a repository URL ends in, for use as link text."""
    parts = url.rstrip("/").split("/")

    if len(parts) < 2:
        raise RuntimeError(f"not a repository URL: {url}")

    return "/".join(parts[-2:])


def read_digests(sums_file: Path) -> dict[str, str]:
    """Map filenames to digests from one release's SHA256SUMS."""
    digests = {}
    for line in sums_file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            digests[name.strip()] = digest
    return digests


def paragraphs(text: str) -> str:
    """Render plain text as escaped HTML paragraphs."""
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text or "") if block.strip()]
    return "\n".join(f"<p>{html.escape(block)}</p>" for block in blocks)


def release_section(release: dict, digests: dict[str, str]) -> str:
    """Render one release: its notes and one verified link per wheel."""
    wheels = [asset for asset in release["assets"] if asset["name"].endswith(".whl")]
    if not wheels:
        raise RuntimeError(f"release {release['tag_name']} has no wheels")

    links = []
    versions = set()
    for asset in sorted(wheels, key=lambda asset: asset["name"]):
        name = asset["name"]
        if name not in digests:
            raise RuntimeError(f"{name} in {release['tag_name']} is missing from SHA256SUMS")
        versions.add(name.split("-")[1])
        links.append(
            LINK.format(
                href=html.escape(asset["browser_download_url"]),
                digest=digests[name],
                name=html.escape(name),
            )
        )

    return RELEASE.format(
        tag=html.escape(release["tag_name"]),
        versions=html.escape(", ".join(sorted(versions))),
        date=html.escape(release["published_at"].split("T")[0]),
        release_url=html.escape(release["html_url"]),
        notes=paragraphs(release.get("body") or ""),
        links="\n".join(links),
    )


def indexable(releases: list[dict]) -> list[dict]:
    """The releases the page covers: published vN releases, newest number first."""
    chosen = []
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue
        if not re.fullmatch(r"v[0-9]+", release["tag_name"]):
            print(f"Skipping unrecognized release tag {release['tag_name']}", file=sys.stderr)
            continue
        chosen.append(release)

    if not chosen:
        raise RuntimeError("no releases to index")

    return sorted(chosen, key=lambda release: int(release["tag_name"][1:]), reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("releases", type=Path, help="JSON list of this repository's releases")
    parser.add_argument("sums", type=Path, help="directory of SHA256SUMS files, one per tag")
    parser.add_argument("directory", type=Path, help="where to write the site")
    parser.add_argument("url", help="the published address of the page")
    parser.add_argument("repo", help="the repository the wheels are built from")
    parser.add_argument("--commit", default="unknown", help="the commit generating the page")
    parser.add_argument("--run-url", default="", help="the workflow run generating the page")
    arguments = parser.parse_args()

    releases = indexable(json.loads(arguments.releases.read_text(encoding="utf-8")))

    sections = []
    for release in releases:
        digests = read_digests(arguments.sums / release["tag_name"])
        sections.append(release_section(release, digests))

    page = PAGE.format(
        title=html.escape(TITLE),
        url=html.escape(arguments.url),
        repo=html.escape(arguments.repo),
        repo_name=html.escape(repository_name(arguments.repo)),
        releases="\n".join(sections),
        commit=html.escape(arguments.commit[:12]),
        run_url=html.escape(arguments.run_url),
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )

    arguments.directory.mkdir(parents=True, exist_ok=True)
    (arguments.directory / "index.html").write_text(page, encoding="utf-8")
    (arguments.directory / ".nojekyll").touch()

    wheels = sum(len([a for a in r["assets"] if a["name"].endswith(".whl")]) for r in releases)
    print(f"Indexed {len(releases)} release(s), {wheels} wheel(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
