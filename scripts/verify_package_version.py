"""Verify built Slugger package artifacts report the expected version."""

from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path


def main() -> int:
    expected = sys.argv[1]
    dist = Path("dist")
    wheel = next(dist.glob(f"slugger-{expected}-*.whl"))
    sdist = dist / f"slugger-{expected}.tar.gz"
    with zipfile.ZipFile(wheel) as zf:
        metadata = zf.read(f"slugger-{expected}.dist-info/METADATA").decode()
    if f"Version: {expected}" not in metadata:
        raise SystemExit(f"wheel metadata does not report version {expected}")
    with tarfile.open(sdist) as tf:
        member = next(m for m in tf.getmembers() if m.name.endswith("/PKG-INFO"))
        extracted = tf.extractfile(member)
        if extracted is None:
            raise SystemExit("sdist PKG-INFO could not be read")
        metadata = extracted.read().decode()
    if f"Version: {expected}" not in metadata:
        raise SystemExit(f"sdist metadata does not report version {expected}")
    print(f"Built wheel and sdist report version {expected}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
