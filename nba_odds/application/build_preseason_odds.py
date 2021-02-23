import pandas as pd
from nba_odds.config.config import Paths

def main():
    basket_ref_games = pd.read_parquet(Paths.path_basket_ref_games)
