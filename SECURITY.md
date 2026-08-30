# Security

This repository publishes binaries other people install, so reports about them matter more than
its size suggests.

If a published wheel looks tampered with, a bundled library ships a known vulnerability, or the
build pipeline fetches something it should not: use GitHub's private
[Report a vulnerability](https://github.com/paperisiili/python-rtmidi-wheels/security/advisories/new)
for this repository rather than a public issue, so a real problem is not advertised before it
can be handled.

To check a wheel you have: every link on the index names its SHA-256, each release carries a
`SHA256SUMS` file, and each wheel has a sigstore attestation —
`gh attestation verify <wheel> --repo paperisiili/python-rtmidi-wheels`.

A vulnerability in python-rtmidi itself belongs upstream:
<https://github.com/SpotlightKid/python-rtmidi>.
