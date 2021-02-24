""" Classes with paths, column names and parameters."""
import os

class Paths:
    """Paths to load data."""
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    path_basket_ref_box_score = os.path.join(project_dir, "data/BasketrefBoxscores.parquet")
    path_basket_ref_games = os.path.join(project_dir, "data/BasketrefGames.parquet")

    output_preseason_features = os.path.join(project_dir, 'data/preseason_dataset.csv')
    output_preplayoff_features = os.path.join(project_dir, 'data/preplayoff_dataset.csv')

    model_dir = os.path.join(project_dir, 'model/')


class GamesRawSchema:
    """ Columns used in the games raw data."""
    date_col = 'datetime'
    season = 'season'
    home = 'home_id'
    away = 'away_id'
    game_id = 'game_id'
    ylabel = 'ylabel'

    # Number of points by quarter for away and home team
    home1 = 'home1'
    home2 = 'home2'
    home3 = 'home3'
    home4 = 'home4'
    away1 = 'away1'
    away2 = 'away2'
    away3 = 'away3'
    away4 = 'away4'


class ProcessedSchema:
    """ Final dataset columns."""
    team_id = 'id'
    points_before_ot = 'points_before_ot' # ot means overtime.
    won = 'won'
