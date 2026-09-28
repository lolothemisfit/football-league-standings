from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MatchResult:
	week: int
	match_date: date
	home_team: str
	away_team: str
	home_goals: int
	away_goals: int


@dataclass
class TeamStanding:
	team: str
	played: int = 0
	won: int = 0
	drawn: int = 0
	lost: int = 0
	goals_for: int = 0
	goals_against: int = 0
	points: int = 0

@dataclass
class RankedStanding:
    position: int
    standing: TeamStanding