""" Class to aggregate season features by team."""

from nba_odds.config.config import GamesRawSchema, ProcessedSchema


class TeamsStats:
    """ Aggregate season features from games_per_team dataset.

    :attributes games_per_team dataframe from nba_odds.preprocessing.games_per_team
    :methods compute_previous_season_features, compute_aggregated_features
    """

    def __init__(self, games_per_team):
        self.games_per_team = games_per_team

    def compute_previous_season_features(self):
        """ Compute features by team."""
        agg_dataset = self.compute_aggregated_features()

        agg_dataset[GamesRawSchema.season] += 1
        previous_season_features = agg_dataset.query(f'{GamesRawSchema.season} < 2019')
        return previous_season_features

    def compute_aggregated_features(self):
        """ Aggregate game features to get feature by team on season."""
        games_per_team = self.games_per_team
        games_per_team['goal_diff'] = games_per_team['points_before_ot'] - games_per_team['opp_points_before_ot']
        agg_dataset = self._aggregate_dataset(games_per_team=games_per_team)
        return agg_dataset

    @staticmethod
    def _aggregate_dataset(games_per_team):
        dataset = games_per_team.groupby([ProcessedSchema.team_id, GamesRawSchema.season]).agg({
            'points_before_ot': ['sum', 'mean'], 'opp_points_before_ot': 'sum', 'won': 'sum', 'goal_diff': ['mean'],
            'efg': 'mean', 'opp_efg': 'mean', 'tov': 'mean', 'opp_tov': 'mean',
            'orb': 'sum', 'opp_orb': 'sum', 'ortg': 'mean', 'opp_ortg': 'mean'
        })
        dataset.columns = ['_'.join(col) for col in dataset.columns]
        return dataset.reset_index()
