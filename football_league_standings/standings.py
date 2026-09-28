from datetime import date
from fractions import Fraction
from typing import Iterable

from football_league_standings.models import (
    MatchResult,
    RankedStanding,
    TeamStanding,
)

start_date = date(1974, 8, 17)


def calculate_week(match_date: date) -> int:
    week = ((match_date - start_date).days // 7) + 1
    return week


def calculate_standings(
    matches: Iterable[MatchResult],
    through_week: int,
) -> list[TeamStanding]:
    standings = {}

    for match in matches:
        if match.home_team not in standings:
            standings[match.home_team] = TeamStanding(
                team=match.home_team
            )

        if match.away_team not in standings:
            standings[match.away_team] = TeamStanding(
                team=match.away_team
            )

        if match.week > through_week:
            continue

        home = standings[match.home_team]
        away = standings[match.away_team]

        home.played += 1
        away.played += 1

        home.goals_for += match.home_goals
        home.goals_against += match.away_goals

        away.goals_for += match.away_goals
        away.goals_against += match.home_goals

        if match.home_goals > match.away_goals:
            home.won += 1
            away.lost += 1
            home.points += 2

        elif match.home_goals == match.away_goals:
            home.drawn += 1
            away.drawn += 1
            home.points += 1
            away.points += 1

        else:
            away.won += 1
            home.lost += 1
            away.points += 2

    return list(standings.values())


def _goal_average_key(standing: TeamStanding) -> tuple[int, Fraction]:
    """Return an exact sortable key for the established goal-average policy.

    Positive goals with none conceded rank above finite averages. A 0/0
    record retains the existing zero-average convention.
    """
    if standing.goals_against == 0:
        if standing.goals_for > 0:
            return 0, Fraction(0)

        return 1, Fraction(0)

    return 1, Fraction(standing.goals_for, standing.goals_against)


def rank_standings(
    standings: Iterable[TeamStanding],
) -> list[RankedStanding]:
    standings_list = list(standings)

    standings_list.sort(
        key=lambda standing: (
            -standing.points,
            _goal_average_key(standing)[0],
            -_goal_average_key(standing)[1],
            standing.team,
        )
    )

    ranked = []
    previous_key = None
    current_position = 0

    for index, standing in enumerate(standings_list, start=1):
        ranking_key = (
            standing.points,
            _goal_average_key(standing),
        )

        if ranking_key != previous_key:
            current_position = index
            previous_key = ranking_key

        ranked.append(
            RankedStanding(
                position=current_position,
                standing=standing,
            )
        )

    return ranked