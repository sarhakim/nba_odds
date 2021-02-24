import pandas as pd
from nba_odds.config.config import Paths
from nba_odds.preprocessing.labels import Labels
from nba_odds.preprocessing.games_per_team import GamesPerTeam
from nba_odds.features.previous_season import PreviousSeason


def main():
    basket_ref_games = pd.read_parquet(Paths.path_basket_ref_games)

    games_per_team = GamesPerTeam(basket_ref_games=basket_ref_games).build_dataset()

    previous_season_features = PreviousSeason(games_per_team=games_per_team).compute_features()
    winner_by_season = Labels(basket_ref_games=basket_ref_games).compute_winner_by_season()

    with_labels = _set_labels(previous_season_features, winner_by_season)
    return with_labels


def _set_labels(previous_season_features, winner_by_season):
    with_label = pd.merge(previous_season_features, winner_by_season, on='season', how='left')
    with_label['won'] = with_label['won'] == with_label['id']
    return with_label

