""" Module to build features. """
import pandas as pd
from nba_odds.config.config import Paths
from nba_odds.features.elo_rating import EloRating
from nba_odds.features.player_efficiency_rating import PER
from nba_odds.preprocessing.labels import Labels
from nba_odds.preprocessing.games_per_team import GamesPerTeam
from nba_odds.features.previous_season import PreviousSeason
from nba_odds.preprocessing.players_data import PlayersData


def main():
    """ Build features dataset from raws datasets.
    :return: dataset with features by team and season with labels (1 if the team won the nba season.).
    """
    # raw data
    basket_ref_games = pd.read_parquet(Paths.path_basket_ref_games)
    basket_ref_box_score = pd.read_parquet(Paths.path_basket_ref_box_score)

    # preprocessed data
    games_per_team = GamesPerTeam(basket_ref_games=basket_ref_games).build_dataset()
    players_data = PlayersData(basket_ref_box_score=basket_ref_box_score,
                               games_per_team=games_per_team).build_data_with_team()

    winner_by_season = Labels(basket_ref_games=basket_ref_games).compute_winner_by_season()

    elo_rating = EloRating(basket_ref_games=basket_ref_games)
    all_games_elo = elo_rating.compute()

    # preseason features
    previous_season_features = PreviousSeason(games_per_team=games_per_team).compute_features()
    preseason_elo = elo_rating.get_preseason_elo(teams_elo_df=all_games_elo)
    per = PER(players_data=players_data).compute_simplified_per()

    # final dataset preseason
    with_labels = _set_labels(previous_season_features, winner_by_season)
    with_elo = pd.merge(with_labels, preseason_elo, on=['id', 'season'], how='left')
    with_per = pd.merge(with_elo, per, on=['id', 'season'], how='left')
    return with_per


def _set_labels(previous_season_features, winner_by_season):
    with_label = pd.merge(previous_season_features, winner_by_season, on='season', how='left')
    with_label['won'] = with_label['won'] == with_label['id']
    return with_label
