""" Module to build features. """
import pandas as pd

from nba_odds.config.config import Paths
from nba_odds.features.elo_rating import EloRating
from nba_odds.features.player_efficiency_rating import PER
from nba_odds.features.teams_stats import TeamsStats
from nba_odds.preprocessing.games_per_team import GamesPerTeam
from nba_odds.preprocessing.labels import Labels
from nba_odds.preprocessing.players_data import PlayersData
from nba_odds.preprocessing.split_on_playoffs import SplitPlayoff


def main():
    """ Build features dataset from raws datasets.
    :return: dataset with features by team and season with labels (1 if the team won the nba season.).
    """
    # raw data
    basket_ref_games = pd.read_parquet(Paths.path_basket_ref_games)
    basket_ref_box_score = pd.read_parquet(Paths.path_basket_ref_box_score)

    # preprocessed data
    games_per_team = GamesPerTeam(basket_ref_games=basket_ref_games).build_dataset()
    players_stats, players_with_team = PlayersData(basket_ref_box_score=basket_ref_box_score,
                                                   games_per_team=games_per_team).build_data()

    # Labels
    winner_by_season = Labels(basket_ref_games=basket_ref_games).compute_winner_by_season()
    elo_rating = EloRating(basket_ref_games=basket_ref_games)
    all_games_elo = elo_rating.compute()

    # previous season features
    preseason_features = _build_preseason_features(all_games_elo, games_per_team, players_stats,
                                                   players_with_team, winner_by_season)

    # regular season features
    playoff_dataset = _build_playoff_features(all_games_elo, basket_ref_box_score, games_per_team, winner_by_season)

    preseason_features.to_csv(Paths.output_preseason_features, index=False)
    playoff_dataset.to_csv(Paths.output_preplayoff_features, index=False)
    return preseason_features, playoff_dataset


def _build_preseason_features(all_games_elo, games_per_team, players_stats, players_with_team, winner_by_season):
    # preseason features
    teams_stats = TeamsStats(games_per_team=games_per_team).compute_previous_season_features()
    preseason_elo = EloRating.get_first_elo_season(teams_elo_df=all_games_elo)
    preseason_per = PER(players_stats=players_stats, players_team=players_with_team).previous_season_per()

    dataset = _merge_all_features(per=preseason_per, elo=preseason_elo, teams_stats=teams_stats,
                                  labels=winner_by_season)
    return dataset


def _build_playoff_features(all_games_elo, basket_ref_box_score, games_per_team, winner_by_season):
    # recreate processed data for playoff
    playoff_splitter = SplitPlayoff(games_per_team=games_per_team)
    games_regular_season = playoff_splitter.keep_only_regular_season()
    preplayoff_player_data, players_with_team = PlayersData(basket_ref_box_score=basket_ref_box_score,
                                                            games_per_team=games_regular_season).build_data()

    # features based on the regular season before playoff
    regular_season_stats = TeamsStats(games_per_team=games_regular_season).compute_aggregated_features()
    preplayoff_per = PER(players_stats=preplayoff_player_data, players_team=players_with_team).preplayoff_season_per()

    # get elo rating before playoff
    playoff_elo = all_games_elo[all_games_elo['date'].isin(playoff_splitter.playoff_dates)]
    preplayoff_elo = EloRating.get_first_elo_season(playoff_elo)

    # final dataset
    playoff_dataset = _merge_all_features(per=preplayoff_per, elo=preplayoff_elo, teams_stats=regular_season_stats,
                                          labels=winner_by_season)
    return playoff_dataset


def _merge_all_features(per, elo, teams_stats, labels):
    # final dataset preseason
    with_labels = _set_labels(teams_stats, labels)
    with_elo = pd.merge(with_labels, elo, on=['id', 'season'], how='left')
    with_per = pd.merge(with_elo, per, on=['id', 'season'], how='left')
    return with_per


def _set_labels(features, winner_by_season):
    with_label = pd.merge(features, winner_by_season, on='season', how='left')
    with_label['won'] = with_label['won'] == with_label['id']
    return with_label


if __name__ == "__main__":
    main()
