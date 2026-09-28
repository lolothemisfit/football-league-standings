import csv
from datetime import date
from pathlib import Path
from football_league_standings.models import MatchResult, RankedStanding
from football_league_standings.standings import calculate_week


_REQUIRED_HEADERS = (
    "week",
    "match_date",
    "home_team",
    "away_team",
    "home_goals",
    "away_goals",
)


def read_matches(path: str | Path) -> list[MatchResult]:
    """Read and validate match results from a CSV file."""
    csv_path = Path(path)
    matches: list[MatchResult] = []
    fixtures: set[tuple[date, str, str]] = set()

    with csv_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.reader(csv_file, strict=True)

        try:
            headers = [header.strip() for header in next(reader)]
        except StopIteration as error:
            raise ValueError(
                f"{csv_path}: CSV file is empty; expected a header row"
            ) from error
        except csv.Error as error:
            raise ValueError(
                f"{csv_path}: invalid CSV header: {error}"
            ) from error

        if len(headers) != len(set(headers)):
            raise ValueError(
                f"{csv_path}: duplicate column names in CSV header"
            )

        missing_headers = [
            header for header in _REQUIRED_HEADERS if header not in headers
        ]
        unexpected_headers = [
            header for header in headers if header not in _REQUIRED_HEADERS
        ]

        if missing_headers or unexpected_headers:
            messages = []

            if missing_headers:
                messages.append(
                    f"missing required header(s): {', '.join(missing_headers)}"
                )

            if unexpected_headers:
                messages.append(
                    f"unexpected header(s): {', '.join(unexpected_headers)}"
                )

            raise ValueError(f"{csv_path}: " + "; ".join(messages))

        header_indexes = {
            header: headers.index(header)
            for header in _REQUIRED_HEADERS
        }

        try:
            for row in reader:
                row_number = reader.line_num

                if len(row) != len(headers):
                    raise ValueError(
                        f"{csv_path}: row {row_number}: expected "
                        f"{len(headers)} columns, found {len(row)}"
                    )

                values = {
                    header: row[index].strip()
                    for header, index in header_indexes.items()
                }

                missing_values = [
                    header
                    for header, value in values.items()
                    if not value
                ]

                if missing_values:
                    raise ValueError(
                        f"{csv_path}: row {row_number}: "
                        f"missing required value(s): "
                        f"{', '.join(missing_values)}"
                    )

                try:
                    week = int(values["week"])
                except ValueError as error:
                    raise ValueError(
                        f"{csv_path}: row {row_number}: "
                        "week must be an integer"
                    ) from error

                try:
                    match_date = date.fromisoformat(values["match_date"])
                except ValueError as error:
                    raise ValueError(
                        f"{csv_path}: row {row_number}: "
                        "match_date must be a valid ISO date "
                        "(YYYY-MM-DD)"
                    ) from error

                if match_date.isoformat() != values["match_date"]:
                    raise ValueError(
                        f"{csv_path}: row {row_number}: "
                        "match_date must use YYYY-MM-DD format"
                    )

                try:
                    home_goals = int(values["home_goals"])
                except ValueError as error:
                    raise ValueError(
                        f"{csv_path}: row {row_number}: "
                        "home_goals must be an integer"
                    ) from error

                try:
                    away_goals = int(values["away_goals"])
                except ValueError as error:
                    raise ValueError(
                        f"{csv_path}: row {row_number}: "
                        "away_goals must be an integer"
                    ) from error

                if week < 1:
                    raise ValueError(
                        f"{csv_path}: row {row_number}: "
                        "week must be a positive integer"
                    )

                if home_goals < 0 or away_goals < 0:
                    raise ValueError(
                        f"{csv_path}: row {row_number}: "
                        "scores cannot be negative"
                    )

                home_team = values["home_team"]
                away_team = values["away_team"]

                if home_team == away_team:
                    raise ValueError(
                        f"{csv_path}: row {row_number}: "
                        "a team cannot play itself"
                    )

                expected_week = calculate_week(match_date)

                if week != expected_week:
                    raise ValueError(
                        f"{csv_path}: row {row_number}: "
                        f"week {week} does not match match_date "
                        f"{match_date.isoformat()} "
                        f"(expected week {expected_week})"
                    )

                fixture = (match_date, home_team, away_team)

                if fixture in fixtures:
                    raise ValueError(
                        f"{csv_path}: row {row_number}: "
                        f"duplicate fixture {home_team} vs {away_team} "
                        f"on {match_date.isoformat()}"
                    )

                fixtures.add(fixture)

                matches.append(
                    MatchResult(
                        week=week,
                        match_date=match_date,
                        home_team=home_team,
                        away_team=away_team,
                        home_goals=home_goals,
                        away_goals=away_goals,
                    )
                )

        except csv.Error as error:
            raise ValueError(
                f"{csv_path}: invalid CSV data near row "
                f"{reader.line_num}: {error}"
            ) from error

    return matches

_OUTPUT_HEADERS = (
    "position",
    "team",
    "played",
    "won",
    "drawn",
    "lost",
    "goals_for",
    "goals_against",
    "goal_average",
    "goal_difference",
    "points",
)


def write_standings(
    path: str | Path,
    ranked_standings: list[RankedStanding],
) -> None:
    """Write ranked league standings to a CSV file."""
    csv_path = Path(path)

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow(_OUTPUT_HEADERS)

        for ranked in ranked_standings:
            standing = ranked.standing

            if standing.goals_against == 0:
                goal_average = (
                    "inf" if standing.goals_for > 0 else "0"
                )
            else:
                goal_average = str(
                    standing.goals_for / standing.goals_against
                )

            writer.writerow(
                [
                    ranked.position,
                    standing.team,
                    standing.played,
                    standing.won,
                    standing.drawn,
                    standing.lost,
                    standing.goals_for,
                    standing.goals_against,
                    goal_average,
                    standing.goals_for - standing.goals_against,
                    standing.points,
                ]
            )