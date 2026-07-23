# Third-party notices

KORYAO Vector60 uses the following unmodified upstream packages through their public package
interfaces. No complete third-party repository is vendored into KORYAO.

## VTracer

- Upstream: `visioncortex/vtracer`
- License: MIT
- Version: `0.6.15`
- Source commit: `fd9cdb08e622f237eb05be553a020ddc9e4c47a1`
- Purpose: generate initial color-vector candidates for the optional Artisan Vector60 pass.

## skia-pathops

- Upstream: `fonttools/skia-pathops`
- License: BSD-3-Clause
- Version: `0.9.2`
- Source commit: `c11e91f442462d1efc1a45d76c76ae9e74aa0de4`
- Purpose: bounded path union, intersection, difference, and xor operations after safety gates.

## svgpathtools

- Upstream: `mathandy/svgpathtools`
- License: MIT
- Version: `1.7.2`
- Source commit: `284fc2c591d852ef51b6168e8d842065f3e41cc2`
- Purpose: curve, tangent, curvature, intersection, and area analysis for geometry validation.

## SVGO

- Upstream: `svg/svgo`
- License: MIT
- Version: `4.0.2`
- Source commit: `b2309cf541aee11634eb653157b0ff86ab326e98`
- Purpose: final SVG cleanup and compression before KORYAO safety validation.

The optional Vector60 dependency group pins the Python packages above. SVGO is pinned in the root
Node development dependencies. diffvg and LIVE remain research references and are not production
dependencies for this release candidate.
