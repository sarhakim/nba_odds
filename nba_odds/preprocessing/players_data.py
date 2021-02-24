"""Clean and process players data."""
import pandas as pd


class PlayersData:
    """ Clean and process players data"""
    def __init__(self, games_per_team, basket_ref_box_score):
        self.games_per_team = games_per_team
        self.players_data = basket_ref_box_score

    def build_data_with_team(self):
        """
        Determine the team of each player for each season and add to provided players data.
        :return: player data with team
        """
        players = self.players_data[['game_id', 'player_id']].copy()
        games_with_team = self.games_per_team[['game_id', 'id', 'season']].copy()
        players_games_with_teams = self._get_players_games_with_season_team(
            games_with_team=games_with_team, players=players
        )
        players_data_with_team = pd.merge(
            self.players_data,
            players_games_with_teams,
            on=['game_id', 'player_id'],
            how='left'
        )  # Todo: find an easier way to get this dataframe

        players_data_with_team = self._process_mp_float(players_data_with_team)
        return players_data_with_team

    @staticmethod
    def _get_players_games_with_season_team(games_with_team, players):
        # one line per game per team per player
        players_games_with_both_teams = pd.merge(players, games_with_team, on='game_id', how='inner')

        players_with_teams = (players_games_with_both_teams.groupby(['player_id', 'season'])
                              .agg(lambda x: (x.value_counts().index[0]))[['id']]
                              .reset_index())  # for each player keep the team that appears most

        players_games_with_season = (players_games_with_both_teams[['game_id', 'player_id', 'season']]
                                     .drop_duplicates())  # one line per game per player with season

        players_games_with_teams = pd.merge(players_games_with_season, players_with_teams,
                                            how='left', on=['player_id', 'season'])
        return players_games_with_teams

    @staticmethod
    def _process_mp_float(df):
        df['mp'] = df['mp'].apply(lambda x: x.replace(',', '.')).astype(float)
        return df




