""" Calculate a simplified PER rating per season."""
from nba_odds.config.params import PerParams

import pandas as pd


class PER:
    """Compute per per team.

    :attributes players_stats dataframe from odds.preprocessing.players_stats
    :attributes players_teams dataframe from odds.preprocessing.players_stats
    :methods compute_simplified_per
    """

    def __init__(self, players_stats, players_team):
        self.players_stats = players_stats
        self.players_team = players_team

    def previous_season_per(self):
        """Use previous season player performances and team compositions to get PER by team for next season.

        :return: dataframe aggregated PER on a each team by season.
        """
        player_season_per = self.compute_per_by_player_on_season()

        player_season_per['season'] += 1
        player_season_per = player_season_per.query('season < 2019')

        player_by_team = pd.merge(player_season_per, self.players_team, on=['player_id', 'season'], how='left')

        agg_per_team = self._aggregate_by_season_team(per_with_features=player_by_team)
        return agg_per_team

    def preplayoff_season_per(self):
        """Use preplayoff season player performances and team compositions to get PER by team for the playoff.
        :return: dataframe aggregated PER on a each team by season.
        """
        player_season_per = self.compute_per_by_player_on_season()
        player_by_team = pd.merge(player_season_per, self.players_team, on=['player_id', 'season'], how='left')
        agg_per_team = self._aggregate_by_season_team(per_with_features=player_by_team)
        return agg_per_team

    def compute_per_by_player_on_season(self):
        """Calculate a simplified per over players games and aggregate it by season.

        :return: dataframe with mean, max per per team and number of nba top players in the team.
        """
        players_data = self.players_stats

        players_data['PER'] = players_data.apply(lambda x: self._calculate_simplified_per(x), axis=1)

        mean_per_by_player = self._aggregate_by_player_on_season(players_data)
        filtered_per_by_player = self._keep_only_relevant_players(mean_per_by_player)
        per_with_features = self._is_good_player_feature(filtered_per_by_player)
        return per_with_features

    @staticmethod
    def _calculate_simplified_per(x):
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
        mean_per = (
            players_data[['player_id', 'season', 'PER', 'game_id', 'mp']].dropna()
                .groupby(['player_id', 'season'])
                .agg({'PER': ['mean', 'max'], 'mp': ['sum'], 'game_id': ['count']})
        )
        mean_per.columns = ['_'.join(col) for col in mean_per.columns]
        mean_per = mean_per.reset_index()
        return mean_per

    @staticmethod
    def _keep_only_relevant_players(mean_per):
        return mean_per.query(f'(game_id_count > {PerParams.min_games_played}) and (mp_sum > {PerParams.min_sum_mp})')

    @staticmethod
    def _is_good_player_feature(per_by_player):
        threshold = PerParams.good_player_per_threshold
        per_by_player.loc[:, 'is_good_player'] = (
                per_by_player['PER_mean'] > per_by_player['PER_mean'].quantile(q=threshold)
        )
        return per_by_player

    @staticmethod
    def _aggregate_by_season_team(per_with_features):
        season_per = per_with_features.groupby(['season', 'id']).agg(
            {
                'PER_mean': ['max', 'mean', 'sum'],
                'is_good_player': ['sum']
            }
        )
        season_per.columns = ['_'.join(col) for col in season_per.columns]
        return season_per.reset_index()
