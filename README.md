# python-rtmidi wheels

Unofficial builds of [python-rtmidi](https://github.com/SpotlightKid/python-rtmidi) for the
CPython versions upstream does not publish wheels for. Upstream stops at 3.12; on anything
newer, pip compiles the source distribution, which needs a C++ compiler and the Python and ALSA
headers on the machine. These wheels remove that requirement.

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
works as usual. `--only-binary` (uv's `no-build-package`) turns a missing wheel into an error
that says what is wrong, instead of a silent fall back to compiling the source distribution.

## What you get

CPython 3.13, 3.14 and free-threaded 3.14t, across five targets:

| Platform | Architectures | Needs | MIDI backends |
| -------- | ------------- | ----- | ------------- |
| Linux    | x86_64, aarch64 | glibc 2.24 or newer | ALSA and JACK |
| macOS    | x86_64, arm64 | macOS 10.13 (3.13) / 10.15 (3.14) on Intel, 11 on arm64 | CoreMIDI |
| Windows  | AMD64         | nothing extra | Windows multimedia |

The Linux wheels bundle libjack — its LGPL license text travels inside each wheel — and use the
system's libasound. The Windows wheels bundle msvcp140.dll, so the Visual C++ redistributable
is not needed. On 3.14t, importing python-rtmidi re-enables the GIL for that process (its
extension predates free-threading); installing still needs nothing beyond pip. Not built, and
falling back to the source distribution: musllinux (Alpine), 3.13t, and Windows arm64.

## Verifying

Wheels differing only in the build number after the version — the `-1-` in
`python_rtmidi-1.5.8-1-cp313-…` — are rebuilds of the same release, newest preferred
automatically, and no published wheel ever changes or disappears. Each index link names its
wheel's SHA-256, which pip checks on download;
[pinning hashes](https://pip.pypa.io/en/stable/topics/secure-installs/) makes that a
requirement:

```
--find-links https://paperisiili.github.io/python-rtmidi-wheels/
--only-binary python-rtmidi
python-rtmidi==1.5.8 \
    --hash=sha256:0123…cdef \
    --hash=sha256:89ab…4567
```

One `--hash` per wheel that might be picked, with digests copied from the release's
`SHA256SUMS` or the index links; python-rtmidi depends on nothing, so that file is complete as
shown. uv records digests on its own in `uv.lock`, as does `pip-compile --generate-hashes`.
Every wheel also carries a sigstore attestation binding it to the workflow run that built it:

```
gh attestation verify python_rtmidi-….whl --repo paperisiili/python-rtmidi-wheels
```

## How they are built

This is not a fork — no copy of python-rtmidi lives here. A public GitHub Actions workflow
downloads the release's own source distribution from PyPI, verifies it against a digest pinned
in this repository, and builds it unmodified with the settings in `cibuildwheel.toml`, running
upstream's test suite on every wheel. Each build batch is published as a numbered, immutable
GitHub release holding the wheels, their digests, and the source of the bundled libjack, and
the index page is regenerated over all of them. The files here document their own decisions;
`MAINTAINING.md` holds the runbook.

## License

The build configuration and scripts in this repository are public domain under CC0 1.0
(`LICENSE`); that grant covers this repository's files only, not the wheels. The wheels carry
python-rtmidi's MIT license. The Linux wheels additionally bundle libjack from
[jack2](https://github.com/jackaudio/jack2) under the LGPL v2.1 or later, with the license text
and notice inside each wheel and the exact source attached to each release; the Windows wheels
bundle msvcp140.dll under the terms Microsoft grants for redistributing that runtime's files.
