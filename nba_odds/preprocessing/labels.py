
import pandas as pd

from nba_odds.config.config import GamesRawSchema, ProcessedSchema


class Labels:
    """
    TODO
    """

    def __init__(self, basket_ref_games):
        self.basket_ref_games = basket_ref_games

    def compute_winner_by_season(self):
        """ Compute winner for each season by looking at who won the last game."""
        basket_ref_games = self._process_date(self.basket_ref_games)
        last_game_by_season = basket_ref_games.loc[basket_ref_games.groupby(GamesRawSchema.season).datetime.idxmax()]

        last_game_by_season[ProcessedSchema.won] = last_game_by_season.apply(lambda row: self._get_winner(row), axis=1)

        winners_by_season = last_game_by_season[[GamesRawSchema.season, ProcessedSchema.won]]
        return winners_by_season

    @staticmethod
    def _process_date(basket_ref_games):
        basket_ref_games[GamesRawSchema.date_col] = pd.to_datetime(basket_ref_games[GamesRawSchema.date_col])
        return basket_ref_games

    @staticmethod
    def _get_winner(row):
        if row[GamesRawSchema.ylabel] == 1:
            return row[GamesRawSchema.home]
        elif row[GamesRawSchema.ylabel] == 0:
            return row[GamesRawSchema.away]