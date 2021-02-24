"""
Class to compute Elo rating feature.
https://towardsdatascience.com/predicting-the-outcome-of-nba-games-with-machine-learning-a810bb768f20
"""
import math

import pandas as pd

from nba_odds.config.config import GamesRawSchema


class EloRating:
    """Class to compute elo rating feature.

    :attributes basket_ref_games: raw pandas dataframe with one line per game.
    :methods compute
    """
    def __init__(self, basket_ref_games):
        self.basket_ref_games = basket_ref_games

    home_pts_col = 'home_points'
    away_pts_col = 'away_points'

    HOME_COURT_ADVANTAGE = 100

    def compute(self):
        """
        Calculates Elo rating by iterating over basket ref games dataframe

        :return: elo_rating dataframe
        """
        basket_ref_games = self.basket_ref_games

        # already done in games_per_team - todo
        basket_ref_games[GamesRawSchema.date_col] = pd.to_datetime(basket_ref_games[GamesRawSchema.date_col])

        games_with_total_pts = self._get_total_points(basket_ref_games)

        team_stats_cols = ['game_id', 'home_id', 'away_id', 'season', 'datetime',
                           self.home_pts_col, self.away_pts_col, GamesRawSchema.ylabel]
        teams_elo_df = self._calculate_elo_ratings(games_with_total_pts[team_stats_cols])
        return teams_elo_df

    def _calculate_elo_ratings(self, games_with_total_pts):

        team_stats = (games_with_total_pts
                      .sort_values(by=GamesRawSchema.date_col).reset_index(drop=True))
        elo_df = pd.DataFrame(
            columns=['game_id', 'home_id', 'away_id', 'h_team_elo_before', 'a_team_elo_before', 'h_team_elo_after',
                     'a_team_elo_after']
        )
        teams_elo_df = pd.DataFrame(columns=['game_id', 'id', 'elo', 'date', 'season'])
        for index, row in (team_stats.iterrows()):
            game_id = row['game_id']
            game_date = row['datetime']
            season = row['season']
            h_team, a_team = row['home_id'], row['away_id']
            h_score, a_score = row['home_points'], row['away_points']
            ylabel = row['ylabel']

            if h_team not in elo_df['home_id'].values and h_team not in elo_df['away_id'].values:
                h_team_elo_before = 1500.0
            else:
                h_team_elo_before = self._get_prev_elo(h_team, game_date, season, team_stats, elo_df)

            if a_team not in elo_df['home_id'].values and a_team not in elo_df['away_id'].values:
                a_team_elo_before = 1500.0
            else:
                a_team_elo_before = self._get_prev_elo(a_team, game_date, season, team_stats, elo_df)

            h_team_elo_after, a_team_elo_after = self._update_elo(
                home_score=h_score, away_score=a_score,
                home_elo=h_team_elo_before, away_elo=a_team_elo_before, ylabel=ylabel
            )

            new_row = {'game_id': game_id, 'home_id': h_team, 'away_id': a_team,
                       'h_team_elo_before': h_team_elo_before, 'a_team_elo_before': a_team_elo_before,
                       'h_team_elo_after': h_team_elo_after, 'a_team_elo_after': a_team_elo_after}

            teams_row_one = {'game_id': game_id, 'id': h_team, 'elo': h_team_elo_before,
                             'date': game_date, 'season': season}
            teams_row_two = {'game_id': game_id, 'id': a_team, 'elo': a_team_elo_before,
                             'date': game_date, 'season': season}

            elo_df = elo_df.append(new_row, ignore_index=True)
            teams_elo_df = teams_elo_df.append(teams_row_one, ignore_index=True)
            teams_elo_df = teams_elo_df.append(teams_row_two, ignore_index=True)
        return teams_elo_df

    @staticmethod
    def get_first_elo_season(teams_elo_df):
        """ Transform elo dataframe to get first elo of the season.
        :param teams_elo_df: dataframe with elo for each game date.
        :return: pandas dataframe with one line per team per season.
        """
        first_elo = (teams_elo_df
                     .sort_values(by=['id', 'date'])
                     .drop_duplicates(['id', 'season'], keep='first'))
        return first_elo[['id', 'elo', 'season']]

    def _get_total_points(self, basket_ref_games):
        home_pts_cols = ['home1', 'home2', 'home3', 'home4', 'home1_ot', 'home2_ot', 'home3_ot', 'home4_ot']
        basket_ref_games[self.home_pts_col] = sum(
            [basket_ref_games[col].fillna(0) for col in home_pts_cols]
        )
        away_pts_cols = ['away1', 'away2', 'away3', 'away4', 'away1_ot', 'away2_ot', 'away3_ot', 'away4_ot']
        basket_ref_games[self.away_pts_col] = sum(
            [basket_ref_games[col].fillna(0) for col in away_pts_cols]
        )
        return basket_ref_games

    # takes into account prev season elo
    @staticmethod
    def _get_prev_elo(team, date, season, team_stats, elo_df):
        prev_game = (team_stats[
            (team_stats['datetime'] < date) &
            ((team_stats['home_id'] == team) | (team_stats['away_id'] == team))
            ].copy().sort_values(by='datetime').tail(1).iloc[0])

        if team == prev_game['home_id']:
            elo_rating = elo_df[elo_df['game_id'] == prev_game['game_id']]['h_team_elo_after'].values[0]
        else:
            elo_rating = elo_df[elo_df['game_id'] == prev_game['game_id']]['a_team_elo_after'].values[0]

        if prev_game['season'] != season:
            return (0.75 * elo_rating) + (0.25 * 1505)
        else:
            return elo_rating

    # updates the home and away teams elo ratings after a game
    def _update_elo(self, home_score, away_score, home_elo, away_elo, ylabel):
        home_prob, away_prob = self._win_probs(home_elo=home_elo, away_elo=away_elo)

        if int(ylabel) == 1:
            home_win = 1
            away_win = 0
        else:
            home_win = 0
            away_win = 1

        k = self._elo_k(mov=home_score - away_score, elo_diff=home_elo - away_elo)

        updated_home_elo = home_elo + k * (home_win - home_prob)
        updated_away_elo = away_elo + k * (away_win - away_prob)

        return updated_home_elo, updated_away_elo

    # Home and road team win probabilities implied by Elo ratings and home court adjustment
    def _win_probs(self, home_elo, away_elo):
        h = math.pow(10, home_elo / 400)
        r = math.pow(10, away_elo / 400)
        a = math.pow(10, self.HOME_COURT_ADVANTAGE / 400)

        denom = r + a * h
        home_prob = a * h / denom
        away_prob = r / denom
        return home_prob, away_prob

    # this function determines the constant used in the elo rating,
    # based on margin of victory and difference in elo ratings
    @staticmethod
    def _elo_k(mov, elo_diff):
        k = 20
        if mov > 0:
            multiplier = (mov + 3) ** 0.8 / (7.5 + 0.006 * elo_diff)
        else:
            multiplier = (-mov + 3) ** 0.8 / (7.5 + 0.006 * (-elo_diff))
        return k * multiplier
