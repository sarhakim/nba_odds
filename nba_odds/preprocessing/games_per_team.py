""" Class to preprocess basket games raw data."""
import pandas as pd

from nba_odds.config.config import GamesRawSchema, ProcessedSchema


class GamesPerTeam:
    """Clean data (floats and dates) and create a dataset with one row per team per game.

    :attribute basket_ref_games: raw pandas dataframe with one line per game.
    :method build_dataset
    """

    def __init__(self, basket_ref_games):
        self.basket_ref_games = basket_ref_games

    def build_dataset(self):
        """Clean and transform the dataframe with one line per game into a dataframe with one line per game per team.

        :return: pandas dataframe with one line per team per game
        """
        basket_ref_games = self.basket_ref_games

        basket_ref_games = self._process_date(basket_ref_games)

        basket_ref_games['away_points_before_ot'] = self._compute_away_points(basket_ref_games)
        basket_ref_games['home_points_before_ot'] = self._compute_home_points(basket_ref_games)

        games_with_floats = self._process_floats(basket_ref_games=basket_ref_games)

        games_per_team = self._build_games_per_team(games_with_floats)
        return games_per_team

    @staticmethod
    def _process_date(basket_ref_games):
        basket_ref_games[GamesRawSchema.date_col] = pd.to_datetime(basket_ref_games[GamesRawSchema.date_col])
        return basket_ref_games

    @staticmethod
    def _compute_home_points(basket_ref_games):
        return (
                basket_ref_games[GamesRawSchema.home1] + basket_ref_games[GamesRawSchema.home2]
                + basket_ref_games[GamesRawSchema.home3] + basket_ref_games[GamesRawSchema.home4]
        )

    @staticmethod
    def _compute_away_points(basket_ref_games):
        return (
                basket_ref_games[GamesRawSchema.away1] + basket_ref_games[GamesRawSchema.away2]
                + basket_ref_games[GamesRawSchema.away3] + basket_ref_games[GamesRawSchema.away4]
        )

    @staticmethod
    def _process_floats(basket_ref_games):
        float_features = [
            'away_pace', 'away_efg', 'away_tov', 'away_orb',
            'away_ftfga', 'away_ortg', 'home_pace', 'home_efg', 'home_tov',
            'home_orb', 'home_ftfga', 'home_ortg']

        for feature in float_features:
            basket_ref_games[feature] = basket_ref_games[feature].apply(lambda x: x.replace(',', '.')).astype(float)
        return basket_ref_games

    @staticmethod
    def _build_games_per_team(basket_ref_games):
        team_features = ['ftscore', 'efg', 'tov', 'orb', 'ftfga', 'ortg', 'points_before_ot']
        opponent_features = ['opp_tov', 'opp_orb', 'opp_ftfga', 'opp_ortg', 'opp_points_before_ot',
                             'opp_efg', 'opp_id']
        other_columns = [GamesRawSchema.game_id, GamesRawSchema.season, ProcessedSchema.team_id,
                         GamesRawSchema.date_col, ProcessedSchema.won]
        columns_to_keep = other_columns + team_features + opponent_features

        # Transform home column names and won label.
        games_home = basket_ref_games.copy()
        games_home.columns = [x.replace('away', 'opp').replace('home_', '') for x in games_home.columns]
        games_home = games_home.rename(columns={'ylabel': 'won'})
        games_home = games_home[columns_to_keep]

        # Transform away data.
        games_away = basket_ref_games.copy()
        games_away.columns = [x.replace('home', 'opp').replace('away_', '') for x in games_away.columns]
        games_away[ProcessedSchema.won] = (games_away[GamesRawSchema.ylabel] == 0).astype(int)
        games_away = games_away[columns_to_keep]

        all_games_teams = pd.concat([games_home, games_away], axis=0)
        return all_games_teams
