import pandas as pd
from sklearn.linear_model import LogisticRegression

from nba_odds.config.config import Paths
from nba_odds.model.model_builder import ModelBuilder


def main():
    """ Build the model and predict odds."""
    preseason_data = pd.read_csv(Paths.output_preseason_features).dropna()
    model = LogisticRegression()
    model_builder = ModelBuilder(dataset=preseason_data, model=model, scale=True, model_name='preseason_lr')
    predictions_df = model_builder.build()
    predictions_df.to_csv(Paths.output_preseason_odds_path, index=False)

    playoff_data = pd.read_csv(Paths.output_preplayoff_features).dropna()
    model = LogisticRegression()
    model_builder = ModelBuilder(dataset=playoff_data, model=model, scale=True, model_name='playoff_lr')
    predictions_df = model_builder.build()
    predictions_df.to_csv(Paths.output_playoff_odds_path, index=False)


if __name__ == '__main__':
    main()
