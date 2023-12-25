""" Module for Extract Step of the Feature ETL Pipeline.
"""

import datetime
import logging
from json import JSONDecodeError
from typing import Optional

import pandas as pd
import requests


def extract_from_api(export_end_reference_datetime: Optional[datetime.datetime] = None,
                     minutes_delay: int = 15,
                     minutes_export: int = 1440,
                     url: str = "https://api.energidataservice.dk/dataset/CO2Emis"):
    """ Extracts raw data from API.
    https://www.energidataservice.dk/tso-electricity/CO2Emis

    Args:
    ------
        - export_end_reference_datetime
        - minutes_delay
        - minutes_export
        - url

    Returns:
    --------
        -
    """

    if not export_end_reference_datetime:
        export_end_reference_datetime = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    else:
        export_end_reference_datetime = export_end_reference_datetime.replace(second=0, microsecond=0)

    end_date = export_end_reference_datetime - datetime.timedelta(minutes=minutes_delay)
    start_date = export_end_reference_datetime - datetime.timedelta(minutes=minutes_delay + minutes_export)

    url = _build_url(start_date, end_date, url)
    logging.info("Request URL: %s", url)

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            raise Exception("Error in request: %s", response.status_code)

        result = response.json()
        logging.info("Number of records extracted: %s", result['total'])

        records = result['records']
        records = pd.DataFrame.from_records(records)

        # Prepare metadata
        datetime_format = "%Y-%m-%dT%H:%M:%SZ"

        metadata = {
            "minutes_delay": minutes_delay,
            "minutes_export": minutes_export,
            "url": url,
            "start_datetime_utc": start_date.strftime(datetime_format),
            "end_datetime_utc": end_date.strftime(datetime_format),
            "datetime_format": datetime_format,
        }

        return records, metadata

    except JSONDecodeError:
        logging.error("Response status [%s]. Could not decode response [URL: %s]",
                      response.status_code, url)

        return None


def _build_url(start_date: datetime.datetime, end_date: datetime.datetime, base_url: str):
    """ Builds the complete url for the API request according to desired time range.
    Results from most recent to oldest.
    """

    start = start_date.strftime("%Y-%m-%dT%H:%M")
    end = end_date.strftime("%Y-%m-%dT%H:%M")
    sorting_column = "Minutes5UTC"

    url = base_url + f"?offset=0&start={start}&end={end}&sort={sorting_column}%20DESC"

    return url
