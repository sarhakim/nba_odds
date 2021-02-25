""" Class to split on playoffs and keep only regular season data."""
import pandas as pd


class SplitPlayoff:
    """Class to keep only regular season data.

    :method: keep_only_regular_season
    """

    def __init__(self, games_per_team):
        self.games_per_team = games_per_team

    def keep_only_regular_season(self):
        """Keep only regular season data, extracted from games_per_team dataset.

        :return: games_regular_season dataframe
        """
        games_regular_season = self.games_per_team[self.games_per_team['datetime'].isin(self.regular_season_dates)]
        return games_regular_season

    @property
    def regular_season_dates(self):
        nb_games_per_team_regular = 82
        nb_teams_before_2004 = 29
        nb_teams_after_2004 = 30
        regular_season_dates_before_2004 = (
            self.games_per_team.query('season < 2004').groupby('season')['datetime'].nsmallest(
                nb_teams_before_2004 * nb_games_per_team_regular)
        )
        regular_season_dates_after_2004 = (
            self.games_per_team.query('season >= 2004').groupby('season')['datetime'].nsmallest(
                nb_teams_after_2004 * nb_games_per_team_regular)
        )
        regular_season_dates = pd.concat([regular_season_dates_before_2004, regular_season_dates_after_2004], axis=0)
        return regular_season_dates

    @property
    def playoff_dates(self):
        games_playoff = self.games_per_team[self.games_per_team['datetime'] not in self.regular_season_dates]
        return games_playoff.datetime
