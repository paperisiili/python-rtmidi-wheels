"""Write the index page that pip reads when this repository is used as a --find-links source.

pip only needs anchors pointing at the wheels, so the surrounding prose is for whoever opens the
page in a browser. A .nojekyll file is written alongside it, without which GitHub Pages filters
parts of what gets uploaded.
"""

import argparse
import html
from pathlib import Path

TITLE = "python-rtmidi wheels"

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
</head>
<body>
<h1>{title}</h1>
<p>Unofficial builds of python-rtmidi {version}, for CPython versions upstream does not publish
wheels for. The Linux wheels carry both ALSA and JACK, the macOS wheels CoreMIDI, and the
Windows wheels the multimedia API.</p>
<p>Install with:</p>
<pre>pip install --find-links {url} python-rtmidi=={version}</pre>
<p>pip picks the wheel matching the interpreter it runs under, and falls back to building
upstream's source distribution from PyPI when none of these matches.</p>
<h2>Wheels</h2>
<ul>
{links}
</ul>
<h2>Bundled libraries</h2>
<p>The Linux wheels include a copy of libjack from
<a href="https://github.com/jackaudio/jack2">jack2</a> v1.9.22, which is licensed under the GNU
Lesser General Public License version 2.1 or later. Its source is available at that address.</p>
<p>The Windows wheels include msvcp140.dll, Microsoft's C++ runtime, so that they work without the
Visual C++ redistributable installed.</p>
<p>python-rtmidi itself is MIT, and its license travels inside every wheel.</p>
</body>
</html>
"""

LINK = '<li><a href="{name}">{name}</a></li>'


def build_page(directory: Path, version: str, url: str) -> str:
    """Render the index for every wheel in a directory."""
    wheels = sorted(path.name for path in directory.glob("*.whl"))

    if not wheels:
        raise RuntimeError(f"no wheels found in {directory}")

    links = "\n".join(LINK.format(name=html.escape(name)) for name in wheels)

    return PAGE.format(
        title=html.escape(TITLE),
        version=html.escape(version),
        url=html.escape(url),
        links=links,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="the directory of wheels to index")
    parser.add_argument("version", help="the python-rtmidi release these were built from")
    parser.add_argument("url", help="the published address of that directory")
    arguments = parser.parse_args()

    page = build_page(arguments.directory, arguments.version, arguments.url)
    (arguments.directory / "index.html").write_text(page, encoding="utf-8")
    (arguments.directory / ".nojekyll").touch()

    count = len(list(arguments.directory.glob("*.whl")))
    print(f"Indexed {count} wheel(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
