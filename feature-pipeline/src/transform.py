""" Module for Transform Step of the Feature ETL Pipeline.
"""

import pandas as pd


def transform_records(dataset: pd.DataFrame):
    """
    Wrapper containing all the transformations from the ETL pipeline.
    """

    dataset = rename_columns(dataset)
    dataset = cast_columns(dataset)
    dataset = encode_area_column(dataset)

    return dataset


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns to match our schema.
    """

    dataset = df.copy()
    dataset.drop(columns=["Minutes5DK"], inplace=True)

    dataset.rename(
        columns={
            "Minutes5UTC": "datetime_utc",
            "PriceArea": "price_area",
            "CO2Emission": "co2_emission",
        },
        inplace=True,
    )

    return dataset


def cast_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cast columns to the correct data type.
    """

    dataset = df.copy()

    dataset["datetime_utc"] = pd.to_datetime(dataset["datetime_utc"])
    dataset["price_area"] = dataset["price_area"].astype("string")
    dataset["energy_consumption"] = dataset["co2_emission"].astype("float64")

    return dataset


def encode_area_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode the area column to integers.
    """

    dataset = df.copy()

    area_mappings = {"DK": 0,
                     "DK1": 1,
                     "DK2": 2}

    dataset["price_area"] = dataset["price_area"].map(lambda a: area_mappings.get(a))
    dataset["price_area"] = dataset["price_area"].astype("int8")

    return dataset
