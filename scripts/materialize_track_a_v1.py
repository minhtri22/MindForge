#!/usr/bin/env python3
"""Compatibility entrypoint for the Track-A Benchmark v1 R1 materializer.

The canonical implementation is ``materialize_track_a_v1_r1.py``. This wrapper
exists so the historical command

    python scripts/materialize_track_a_v1.py --out benchmarks/track-a-capability-v1

continues to work without carrying duplicate benchmark-generation logic.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from materialize_track_a_v1_r1 import ROOT, main as r1_main


def _canonical_out() -> Path:
    return ROOT.resolve()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="benchmarks/track-a-capability-v1",
        help="Compatibility option. Only the canonical Track-A v1 path is supported.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    requested = Path(args.out)
    if not requested.is_absolute():
        requested = Path.cwd() / requested
    if requested.resolve() != _canonical_out():
        raise SystemExit(
            "Track-A v1 R1 materialization is frozen to "
            f"{_canonical_out()}; got {requested.resolve()}"
        )
    r1_main()


if __name__ == "__main__":
    main()
