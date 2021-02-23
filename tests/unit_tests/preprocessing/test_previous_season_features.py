"""Class to test ProcessGames class."""
from unittest import TestCase

import pandas as pd

from nba_odds.preprocessing.previous_season_features import PreviousSeasonFeatures


class TestPreviousSeasonFeatures(TestCase):
    """Class to test ProcessGames class."""

    def test__build_games_per_team(self):
        # Given
        basket_ref_games = pd.DataFrame(
            {'datetime': ['2020-01-01', '2001-04-01'],
             'game_id': ['123', '456'],
             'season': ['2020', '2001'],
             'home_id': [5, 7],
             'home_ftscore': [77, 88],
             'home_efg': [0.397, 0.67],
             'home_tov': [9.2, 10.5],
             'home_orb': [21.3, 10.0],
             'home_ftfga': [0.19, 0.50],
             'home_ortg': [89.1, 90.0],
             'home_points_before_ot': [4, 100],
             'away_id': [6, 1],
             'away_ftscore': [99, 108],
             'away_efg': [0.697, 0.567],
             'away_tov': [12.2, 13.0],
             'away_orb': [27.3, 56.0],
             'away_ftfga': [0.12, 0.3],
             'away_ortg': [109.1, 70.0],
             'away_points_before_ot': [4, 70],
             'ylabel': [1, 0]}
        )

        # When 
        actual = (PreviousSeasonFeatures(basket_ref_games=None)
                  ._build_games_per_team(basket_ref_games=basket_ref_games)
                  .reset_index(drop=True))

        # Then
        expected = pd.DataFrame(
            {'datetime': ['2020-01-01', '2001-04-01', '2020-01-01', '2001-04-01'],
             'season': ['2020', '2001', '2020', '2001'],
             'game_id': ['123', '456', '123', '456'],
             'id': [5, 7, 6, 1],
             'ftscore': [77, 88, 99, 108],
             'efg': [0.397, 0.67, 0.697, 0.567],
             'tov': [9.2, 10.5, 12.2, 13.0],
             'orb': [21.3, 10.0, 27.3, 56.0],
             'ftfga': [0.19, 0.50, 0.12, 0.3],
             'ortg': [89.1, 90.0, 109.1, 70.0],
             'points_before_ot': [4, 100, 4, 70],
             'opp_id': [6, 1, 5, 7],
             'opp_efg': [0.697, 0.567, 0.397, 0.67],
             'opp_tov': [12.2, 13.0, 9.2, 10.5],
             'opp_orb': [27.3, 56.0, 21.3, 10.0],
             'opp_ftfga': [0.12, 0.3, 0.19, 0.50],
             'opp_ortg': [109.1, 70.0, 89.1, 90.0],
             'opp_points_before_ot': [4, 70, 4, 100],
             'won': [1, 0, 0, 1]}
        )
        pd.testing.assert_frame_equal(actual.sort_index(axis=1), expected.sort_index(axis=1))
