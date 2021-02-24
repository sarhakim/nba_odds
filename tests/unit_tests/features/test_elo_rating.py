""" Class to test Elo rating."""
import math
from unittest import TestCase
import pandas as pd

from nba_odds.features.elo_rating import EloRating


class TestEloRating(TestCase):
    def test__calculate_elo_ratings(self):
        # Given
        games_stat = pd.DataFrame(
            {'datetime': ['2020-01-01', '2021-04-01'],
             'game_id': ['123', '456'],
             'season': ['2020', '2021'],
             'home_id': [5, 7],
             'away_id': [7, 5],
             'home_points': [20, 100],
             'away_points': [100, 10],
             'ylabel': [0, 1]}
        )

        # When
        actual_elo_ratings = (EloRating(basket_ref_games=None)
                              ._calculate_elo_ratings(games_with_total_pts=games_stat))

        # Then
        # expected new elo ratings
        h = math.pow(10, 1500 / 400)
        r = math.pow(10, 1500 / 400)
        a = math.pow(10, 100 / 400)
        denom = r + a * h
        home_prob = a * h / denom
        away_prob = r / denom

        mov = -80  # goal diff on first game
        elo_diff = 0
        k = 20*(-mov + 3) ** 0.8 / (7.5 + 0.006 * (-elo_diff))
        updated_home_elo = 1500 + k * (0 - home_prob)
        updated_away_elo = 1500 + k * (1 - away_prob)

        home_updated_after_season = (0.75 * updated_home_elo) + (0.25 * 1505)
        away_updated_after_season = (0.75 * updated_away_elo) + (0.25 * 1505)

        expected_elo_rating = pd.DataFrame(
            {'date': ['2020-01-01', '2020-01-01', '2021-04-01', '2021-04-01'],
             'game_id': ['123', '123', '456', '456'],
             'season': ['2020', '2020', '2021', '2021'],
             'id': ['5', '7', '7', '5'],
             'elo': [1500, 1500, away_updated_after_season, home_updated_after_season]
             }
        )
        pd.testing.assert_frame_equal(actual_elo_ratings.sort_index(axis=1),
                                      expected_elo_rating.sort_index(axis=1))
