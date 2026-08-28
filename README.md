# python-rtmidi wheels

Unofficial builds of [python-rtmidi](https://github.com/SpotlightKid/python-rtmidi) for the CPython versions upstream does not publish wheels for.

This is not a fork. No copy of python-rtmidi lives here — the workflow downloads the release's own source distribution from PyPI and builds that unmodified. What this repository holds is the build configuration and the workflow that runs it.

## Why

Upstream's newest release is 1.5.8, from November 2023, and it ships wheels for CPython 3.8 through 3.12 only. On anything newer pip falls back to the source distribution, so installing python-rtmidi means having a C++ compiler, the Python headers and the ALSA headers on the machine. These wheels remove that requirement for 3.13 and 3.14.

## What gets built

Ten wheels, CPython 3.13 and 3.14 across five targets:

| Platform | Architectures | MIDI backend |
| -------- | ------------- | ------------ |
| Linux    | x86_64, aarch64 (`manylinux_2_28`) | ALSA and JACK |
| macOS    | x86_64, arm64 | CoreMIDI |
| Windows  | AMD64         | Windows multimedia |

The Linux wheels link `libasound.so.2` from the system rather than bundling it, which is what upstream does and what any machine with ALSA already satisfies. libjack is bundled rather than left to the system, so a wheel built against JACK still imports on a machine that has never installed it. `manylinux_2_28` needs glibc 2.28 or newer.

Every wheel is checked after building for the backends it actually ended up with.

## Using them

```
pip install --find-links https://paperisiili.github.io/python-rtmidi-wheels/ python-rtmidi==1.5.8
```

or, in a `requirements.txt`:

```
--find-links https://paperisiili.github.io/python-rtmidi-wheels/
python-rtmidi==1.5.8
```

pip picks the wheel matching the interpreter it is running under and falls back to building upstream's source distribution from PyPI when none matches, so pinning this source does not strand anyone on a Python that has no wheel here. If the address is unreachable pip warns and carries on to PyPI rather than failing the install.

## Building

The workflow runs on a pushed tag matching `v*`, and on request from the Actions tab. A manual run takes a version to build; leaving it empty uses `DEFAULT_RTMIDI_VERSION` from the workflow, which is the one line to change when moving to a new upstream release.

Wheels are published to GitHub Pages, which needs its source set to GitHub Actions once, under Settings then Pages. Every action used here is one of GitHub's own, so a repository restricting Actions to its owner needs "Allow actions created by GitHub" ticked as well, but nothing looser. The repository has to stay public for both Pages and the Actions minutes.

`cibuildwheel.toml` carries the build settings. It is passed with `--config-file`, which replaces the equivalent block inside the source distribution rather than merging with it, so upstream's own choice of Python versions does not carry over.

Two details in there are worth knowing before editing it. The build marks a platform backend as required only when JACK is absent, so on Linux, where JACK is installed, ALSA is optional as far as the build is concerned — the assertion in `test-command` is what holds that line, not the build itself. And architectures are left at cibuildwheel's default on Linux and macOS because the workflow gives each architecture its own native runner; Windows is pinned to 64-bit, which that default would otherwise widen.

## License

python-rtmidi is MIT, and its license travels inside every wheel.

The Linux wheels additionally contain libjack from [jack2](https://github.com/jackaudio/jack2) v1.9.22, under the GNU Lesser General Public License version 2.1 or later. jack2's repository-level `COPYING` is GPLv2 and covers the server; the client library bundled here carries LGPL headers of its own. Redistributing the Linux wheels therefore means meeting that license's terms, and jack2's source is at the address above.

The Windows wheels contain msvcp140.dll, Microsoft's C++ runtime, so that they work on a machine without the Visual C++ redistributable installed. It is redistributed under the terms Microsoft grants for that runtime's files.

The build configuration and scripts here are yours to treat as you like.
