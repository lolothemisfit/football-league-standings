# Football League Standings

A Python command-line application that reads football match results from a CSV file and generates league standings through a specified week.

The application calculates each team's matches played, wins, draws, losses, goals for, goals against, goal average, goal difference, points, and league position.

## Requirements

* Python 3.10 or later
* Python standard library
* No external packages are required to run the application
* The automated test suite uses Python's built-in `unittest` framework

## Project Structure

```text
football-league-standings/
├── AI/
│   └── <Copilot conversation history>
├── data/
│   ├── first_division_1974_75.csv
│   └── standings_after_week_10.csv
├── football_league_standings/
│   ├── cli.py
│   ├── csv_io.py
│   ├── main.py
│   ├── models.py
│   └── standings.py
├── tests/
│   ├── test_cli.py
│   ├── test_csv_io.py
│   └── test_standings.py
├── AI-COLLABORATION.md
├── GITHUB_COPILOT_INSTRUCTIONS.md
└── README.md
```

## Running the Application

**All commands in this section must be run from the project root directory** (`football-league-standings/`).

For example:

```bash
cd football-league-standings
```

You can verify that you are in the project root by checking that the `data`, `football_league_standings`, and `tests` directories are present:

```bash
ls
```

Do not run the application from inside the `data`, `tests`, `AI`, or `football_league_standings` directories.

### Run the supplied example

The project includes a sample First Division 1974–75 match-results CSV:

```text
data/first_division_1974_75.csv
```

From the **project root**, run:

```bash
python3 -m football_league_standings.main \
  --input data/first_division_1974_75.csv \
  --through-week 10 \
  --output data/standings_after_week_10.csv
```

The application will read the supplied match results through week 10 and create:

```text
data/standings_after_week_10.csv
```

You can inspect the generated CSV with:

```bash
cat data/standings_after_week_10.csv
```

### Command-line arguments

| Argument         | Description                           |
| ---------------- | ------------------------------------- |
| `--input`        | Path to the input match-results CSV   |
| `--through-week` | Calculate standings through this week |
| `--output`       | Path for the generated standings CSV  |

For example, to process a different input file from the project root:

```bash
python3 -m football_league_standings.main \
  --input data/input.csv \
  --through-week 10 \
  --output data/output.csv
```

## Input CSV Format

The input CSV must contain exactly these required columns:

```text
week,match_date,home_team,away_team,home_goals,away_goals
```

Example:

```csv
week,match_date,home_team,away_team,home_goals,away_goals
1,1974-08-17,Team A,Team B,2,1
1,1974-08-17,Team C,Team D,1,1
```

The application validates the input data before processing it.

Validation includes:

* required headers
* duplicate headers
* unexpected headers
* correct number of columns
* missing values
* positive week numbers
* valid ISO dates (`YYYY-MM-DD`)
* non-negative scores
* preventing a team from playing itself
* checking that the week matches the match date
* duplicate fixture detection

## Output CSV Format

The generated CSV contains:

```text
position,team,played,won,drawn,lost,goals_for,goals_against,goal_average,goal_difference,points
```

The supplied example generates a standings table containing the teams and statistics calculated from matches through week 10.

## Running the Tests

**Run this command from the project root directory.**

```bash
python3 -m unittest discover -s tests
```

The current test suite contains 29 tests.

Expected result:

```text
Ran 29 tests in ...
OK
```

The tests cover:

* CSV reading and validation
* standings calculations
* ranking and tied positions
* CSV output
* CLI execution
* invalid CLI arguments
* missing input files

## Application Entry Point

The executable entry point is:

```text
football_league_standings.main
```

It delegates command-line processing to `football_league_standings.cli`.

The application accepts:

```text
--input
--through-week
--output
```

The `--through-week` value must be a positive integer.

## AI-Assisted Development

This project was developed with assistance from **GitHub Copilot**, not Claude.

The assessment specification refers to Claude-specific files and session data. Since Claude was not used for this project, no fabricated Claude session data or Claude conversation history has been included.

Instead, the repository contains equivalent documentation of the actual AI-assisted development process:

* `GITHUB_COPILOT_INSTRUCTIONS.md` — project instructions used for AI assistance
* `AI-COLLABORATION.md` — documentation of the AI collaboration process
* `AI_REFLECTION.md` — reflection on the AI-assisted development experience
* `AI/` — exported Copilot conversation history

## Verification

The final application was verified by:

1. Running the complete automated test suite.
2. Running the CLI from the project root against the supplied match-results CSV.
3. Generating the standings output CSV.
4. Inspecting the generated output.
5. Testing invalid CLI arguments and missing input files.
