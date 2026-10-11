#!/usr/bin/env sh
# Download the SNAP web-BerkStan edge list into data/ (about 20 MB compressed,
# 110 MB uncompressed). Public, no account needed.
set -eu

DEST="data/web-BerkStan.txt"
URL="https://snap.stanford.edu/data/web-BerkStan.txt.gz"

if [ -f "$DEST" ]; then
    echo "dataset present: $DEST"
    exit 0
fi

echo "downloading $URL"
curl -fsSL -o "$DEST.gz" "$URL"
gzip -d "$DEST.gz"
echo "saved $DEST"
