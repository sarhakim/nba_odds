import pandas as pd
from imblearn.over_sampling import ADASYN
from imblearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from nba_odds.config.config import Paths
from nba_odds.model.model_builder import ModelBuilder


def main():
    """ Build the model and predict odds."""
    columns_to_keep = ['elo', 'goal_diff_mean', 'PER_mean_sum', 'won_sum', 'points_before_ot_sum', 'PER_mean_mean',
                       'opp_ortg_mean', 'points_before_ot_mean', 'opp_points_before_ot_sum', 'orb_sum'] + ['id', 'won',
                                                                                                           'season']

    preseason_data = pd.read_csv(Paths.output_preseason_features).dropna()
    preseason_model(preseason_data[columns_to_keep])

    playoff_data = pd.read_csv(Paths.output_preplayoff_features).dropna()
    preplayoff_model(playoff_data) # keep all features for playoff predictions


def preplayoff_model(playoff_data):
    model = RandomForestClassifier()
    model_builder = ModelBuilder(dataset=playoff_data, model=model, scale=True, model_name='playoff_lr')
    predictions_df = model_builder.build()

    # Random forrest predicts 0 as a probability. We fill missing odds with a multiple of the maximum odd.
    predictions_df.loc[:, 'odds'] = predictions_df['odds'].fillna(2*max(predictions_df['odds']))

    predictions_df.to_csv(Paths.output_playoff_odds_path, index=False)


def preseason_model(preseason_data):
    model = LogisticRegression()
    adasyn = ADASYN()
    pipeline = Pipeline([('sampling', adasyn), ('class', model)])
    model_builder = ModelBuilder(dataset=preseason_data, model=pipeline, scale=True, model_name='preseason_lr')
    predictions_df = model_builder.build()
    predictions_df.to_csv(Paths.output_preseason_odds_path, index=False)


if __name__ == '__main__':
    main()
