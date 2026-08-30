# Maintaining

The files here document their own decisions in place — this is only the choreography between
them. Nothing on this page should matter to anyone installing wheels; that story is
`README.md`.

## Publishing a build

1. Run **Build wheels** from the Actions tab, with a python-rtmidi version or empty for
   `DEFAULT_RTMIDI_VERSION`. It fetches and digest-checks the sdist, builds and tests the full
   wheel set, and asserts the result (`check_wheels.py`). It publishes nothing.
2. Look the run over — each platform's "Inspect what was built" step lists every wheel's
   contents, and the check job is the contract.
3. Run **Release wheels** with the green run's ID and one paragraph of notes; the index shows
   only that first paragraph, the release page everything. It numbers the release (v1, v2, …),
   stamps the number into each wheel as its build tag, writes SHA256SUMS, attests the wheels,
   attaches the jack2 source, and republishes the index.
4. Releases are immutable: superseding a build means cutting a new release — the higher build
   number wins automatically — never editing a published one. Deleting a release breaks every
   pin against it; it is for withdrawal, not correction, and **Publish index** run on its own
   afterwards updates the page. It also reruns alone for page-text changes, with no build.

## Moving to a new upstream release

Change `DEFAULT_RTMIDI_VERSION` in `.github/workflows/build-wheels.yml`, and add the sdist's
digest to `PINNED` in `fetch_sdist.py` — PyPI's JSON reports it, and an unpinned build prints
it. Update the versions named in `README.md` and the repository description. Then build,
inspect, release.

## Adding a CPython version

Add it to `build` in `cibuildwheel.toml` and bump `EXPECTED_WHEELS` in the build workflow;
supporting it may first need a newer `CIBUILDWHEEL_VERSION`. The repository retires when
upstream ships wheels for these Pythons itself — nothing here shadows a wheel upstream
provides, and pip pools this index with PyPI either way.

## The canary

The build workflow also runs monthly on its schedule and publishes nothing; a red run means
something outside this repository rotted — a runner image, a package name, an upstream surface
— and GitHub emails about failed runs by default. Two quirks: cron workflows are disabled after
about 60 days without repository activity (GitHub emails; re-enabling is one click on the
Actions page), and failure emails for scheduled runs go to whoever last edited the workflow
file's schedule.

## What is pinned, and where

- The python-rtmidi sdist: `PINNED` in `fetch_sdist.py`.
- cibuildwheel: `CIBUILDWHEEL_VERSION` in the build workflow.
- jack2: `JACK2_VERSION` / `JACK2_COMMIT` in the build workflow, and the same version and
  commit in `cibuildwheel.toml`'s before-all — keep the two files in step.
- Actions are GitHub's own only, by major version tag; the canary is what catches breakage.

macos-15-intel is GitHub's last Intel runner class. When it retires, either move that leg to an
arm64 runner cross-compiling x86_64 (cibuildwheel's archs setting, tests under Rosetta) or drop
it deliberately.

## One-time repository setup

GitHub Pages set to deploy from GitHub Actions (Settings → Pages); "Allow actions created by
GitHub" if Actions are restricted; private vulnerability reporting enabled for `SECURITY.md`.
The repository stays public for Pages and the Actions minutes.
