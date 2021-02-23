import pandas as pd

from nba_odds.config.config import GamesRawSchema, ProcessedSchema


class PreviousSeasonFeatures:
    """
    TODO
    """

    def __init__(self, basket_ref_games):
        self.basket_ref_games = basket_ref_games

    def build_dataset(self):
        """
        TODO
        :return:
        """
        basket_ref_games = self.basket_ref_games

        basket_ref_games['away_points_before_ot'] = self._compute_away_points(basket_ref_games)
        basket_ref_games['home_points_before_ot'] = self._compute_home_points(basket_ref_games)
        games_with_floats = self._process_floats(basket_ref_games=basket_ref_games)

        games_per_team = self._build_games_per_team(games_with_floats)

        games_per_team['goal_diff'] = games_per_team['points_before_ot'] - games_per_team['opp_points_before_ot']
        agg_dataset = self._aggregate_dataset(games_per_team)
        agg_dataset['season'] = agg_dataset['season'] + 1
        return agg_dataset

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
        """
        Transform the dataframe with one line per game into a dataframe with one line per game per team.

        :param basket_ref_games: raw pandas dataframe
        :return: pandas dataframe with one line per team per game
        """

        team_features = ['ftscore', 'efg', 'tov', 'orb', 'ftfga', 'ortg', 'points_before_ot']
        opponent_features = ['opp_tov', 'opp_orb', 'opp_ftfga', 'opp_ortg', 'opp_points_before_ot',
                             'opp_efg', 'opp_id']
        other_columns = [GamesRawSchema.game_id, GamesRawSchema.season, ProcessedSchema.team_id,
                         GamesRawSchema.date_col, ProcessedSchema.won]
        columns_to_keep = other_columns + team_features + opponent_features

        games_home = basket_ref_games.copy()
        games_home.columns = [x.replace('away', 'opp').replace('home_', '') for x in games_home.columns]
        games_home = games_home.rename(columns={'ylabel': 'won'})
        games_home = games_home[columns_to_keep]

        games_away = basket_ref_games.copy()
        games_away.columns = [x.replace('home', 'opp').replace('away_', '') for x in games_away.columns]
        games_away[ProcessedSchema.won] = (games_away[GamesRawSchema.ylabel] == 0).astype(int)
        games_away = games_away[columns_to_keep]

        all_games_teams = pd.concat([games_home, games_away], axis=0)
        return all_games_teams

    @staticmethod
    def _aggregate_dataset(games_per_team):
        dataset = games_per_team.groupby([ProcessedSchema.team_id, GamesRawSchema.season]).agg({
            'points_before_ot': ['sum', 'mean'], 'opp_points_before_ot': 'sum', 'won': 'sum', 'goal_diff': ['mean'],
            'efg': 'mean', 'opp_efg': 'mean', 'tov': 'mean', 'opp_tov': 'mean',
            'orb': 'sum', 'opp_orb': 'sum', 'ortg': 'mean', 'opp_ortg': 'mean'
        })
        dataset.columns = ['_'.join(col) for col in dataset.columns]
        return dataset.reset_index()
