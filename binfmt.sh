#!/bin/sh
# Register qemu-aarch64 binfmt handlers in the docker host kernel and
# verify aarch64 emulation. Must be re-run after every docker VM reboot.
# Requires the docker environment of the cibuildwheel machine.
set -eu

docker run --privileged --rm tonistiigi/binfmt --install arm64

# Pre-pull the probe image; on Docker 24.0.0 the pull reports a spurious
# "No such image" although the image was stored (moby/moby#45558).
docker pull --platform linux/arm64 debian:trixie-slim >/dev/null 2>&1 || true

if ! machine=$(docker run --rm --platform linux/arm64 debian:trixie-slim uname -m) \
    || [ "$machine" != "aarch64" ]; then
    echo "aarch64 emulation is not working" >&2
    exit 1
fi

echo "aarch64 emulation OK"
