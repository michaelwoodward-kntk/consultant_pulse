"""CLI entry point for local checks."""

from __future__ import annotations

import argparse

from consultant_pulse.api import ConsultantPulseApi
from consultant_pulse.transform import normalize_score


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Consultant Pulse helpers")
    parser.add_argument("--score", type=float)
    parser.add_argument("--show-config", action="store_true")
    parser.add_argument("--bronze-ddl", action="store_true")
    args = parser.parse_args(argv)
    if args.score is None and not args.show_config and not args.bronze_ddl:
        parser.error("pass --score, --show-config, or --bronze-ddl")

    if args.score is not None:
        print(normalize_score(args.score))

    if args.show_config or args.bronze_ddl:
        api = ConsultantPulseApi()
        if args.show_config:
            described = api.describe()
            for key in ("catalog", "schema", "volume", "bronze_table", "host", "profile"):
                print(f"{key}={described[key]}")
        if args.bronze_ddl:
            print(api.bronze_ddl())


if __name__ == "__main__":
    main()
