import tempfile
import unittest
from datetime import date
from pathlib import Path
import csv

from football_league_standings.csv_io import read_matches, write_standings
from football_league_standings.models import (
    MatchResult,
    RankedStanding,
    TeamStanding,
)


class TestReadMatches(unittest.TestCase):
	header = "week,match_date,home_team,away_team,home_goals,away_goals\n"

	def read_csv(self, content: str) -> list[MatchResult]:
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory) / "matches.csv"
			path.write_text(content, encoding="utf-8")
			return read_matches(path)

	def test_parses_values_and_strips_surrounding_whitespace(self):
		matches = self.read_csv(
			self.header + " 1 , 1974-08-17 , Arsenal , Leeds United , 3 , 1 \n"
		)

		self.assertEqual(
			matches,
			[MatchResult(1, date(1974, 8, 17), "Arsenal", "Leeds United", 3, 1)],
		)

	def test_rejects_missing_required_header(self):
		with self.assertRaisesRegex(ValueError, "missing required header.*week"):
			self.read_csv(
				"match_date,home_team,away_team,home_goals,away_goals\n"
				"1974-08-17,Arsenal,Leeds United,3,1\n"
			)

	def test_rejects_malformed_row_width(self):
		with self.assertRaisesRegex(ValueError, "row 2: expected 6 columns"):
			self.read_csv(self.header + "1,1974-08-17,Arsenal,Leeds United,3\n")

	def test_rejects_missing_value_and_blank_team(self):
		for row, expected in (
			("1,1974-08-17,,Leeds United,3,1\n", "home_team"),
			("1,1974-08-17,Arsenal,Leeds United,,1\n", "home_goals"),
		):
			with self.subTest(row=row):
				with self.assertRaisesRegex(ValueError, expected):
					self.read_csv(self.header + row)

	def test_rejects_invalid_date_and_non_integer_fields(self):
		invalid_rows = (
			("one,1974-08-17,Arsenal,Leeds United,3,1\n", "week must be an integer"),
			("1,not-a-date,Arsenal,Leeds United,3,1\n", "valid ISO date"),
			("1,1974-08-17,Arsenal,Leeds United,three,1\n", "home_goals must be an integer"),
			("1,1974-08-17,Arsenal,Leeds United,3,one\n", "away_goals must be an integer"),
		)
		for row, expected in invalid_rows:
			with self.subTest(row=row):
				with self.assertRaisesRegex(ValueError, expected):
					self.read_csv(self.header + row)

	def test_rejects_negative_scores(self):
		with self.assertRaisesRegex(ValueError, "scores cannot be negative"):
			self.read_csv(self.header + "1,1974-08-17,Arsenal,Leeds United,-1,0\n")

	def test_rejects_team_playing_itself(self):
		with self.assertRaisesRegex(ValueError, "team cannot play itself"):
			self.read_csv(self.header + "1,1974-08-17,Arsenal,Arsenal,1,0\n")

	def test_rejects_week_that_does_not_match_match_date(self):
		with self.assertRaisesRegex(ValueError, "does not match match_date"):
			self.read_csv(self.header + "2,1974-08-17,Arsenal,Leeds United,3,1\n")

	def test_rejects_duplicate_fixture_but_accepts_reverse_fixture(self):
		duplicate = (
			self.header
			+ "1,1974-08-17,Arsenal,Leeds United,3,1\n"
			+ "1,1974-08-17,Arsenal,Leeds United,3,1\n"
		)
		with self.assertRaisesRegex(ValueError, "duplicate fixture"):
			self.read_csv(duplicate)

		reverse = (
			self.header
			+ "1,1974-08-17,Arsenal,Leeds United,3,1\n"
			+ "1,1974-08-17,Leeds United,Arsenal,0,2\n"
		)
		matches = self.read_csv(reverse)
		self.assertEqual(len(matches), 2)


class TestWriteStandings(unittest.TestCase):

    def create_ranked_standings(self):
        return [
            RankedStanding(
                position=1,
                standing=TeamStanding(
                    team="Arsenal",
                    played=2,
                    won=2,
                    drawn=0,
                    lost=0,
                    goals_for=5,
                    goals_against=2,
                    points=4,
                ),
            ),
            RankedStanding(
                position=2,
                standing=TeamStanding(
                    team="Chelsea",
                    played=2,
                    won=1,
                    drawn=1,
                    lost=0,
                    goals_for=3,
                    goals_against=2,
                    points=3,
                ),
            ),
        ]

    def test_writes_expected_headers_and_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standings.csv"

            write_standings(
                path,
                self.create_ranked_standings(),
            )

            with path.open(
                "r",
                newline="",
                encoding="utf-8",
            ) as csv_file:
                rows = list(csv.reader(csv_file))

        self.assertEqual(
            rows[0],
            [
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
            ],
        )

        self.assertEqual(
            rows[1],
            [
                "1",
                "Arsenal",
                "2",
                "2",
                "0",
                "0",
                "5",
                "2",
                "2.5",
                "3",
                "4",
            ],
        )

        self.assertEqual(
            rows[2],
            [
                "2",
                "Chelsea",
                "2",
                "1",
                "1",
                "0",
                "3",
                "2",
                "1.5",
                "1",
                "3",
            ],
        )

    def test_preserves_ranked_order(self):
        ranked = [
            RankedStanding(
                position=1,
                standing=TeamStanding(
                    team="Liverpool",
                    played=1,
                    won=1,
                    goals_for=2,
                    goals_against=0,
                    points=2,
                ),
            ),
            RankedStanding(
                position=1,
                standing=TeamStanding(
                    team="Arsenal",
                    played=1,
                    won=1,
                    goals_for=2,
                    goals_against=0,
                    points=2,
                ),
            ),
        ]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standings.csv"

            write_standings(path, ranked)

            with path.open(
                "r",
                newline="",
                encoding="utf-8",
            ) as csv_file:
                rows = list(csv.reader(csv_file))

        self.assertEqual(rows[1][1], "Liverpool")
        self.assertEqual(rows[2][1], "Arsenal")

    def test_handles_zero_goals_against(self):
        ranked = [
            RankedStanding(
                position=1,
                standing=TeamStanding(
                    team="Ipswich Town",
                    played=1,
                    won=1,
                    goals_for=2,
                    goals_against=0,
                    points=2,
                ),
            ),
            RankedStanding(
                position=2,
                standing=TeamStanding(
                    team="Unused Team",
                    played=0,
                    goals_for=0,
                    goals_against=0,
                    points=0,
                ),
            ),
        ]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standings.csv"

            write_standings(path, ranked)

            with path.open(
                "r",
                newline="",
                encoding="utf-8",
            ) as csv_file:
                rows = list(csv.reader(csv_file))

        self.assertEqual(rows[1][8], "inf")
        self.assertEqual(rows[2][8], "0")

    def test_writes_empty_standings_with_header_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "standings.csv"

            write_standings(path, [])

            with path.open(
                "r",
                newline="",
                encoding="utf-8",
            ) as csv_file:
                rows = list(csv.reader(csv_file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "position")
        self.assertEqual(len(rows[0]), 11)

if __name__ == "__main__":
	unittest.main()
