""" Class to build, save and evaluate the model."""
import logging
import os
import time

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from nba_odds.config.config import Paths


class BuildModel:
    """Class to build the model from a provided dataset."""

    def __init__(self, dataset):
        self.dataset = dataset
        self.model = None
        self.mae = None
        self.rmse = None

    def build(self):
        """ Build the model."""

        logging.info(f"Processing input data.")

        x, y = self._extract_features_and_target(self.dataset)
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)

        #x_train_scaled, x_test_scaled = self._scale_data(x_test, x_train)

        logging.info(f"Building model.")
        model = RandomForestClassifier()
        model.fit(X=x_train, y=y_train)

        self.model = model

        self._model_performances(x_test, y_test)

        self._save_model(processed_df_columns=self.dataset.columns)

    @staticmethod
    def _scale_data(x_test, x_train):
        # todo - see if we should save the scaler
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
        proba = [x[1] for x in predictions]
        self.mae = mean_absolute_error(y_pred=proba, y_true=y_test)
        self.rmse = mean_squared_error(y_pred=proba, y_true=y_test)
        logging.info(f"mae : {self.mae}")
        logging.info(f"rmse : {self.rmse}")

    def _save_model(self, processed_df_columns):
        current_ts = round(time.time())
        model_filename = f"model_{current_ts}.pkl"
        model_columns_filename = f"model_columns_{current_ts}.pkl"

        joblib.dump(self.model, os.path.join(Paths.model_dir, model_filename))
        model_columns = list(processed_df_columns)
        joblib.dump(model_columns, os.path.join(Paths.model_dir, model_columns_filename))
        logging.info(f"{model_filename} and {model_columns_filename} have been created.")
