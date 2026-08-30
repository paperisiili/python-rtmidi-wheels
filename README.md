# python-rtmidi wheels

Unofficial builds of [python-rtmidi](https://github.com/SpotlightKid/python-rtmidi) for the
CPython versions upstream does not publish wheels for.

## Installing

```
pip install --only-binary python-rtmidi --find-links https://paperisiili.github.io/python-rtmidi-wheels/ python-rtmidi
```

or, in a `requirements.txt`:

```
--find-links https://paperisiili.github.io/python-rtmidi-wheels/
--only-binary python-rtmidi
python-rtmidi
```

or, for uv, in a `pyproject.toml` beside an ordinary `python-rtmidi` dependency under
`[project]`:

```
[tool.uv]
find-links = ["https://paperisiili.github.io/python-rtmidi-wheels/"]
no-build-package = ["python-rtmidi"]
```

pip picks the wheel matching the interpreter it runs under, and pinning `python-rtmidi==1.5.8`
works as usual. `--only-binary` (uv's `no-build-package`) is worth the extra words: without it,
an interpreter with no wheel here quietly falls back to compiling upstream's source
distribution, which needs the C++ compiler and headers these wheels exist to spare — with it, a
missing wheel is an error that says what is wrong.

A `pyproject.toml` has nowhere under `[project]` to put any of this. That table describes
dependencies without saying where they come from, and the only address it can carry is a direct
link to one file, which would pin a single Python version and a single platform. Where wheels
are found is the installer's own setting every time: the uv table above (or its named-index
spelling, `[[tool.uv.index]]` with `format = "flat"`), `PIP_FIND_LINKS` or `pip.conf` for pip
itself.

## Why

Upstream's newest release ships wheels for CPython 3.8 through 3.12 only. On anything newer pip
falls back to the source distribution, so installing python-rtmidi means having a C++ compiler,
the Python headers and the ALSA headers on the machine. These wheels remove that requirement.

## What gets built

Fifteen wheels per release: CPython 3.13, 3.14 and free-threaded 3.14t, across five targets.

| Platform | Architectures | Needs | MIDI backends |
| -------- | ------------- | ----- | ------------- |
| Linux    | x86_64, aarch64 | glibc 2.24 or newer | ALSA and JACK |
| macOS    | x86_64, arm64 | macOS 10.13 (3.13) / 10.15 (3.14) on Intel, 11 on arm64 | CoreMIDI |
| Windows  | AMD64         | nothing extra | Windows multimedia |

The Linux wheels are built on `manylinux_2_28` images; auditwheel grades what they actually
require, which comes out at glibc 2.24. They link `libasound` from the system rather than
bundling it, which is what upstream does and what any machine with ALSA already satisfies.
libjack is bundled instead, so a wheel built against JACK still imports on a machine that has
never installed it — its LGPL license text and a provenance notice travel inside each wheel, in
`dist-info/licenses/jack2/`. The Windows wheels bundle msvcp140.dll, so they work without the
Visual C++ redistributable installed.

python-rtmidi's extension predates free-threading, so on 3.14t importing it re-enables the GIL
for that process (CPython prints a notice); the install itself still needs nothing beyond pip.
Not built, and falling back to the source distribution: musllinux (Alpine and other musl
systems, matching upstream), 3.13t (its free-threading was experimental and build tooling has
dropped it), and Windows arm64.

Every wheel is tested after building — upstream's CI-marked pytest suite, then an assertion on
the backends it actually ended up with.

## Releases and versions

The wheels live as GitHub release assets, and the index page is only links to them. Releases
are numbered v1, v2, … in this repository's own sequence; each states which python-rtmidi
version it builds and why it exists. A release never changes after publication, so a wheel URL
and its digest are permanent, and hash-pinned installs keep resolving as long as this
repository exists.

Each wheel's filename carries its release number as the wheel build tag — the `-1-` in
`python_rtmidi-1.5.8-1-cp313-…` — so rebuilt wheels for the same python-rtmidi version coexist
with their predecessors under distinct names, and installers prefer the highest build number on
their own. Superseding a build means cutting a new release, not touching an old one.

## Verifying

Each link on the index names its wheel's SHA-256 in the fragment, which pip checks on download
and matches when an install [pins hashes](https://pip.pypa.io/en/stable/topics/secure-installs/).
Every release carries a `SHA256SUMS` file, and every wheel a sigstore attestation binding it to
the workflow run that built it:

```
gh attestation verify python_rtmidi-….whl --repo paperisiili/python-rtmidi-wheels
```

## Building

This is not a fork. No copy of python-rtmidi lives here — the build downloads the release's own
source distribution from PyPI, verifies it against a digest pinned in `fetch_sdist.py`, and
builds it unmodified with the settings in `cibuildwheel.toml`. The bundled libjack is built from
a jack2 checkout pinned by commit, and the exact source tree is archived with each release.

Three workflows, run from the Actions tab:

- **Build wheels** builds and checks a full wheel set from a python-rtmidi version (empty input
  means `DEFAULT_RTMIDI_VERSION`) and publishes nothing. It also runs monthly on its own, as a
  canary: a red run means a runner image, package, or upstream surface rotted, and GitHub's
  failure email says so before it matters.
- **Release wheels** takes a green build run's ID and release notes, stamps the wheels with the
  next release number, and publishes them as that GitHub release — the deliberate step between
  building and serving.
- **Publish index** regenerates the Pages index over every release. Release wheels ends by
  running it; dispatched alone it republishes page text or reflects a deleted release.

Moving to a new upstream release: change `DEFAULT_RTMIDI_VERSION` in
`.github/workflows/build-wheels.yml`, add the sdist digest to `PINNED` in `fetch_sdist.py`, and
update the version this README names. A new CPython version is one entry in the `build` line of
`cibuildwheel.toml`, plus whatever cibuildwheel bump first supports it. The repository retires
when upstream ships wheels for these Pythons itself — nothing here shadows a wheel upstream
provides, and pip pools this index with PyPI either way.

Publishing needs GitHub Pages set to deploy from GitHub Actions, once, under Settings → Pages.
Every action used here is one of GitHub's own, so a repository restricting Actions to its owner
needs "Allow actions created by GitHub" ticked as well, but nothing looser. The repository has
to stay public for Pages and the Actions minutes.

## License

The build configuration and scripts in this repository are placed in the public domain under
CC0 1.0; see `LICENSE`. That grant covers this repository's files only — not python-rtmidi, and
not the wheels.

The wheels carry python-rtmidi under its MIT license, which travels inside every wheel. The
Linux wheels additionally bundle libjack from [jack2](https://github.com/jackaudio/jack2),
under the GNU Lesser General Public License v2.1 or later: the license text and notice are
inside each wheel, and the exact source is attached to each release. The Windows wheels bundle
msvcp140.dll under the terms Microsoft grants for redistributing that runtime's files.
