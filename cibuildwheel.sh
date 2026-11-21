#!/bin/sh
# Build wheels from a clean export of HEAD, forwarding all arguments
# to cibuildwheel. Note that uncommitted changes are not included, and
# relative paths in arguments resolve inside the export.
set -eu

root=$(cd "$(dirname "$0")" && pwd)
cibw=$root/bin/cibuildwheel

if [ ! -x "$cibw" ]; then
    echo "cibuildwheel not found: $cibw" >&2
    exit 1
fi

if [ -n "$(git -C "$root" status --porcelain)" ]; then
    echo "warning: working tree is dirty, building HEAD instead" >&2
fi

export_dir=$(mktemp -d "${TMPDIR:-/tmp}/rl-cibuildwheel.XXXXXX")
trap 'rm -rf "$export_dir"' EXIT INT TERM

git -C "$root" archive HEAD | tar -x -C "$export_dir"

case " $* " in
    *" --output-dir"*) ;;
    *)
        if [ -z "${CIBW_OUTPUT_DIR:-}" ]; then
            set -- --output-dir "$root/wheelhouse" "$@"
        fi
        ;;
esac

cd "$export_dir"
exec "$cibw" "$@"
