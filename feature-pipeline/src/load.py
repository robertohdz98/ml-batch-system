""" Module for Load Step of the Feature ETL Pipeline.
"""

import logging
import os

import hopsworks
import pandas as pd


def load_to_feature_store(
    dataset: pd.DataFrame,
    # validation_expectation_suite: ExpectationSuite,
    feature_group_version: int,
):
    """ Loads transformed data into Feature Store (Hopsworks).
    """

    logging.info("Batch writed into Feature Store.")

    # Connect to feature store.
    conn = hopsworks.login(
        api_key_value=os.getenv("FEATURE_STORE_API_KEY"),
        project=os.getenv("FEATURE_STORE_PROJECT", "ml_batch_system")
    )

    feature_store = conn.get_feature_store()

    # Create feature group
    co2_feature_group = feature_store.get_or_create_feature_group(
        name="co2_emission",
        version=feature_group_version,
        description="CO2 emission from electricity consumed in Denmark measured in g/kWh",
        primary_key=["price_area"],
        event_time="datetime_utc",
        online_enabled=False,
        # expectation_suite=validation_expectation_suite,
    )

    # Upload data.
    co2_feature_group.insert(
        features=dataset,
        overwrite=False,
        write_options={
            "wait_for_job": True,
        },
    )

    # Add feature descriptions.
    feature_descriptions = [
        {
            "name": "datetime_utc",
            "description": """
                            Datetime interval in UTC when the data was observed.
                            """,
            "validation_rules": "The resolution of the data is 5 minutes ",
        },
        {
            "name": "price_area",
            "description": """
                            Denmark is divided in two price areas, divided by the Great Belt: DK1 and DK2.
                            If price area is “DK”, the data covers all Denmark.
                            """,
            "validation_rules": "0 (DK), 1 (DK1) or 2 (DK2) (int)",
        },
        {
            "name": "co2_emission",
            "description": "CO2 emission from electricity consumed in Denmark measured in g/kWh.",
            "validation_rules": ">=0 (float)",
        },
    ]
    for description in feature_descriptions:
        co2_feature_group.update_feature_description(
            description["name"], description["description"]
        )

    # Update statistics.
    co2_feature_group.statistics_config = {
        "enabled": True,
        "histograms": True,
        "correlations": True,
    }
    co2_feature_group.update_statistics_config()
    co2_feature_group.compute_statistics()

    return co2_feature_group
