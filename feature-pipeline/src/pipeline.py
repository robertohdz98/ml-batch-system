""" Module for Feature ETL Pipeline workflow.
"""

import datetime
import logging
import os
from typing import Optional

from extract import extract_from_api
from load import load_to_feature_store
from transform import transform_records


def run_etl_pipeline(
    export_end_reference_datetime: Optional[datetime.datetime] = None,
    minutes_delay: int = 15,
    minutes_export: int = 1440,  # (60min x 24h)
    url: str = os.getenv("DATASET_URL", "https://www.energidataservice.dk/tso-electricity/CO2Emis"),
    feature_group_version: int = 1
):
    """ Runs ETL pipeline from API (https://www.energidataservice.dk/tso-electricity/CO2Emis)
    """

    result, metadata = extract_from_api(
        export_end_reference_datetime,
        minutes_delay,
        minutes_export,
        url)
    logging.info("Extract step completed.")

    dataset = transform_records(result)
    logging.info("Tranform step completed.")

    # logging.info("Building validation expectation suite.")
    # validation_expectation_suite = validation.build_expectation_suite()
    # logging.info("Successfully built validation expectation suite.")

    # logging.info(f"Validating data and loading it to the feature store.")
    load_to_feature_store(
        dataset,
        # validation_expectation_suite=validation_expectation_suite,
        feature_group_version=feature_group_version,
    )
    metadata["feature_group_version"] = feature_group_version
    logging.info("Load step completed.")

    # utils.save_json(metadata, file_name="feature_pipeline_metadata.json")
    # logging.info("Done!")

    return metadata
