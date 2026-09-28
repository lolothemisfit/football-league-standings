import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from football_league_standings.cli import main


class TestCli(unittest.TestCase):

    def test_main_generates_output_csv(self):
        input_csv = (
            "week,match_date,home_team,away_team,home_goals,away_goals\n"
            "1,1974-08-17,Team A,Team B,2,1\n"
            "1,1974-08-17,Team C,Team D,1,1\n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "input.csv"
            output_path = temp_path / "output.csv"

            input_path.write_text(input_csv)

            with patch(
                "sys.argv",
                [
                    "cli",
                    "--input",
                    str(input_path),
                    "--through-week",
                    "1",
                    "--output",
                    str(output_path),
                ],
            ):
                result = main()

            self.assertEqual(result, 0)
            self.assertTrue(output_path.exists())

            with output_path.open(newline="") as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(len(rows), 4)
            self.assertEqual(rows[0]["position"], "1")
            self.assertEqual(rows[0]["team"], "Team A")
            self.assertEqual(rows[0]["points"], "2")

    def test_main_rejects_missing_input_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.csv"

            with patch(
                "sys.argv",
                [
                    "cli",
                    "--input",
                    str(Path(temp_dir) / "does_not_exist.csv"),
                    "--through-week",
                    "1",
                    "--output",
                    str(output_path),
                ],
            ):
                with self.assertRaises(SystemExit) as context:
                    main()

            self.assertEqual(context.exception.code, 2)
            self.assertFalse(output_path.exists())

    def test_main_rejects_invalid_week(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "input.csv"
            output_path = Path(temp_dir) / "output.csv"

            input_path.write_text(
                "week,home_team,home_score,away_team,away_score\n"
            )

            with patch(
                "sys.argv",
                [
                    "cli",
                    "--input",
                    str(input_path),
                    "--through-week",
                    "0",
                    "--output",
                    str(output_path),
                ],
            ):
                with self.assertRaises(SystemExit) as context:
                    main()

            self.assertEqual(context.exception.code, 2)
            self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()