""" Calculate a simplified PER rating per season per team."""
from nba_odds.config.params import PerParams

class PER:
    def __init__(self, players_data):
        self.players_data = players_data

    def compute_simplified_per(self):
        players_data = self.players_data

        players_data['PER'] = players_data.apply(lambda x: self._calculate_per(x), axis=1)

        mean_per_by_player = self._aggregate_by_player_on_season(players_data)
        filtered_per_by_player = self._keep_only_relevant_players(mean_per_by_player)
        per_with_features = self._is_good_player_feature(filtered_per_by_player)

        team_per = self._aggregate_by_season_team(per_with_features)
        return team_per

    @staticmethod
    def _calculate_per(x):
        if x['mp'] > PerParams.min_mp:
            per = (85.910 * x['fg'] + 53.897 * x['stl'] + 51.757 * x['_3p'] + 46.864 * x['ft'] +
                   39.190 * x['blk'] + 39.190 * x['orb'] + 34.677 * x['ast'] + 14.707 * x['drb']
                   - x['pf'] * 17.174
                   - (x['fta'] - x['ft']) * 20.091
                   - (x['fga'] - x['fg']) * 39.190
                   - x['tov'] * 53.897) * (1 / x['mp'])
            return per

    @staticmethod
    def _aggregate_by_player_on_season(players_data):
        mean_per = (players_data[['player_id', 'season', 'PER', 'game_id', 'mp', 'id']].dropna().groupby(
            ['player_id', 'season', 'id'])
            .agg({'PER': ['mean', 'median', 'max', 'min'], 'mp': ['sum'], 'game_id': ['count']}))
        mean_per.columns = ['_'.join(col) for col in mean_per.columns]
        mean_per = mean_per.reset_index()
        return mean_per

    @staticmethod
    def _keep_only_relevant_players(mean_per):
        return mean_per.query(f'(game_id_count > {PerParams.min_games_played}) and (mp_sum > {PerParams.min_sum_mp})')

    @staticmethod
    def _is_good_player_feature(per_by_player):
        threshold = PerParams.good_player_per_threshold
        per_by_player.loc['is_good_player'] = (
                per_by_player['PER_mean'] > per_by_player['PER_mean'].quantile(q=threshold)
        )
        return per_by_player

    @staticmethod
    def _aggregate_by_season_team(per_with_features):
        teams_per = per_with_features.groupby(['id', 'season']).agg(
            {
                'PER_mean': ['max', 'mean'],
                'is_good_player': ['sum']
            }
        )
        teams_per.columns = ['_'.join(col) for col in teams_per.columns]
        teams_per = teams_per.reset_index()
        return teams_per
