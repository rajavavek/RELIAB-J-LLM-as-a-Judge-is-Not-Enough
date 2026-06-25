from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="RELIAB-J command-line interface")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()
    if args.version:
        from reliabj import __version__
        print(__version__)
    else:
        parser.print_help()
