""" Class to build, save and evaluate the model."""
import logging
import os
import time

import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler

from nba_odds.config.config import Paths


class ModelBuilder:
    """Class to build the model from a provided dataset."""

    def __init__(self, dataset, model, scale, model_name):
        self.dataset = dataset
        self.scale = scale
        self.model = model
        self.model_name = model_name
        self.mae = None
        self.rmse = None

    def build(self):
        """ Build the model."""

        logging.info(f"Processing input data.")
        season_to_pred = self.dataset.query('season == 2018')
        train = self.dataset.query('season < 2018')

        x_train, y_train = self._extract_features_and_target(train)
        x_test, y_test = self._extract_features_and_target(season_to_pred)

        if self.scale:
            x_train_scaled, x_test_scaled = self._scale_data(x_test, x_train)
        else:
            x_train_scaled, x_test_scaled = x_train, x_test

        logging.info(f"Building model.")
        self.model.fit(X=x_train_scaled, y=y_train)

        predictions = self._model_performances(x_test=x_test_scaled, y_test=y_test)
        self._save_model(processed_df_columns=self.dataset.columns)

        season_to_pred['predictions'] = predictions
        season_to_pred['odds'] = season_to_pred['predictions'].apply(lambda x: 1 / x if x > 0 else None)
        return season_to_pred[['season', 'id', 'predictions', 'odds']]

    @staticmethod
    def _scale_data(x_test, x_train):
        # todo - save the scaler
        scaler = StandardScaler()
        x_train_scaled = scaler.fit_transform(x_train)
        x_test_scaled = scaler.transform(x_test)
        return x_train_scaled, x_test_scaled

    @staticmethod
    def _extract_features_and_target(df):
        x = df.drop(['id', 'season', 'won'], axis=1)
        y = df['won']
        return x, y

    def _model_performances(self, x_test, y_test):
        predictions = self.model.predict_proba(x_test)
        proba = predictions[:, 1]
        self.mae = mean_absolute_error(y_pred=proba, y_true=y_test)
        self.rmse = mean_squared_error(y_pred=proba, y_true=y_test)
        logging.info(f"mae : {self.mae}")
        logging.info(f"rmse : {self.rmse}")
        return proba

    def _save_model(self, processed_df_columns):
        current_ts = round(time.time())
        model_filename = f"{self.model_name}_{current_ts}.pkl"
        model_columns_filename = f"{self.model_name}_columns_{current_ts}.pkl"

        joblib.dump(self.model, os.path.join(Paths.model_dir, model_filename))
        model_columns = list(processed_df_columns)
        joblib.dump(model_columns, os.path.join(Paths.model_dir, model_columns_filename))
        logging.info(f"{model_filename} and {model_columns_filename} have been created.")
