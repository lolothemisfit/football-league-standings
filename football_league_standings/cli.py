import argparse
import sys
from pathlib import Path

from football_league_standings.csv_io import read_matches, write_standings
from football_league_standings.standings import (
    calculate_standings,
    rank_standings,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Calculate football league standings from match results."
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to the input match-results CSV file.",
    )

    parser.add_argument(
        "--through-week",
        required=True,
        type=int,
        help="Calculate standings through this week.",
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path for the output standings CSV file.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.through_week < 1:
        parser.error("--through-week must be a positive integer")

    if not args.input.is_file():
        parser.error(f"input file does not exist: {args.input}")

    try:
        matches = read_matches(args.input)
        standings = calculate_standings(
            matches,
            through_week=args.through_week,
        )
        ranked_standings = rank_standings(standings)

        write_standings(
            args.output,
            ranked_standings,
        )

    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    return 0