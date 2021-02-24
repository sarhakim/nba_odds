import pandas as pd
from nba_odds.config.config import Paths
from nba_odds.features.elo_rating import EloRating
from nba_odds.preprocessing.labels import Labels
from nba_odds.preprocessing.games_per_team import GamesPerTeam
from nba_odds.features.previous_season import PreviousSeason


def main():
    basket_ref_games = pd.read_parquet(Paths.path_basket_ref_games)

    games_per_team = GamesPerTeam(basket_ref_games=basket_ref_games).build_dataset()

    elo_rating = EloRating(basket_ref_games=basket_ref_games)
    all_games_elo = elo_rating.compute()

    winner_by_season = Labels(basket_ref_games=basket_ref_games).compute_winner_by_season()
    previous_season_features = PreviousSeason(games_per_team=games_per_team).compute_features()
    preseason_elo = elo_rating.get_preseason_elo(teams_elo_df=all_games_elo)

    with_labels = _set_labels(previous_season_features, winner_by_season)
    with_elo = pd.merge(with_labels, preseason_elo, on=['id', 'season'], how='left')
    return with_elo


def _set_labels(previous_season_features, winner_by_season):
    with_label = pd.merge(previous_season_features, winner_by_season, on='season', how='left')
    with_label['won'] = with_label['won'] == with_label['id']
    return with_label
