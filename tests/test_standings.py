import unittest

from datetime import date

from football_league_standings.models import MatchResult, TeamStanding
from football_league_standings.standings import (
    calculate_standings,
    calculate_week,
    rank_standings,
)


class TestStandings(unittest.TestCase):

    def test_opening_day_is_week_one(self):
        match_date = date(1974, 8, 17)

        result = calculate_week(match_date)

        self.assertEqual(result, 1)

    def test_19_october_is_week_ten(self):
        match_date = date(1974, 10, 19)

        result = calculate_week(match_date)

        self.assertEqual(result, 10)

    def test_26_october_is_week_11(self):
        match_date = date(1974, 10, 26)

        result = calculate_week(match_date)

        self.assertEqual(result, 11)

    def standings_by_team(self, matches, through_week):
        standings = calculate_standings(matches, through_week)

        return {standing.team: standing for standing in standings}

    def assert_standing_fields(self, standing, **expected):
        for field, value in expected.items():
            with self.subTest(team=standing.team, field=field):
                self.assertEqual(getattr(standing, field), value)

    def make_standing(self, team, points, goals_for, goals_against):
        return TeamStanding(
            team=team,
            points=points,
            goals_for=goals_for,
            goals_against=goals_against,
        )

    def test_home_win_updates_both_teams(self):
        matches = [
            MatchResult(
                1,
                date(1974, 8, 17),
                "Arsenal",
                "Leeds United",
                3,
                1,
            )
        ]

        result = self.standings_by_team(matches, through_week=1)

        self.assert_standing_fields(
            result["Arsenal"],
            played=1,
            won=1,
            drawn=0,
            lost=0,
            goals_for=3,
            goals_against=1,
            points=2,
        )

        self.assert_standing_fields(
            result["Leeds United"],
            played=1,
            won=0,
            drawn=0,
            lost=1,
            goals_for=1,
            goals_against=3,
            points=0,
        )

    def test_draw_gives_each_team_one_point(self):
        matches = [
            MatchResult(
                1,
                date(1974, 8, 17),
                "Everton",
                "Chelsea",
                2,
                2,
            )
        ]

        result = self.standings_by_team(matches, through_week=1)

        for team in ("Everton", "Chelsea"):
            with self.subTest(team=team):
                self.assert_standing_fields(
                    result[team],
                    played=1,
                    won=0,
                    drawn=1,
                    lost=0,
                    goals_for=2,
                    goals_against=2,
                    points=1,
                )

    def test_away_win_awards_points_to_away_team(self):
        matches = [
            MatchResult(
                1,
                date(1974, 8, 17),
                "Burnley",
                "Ipswich Town",
                0,
                2,
            )
        ]

        result = self.standings_by_team(matches, through_week=1)

        self.assert_standing_fields(
            result["Burnley"],
            played=1,
            won=0,
            drawn=0,
            lost=1,
            goals_for=0,
            goals_against=2,
            points=0,
        )

        self.assert_standing_fields(
            result["Ipswich Town"],
            played=1,
            won=1,
            drawn=0,
            lost=0,
            goals_for=2,
            goals_against=0,
            points=2,
        )

    def test_matches_after_cutoff_do_not_contribute(self):
        matches = [
            MatchResult(
                9,
                date(1974, 10, 12),
                "North",
                "South",
                2,
                0,
            ),
            MatchResult(
                10,
                date(1974, 10, 19),
                "East",
                "North",
                1,
                1,
            ),
            MatchResult(
                10,
                date(1974, 10, 19),
                "South",
                "West",
                1,
                0,
            ),
            MatchResult(
                11,
                date(1974, 10, 26),
                "North",
                "West",
                0,
                3,
            ),
        ]

        result = self.standings_by_team(matches, through_week=10)

        self.assert_standing_fields(
            result["North"],
            played=2,
            won=1,
            drawn=1,
            lost=0,
            goals_for=3,
            goals_against=1,
            points=3,
        )

        self.assert_standing_fields(
            result["West"],
            played=1,
            won=0,
            drawn=0,
            lost=1,
            goals_for=0,
            goals_against=1,
            points=0,
        )

    def test_more_points_rank_above_higher_goal_average(self):
        points_leader = self.make_standing(
            "Points Leader",
            11,
            5,
            5,
        )

        ratio_leader = self.make_standing(
            "Ratio Leader",
            10,
            8,
            2,
        )

        ranked = rank_standings(
            [ratio_leader, points_leader]
        )

        self.assertEqual(
            [
                (item.position, item.standing.team)
                for item in ranked
            ],
            [
                (1, "Points Leader"),
                (2, "Ratio Leader"),
            ],
        )

    def test_goal_average_breaks_points_tie_not_goal_difference(self):
        ratio_winner = self.make_standing(
            "Ratio Winner",
            10,
            3,
            2,
        )

        goal_difference_winner = self.make_standing(
            "Goal Difference Winner",
            10,
            8,
            6,
        )

        ranked = rank_standings(
            [goal_difference_winner, ratio_winner]
        )

        self.assertEqual(
            [
                (item.position, item.standing.team)
                for item in ranked
            ],
            [
                (1, "Ratio Winner"),
                (2, "Goal Difference Winner"),
            ],
        )

    def test_tied_teams_share_competition_position(self):
        alpha = self.make_standing(
            "Alpha",
            10,
            4,
            2,
        )

        beta = self.make_standing(
            "Beta",
            10,
            2,
            1,
        )

        gamma = self.make_standing(
            "Gamma",
            10,
            3,
            2,
        )

        ranked = rank_standings(
            [gamma, beta, alpha]
        )

        self.assertEqual(
            [
                (item.position, item.standing.team)
                for item in ranked
            ],
            [
                (1, "Alpha"),
                (1, "Beta"),
                (3, "Gamma"),
            ],
        )

    def test_exact_tie_display_order_is_alphabetical(self):
        zulu = self.make_standing(
            "Zulu",
            10,
            2,
            1,
        )

        alpha = self.make_standing(
            "Alpha",
            10,
            4,
            2,
        )

        ranked = rank_standings(
            [zulu, alpha]
        )

        self.assertEqual(
            [
                (item.position, item.standing.team)
                for item in ranked
            ],
            [
                (1, "Alpha"),
                (1, "Zulu"),
            ],
        )

    def test_goal_average_comparison_is_exact(self):
        ratio_just_below_one = self.make_standing(
            "Alpha",
            10,
            10**30,
            10**30 + 1,
        )
        ratio_equal_to_one = self.make_standing(
            "Zulu",
            10,
            1,
            1,
        )

        ranked = rank_standings(
            [ratio_just_below_one, ratio_equal_to_one]
        )

        self.assertEqual(
            [
                (item.position, item.standing.team)
                for item in ranked
            ],
            [
                (1, "Zulu"),
                (2, "Alpha"),
            ],
        )

    def test_zero_goals_against_keeps_existing_average_convention(self):
        positive_goals_and_none_conceded = self.make_standing(
            "Perfect",
            5,
            1,
            0,
        )
        zero_for_and_zero_against = self.make_standing(
            "No Matches",
            5,
            0,
            0,
        )
        zero_for_and_positive_against = self.make_standing(
            "Scoreless",
            5,
            0,
            1,
        )

        ranked = rank_standings(
            [
                zero_for_and_zero_against,
                zero_for_and_positive_against,
                positive_goals_and_none_conceded,
            ]
        )

        self.assertEqual(
            [
                (item.position, item.standing.team)
                for item in ranked
            ],
            [
                (1, "Perfect"),
                (2, "No Matches"),
                (2, "Scoreless"),
            ],
        )


if __name__ == "__main__":
    unittest.main()