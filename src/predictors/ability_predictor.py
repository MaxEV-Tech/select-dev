import numpy as np
import pandas as pd
import xgboost as xgb
import datetime as dt
import typing as tp
import re

from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.base import BaseEstimator, TransformerMixin, ClassifierMixin
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
# from sklearn.metrics import accuracy_score, log_loss, classification_report

from sklearn.metrics import \
    mean_squared_error as mse, \
    mean_absolute_error as mae, \
    r2_score as r2, \
    mean_absolute_percentage_error as mape, get_scorer_names

from sklearn.preprocessing import OneHotEncoder as OHE
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler


class FlagsEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self._converter = None
        self._unique_flags: list[str] = ["B", "SO", "R", "W", "TI", "ME", "T", "ST", "D", "None"]

    def fit(self, data: pd.DataFrame, y=None, separator=","):
        """
        data: only DataFrame, doesn't work with Series
        """

        self._converter = lambda row: np.isin(self._unique_flags,
                                              row.split(separator))

        return self

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        data: only DataFrame, doesn't work with Series

        :return: pd.DataFrame
        """
        col_name = data.columns[0]
        return pd.DataFrame(data[col_name]
                            .astype("str")
                            .apply(self._converter)
                            .tolist(),
                            columns=self._unique_flags)


class NameEncoder(BaseEstimator, TransformerMixin):
    del_money = re.compile(r"(?:, |)\$[\d.,]+[KM]?(?: Gtd|)")
    border_types = re.compile(r"(?:[\[\]()]| -)")

    @staticmethod
    def converter(name: str) -> (str, str | None):
        clean = re.sub(NameEncoder.del_money,
                       "",
                       name)
        splitter = re.split(NameEncoder.border_types, clean)
        clean_name = splitter[0].strip()
        over_info = ",".join(splitter[1:]).rstrip(",") if len(splitter) > 1 else None

        return clean_name, over_info

    def fit(self, data: pd.DataFrame, y=None):
        """
        data: only DataFrame, doesn't work with Series
        """
        return self

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        data: only DataFrame, doesn't work with Series

        :return: pd.DataFrame
        """

        col_name = data.columns[0]
        return pd.DataFrame(data[col_name]
                            .astype("str")
                            .apply(NameEncoder.converter)
                            .tolist(),
                            columns=["name", "over info"])


class DataEncoder(BaseEstimator, TransformerMixin):
    @staticmethod
    def converter(time: dt.datetime):
        return time.date(), time.hour + 1 * (time.minute > 30), time, *np.eye(7)[time.weekday()]

    def fit(self, data: pd.DataFrame, y=None):
        """
        data: only DataFrame, doesn't work with Series
        """
        return self

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        data: only DataFrame, doesn't work with Series
        cols is timestamp, @duration, @date

        :return: pd.DataFrame
        """
        data_col = data.columns[0]

        return pd.DataFrame(data[data_col]
                            .apply(DataEncoder.converter)
                            .tolist())


class NoImputer(BaseEstimator, TransformerMixin):
    def fit(self, data: pd.DataFrame, y=None):
        return self

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        return data


class PreprocessData(BaseEstimator, TransformerMixin):
    def fit(self, data: pd.DataFrame, y=None):
        return self

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        flag_name = ["B", "SO", "R", "W", "TI", "ME", "T", "ST", "D", "None"]

        data = pd.DataFrame(data,
                            columns=["name", "over info", "date", "hour", "datetime",
                                     "mon", "tue", "wed", "thu", "fri", "sat", "sun"] + flag_name + [
                                        "stake", "rake", "gtd", "PpT"])

        data[["name", "over info"]] = data[["name", "over info"]].astype(str)

        data["datetime"] = pd.to_datetime(data["datetime"])

        data[["mon", "tue", "wed", "thu", "fri", "sat", "sun"] + flag_name] = data[
            ["mon", "tue", "wed", "thu", "fri", "sat", "sun"] + flag_name].astype(bool)

        data[["hour", "PpT"]] = data[["hour", "PpT"]].astype(int)

        data[["stake", "rake", "gtd"]] = data[["stake", "rake", "gtd"]].astype(float)

        return data


class DropSnD(BaseEstimator, TransformerMixin):
    def fit(self, data: pd.DataFrame, y=None):
        return self

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.select_dtypes(exclude=[object, dt.date, dt.time, dt.datetime, np.datetime64])


class AbilityPredictor:

    def __init__(self, network):
        self._network = network
        self._data_transformer = self.init_transformer()
        self.clean_data = Pipeline([
            ("transformer", self._data_transformer),
            ("naming", PreprocessData())
        ])
        raw_data = self.get_data_by_network()

        raw_data.dropna(subset=['AvAbility', '@duration'], inplace=True)
        raw_data['StartTime'] = pd.to_datetime(raw_data['timestamp'] - raw_data['@duration'], unit='s')

        target = raw_data["AvAbility"]
        x_train, x_test, y_train, y_test = train_test_split(raw_data, target, test_size=0.3)
        self.model = Pipeline([
            ("preprocess", self.clean_data),
            ("drop SnD", DropSnD()),
            ("model", xgb.XGBRegressor())
        ]).fit(x_train, y_train)

    def predict(self, data):
        data["StartTime"] = pd.to_datetime(data["@scheduledStartDate"], unit="s")
        data[["@guarantee", "@overlay", "@rake", "@stake"]] = data[
            ["@guarantee", "@overlay", "@rake", "@stake"]].astype(dtype=float)
        data["@playersPerTable"] = data["@playersPerTable"].astype(dtype=int)
        data["predictedAvAbility"] = self.model.predict(data)

        return data

    def get_data_by_network(self):
        return pd.read_csv(f'/home/dron/poker_data/{self._network}.csv')

    def init_transformer(self):
        flags_pipe = Pipeline(steps=[
            ("encoder", FlagsEncoder())
        ])

        names_pipe = Pipeline(steps=[
            ("encoder",
             NameEncoder())
        ])

        dates_pipe = Pipeline(steps=[
            ("encoder",
             DataEncoder())
        ])

        numeric_pipe = Pipeline(steps=[
            ("imputer", SimpleImputer()),
            ("scaler", StandardScaler())
        ])

        no_pipe = Pipeline(steps=[
            ("encoder", NoImputer())
        ])

        numerical_cols = ["@stake", "@rake", "@guarantee"]

        flags_cols = ["@flags"]

        name_cols = ["@name"]

        others_cols = ["@playersPerTable"]

        date_cols = ["StartTime"]

        return ColumnTransformer(
            [
                ("name", names_pipe, name_cols),
                ("date", dates_pipe, date_cols),
                ("flags", flags_pipe, flags_cols),
                ("numerics", numeric_pipe, numerical_cols),
                ("others", no_pipe, others_cols)
            ],
            remainder="drop"
        )
