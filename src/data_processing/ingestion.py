"""Data ingestion functions.

TODO: Complete these functions for the library project.
"""

import json
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def load_csv(filepath, **kwargs):
    """Load CSV file into DataFrame.

    Args:
        filepath (str): Path to CSV file
        **kwargs: Additional arguments for pd.read_csv()

    Returns:
        pd.DataFrame: Loaded data

    Raises:
        FileNotFoundError: If file doesn't exist
        pd.errors.EmptyDataError: If file is empty

    Example:
        >>> df = load_csv('data/circulation.csv')
        >>> print(len(df))
    """
    filepath = Path(filepath)

    # Check file exists
    if not filepath.exists():
        logger.error(f"File not found: {filepath}")
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        logger.info(f"Loading CSV from {filepath}")
        df = pd.read_csv(filepath, **kwargs)
        logger.info(f"Successfully loaded {len(df)} rows from {filepath}")
        return df

    except pd.errors.EmptyDataError:
        logger.error(f"CSV file is empty: {filepath}")
        raise
    except Exception as e:
        logger.error(f"Error loading CSV {filepath}: {e}")
        raise
    """Load CSV file with error handling.

    Args:
        filepath: Path to CSV file

    Returns:
        DataFrame with loaded data

    TODO: Add error handling and logging
    """

            # Check file exists
    if not filepath.exists():
        logger.error(f"CSV File not found: {filepath}")
        raise FileNotFoundError(f"CSV File not found: {filepath}")
    return pd.read_csv(filepath)


def load_json(filepath):
    """Load JSON file and flatten nested structure into a DataFrame.

    Args:
        filepath (str): Path to JSON file

    Returns:
        pd.DataFrame: Loaded, flattened data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON

    Example:
        >>> df = load_json('data/events.json')
    """
    filepath = Path(filepath)

    if not filepath.exists():
        logger.error(f"File not found: {filepath}")
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        logger.info(f"Loading JSON from {filepath}")
        with open(filepath, 'r') as f:
            data = json.load(f)

        df = pd.json_normalize(data)

        logger.info(f"Successfully loaded {len(df)} records from {filepath}")
        return df

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading JSON {filepath}: {e}")
        raise
    """Load JSON file and flatten structure.

    Args:
        filepath: Path to JSON file

    Returns:
        DataFrame with flattened data

    TODO: Implement JSON loading and flattening
    """

        # Check file exists
    if not filepath.exists():
        logger.error(f"JSON File not found: {filepath}")
        raise FileNotFoundError(f"JSON File not found: {filepath}")
    with open(filepath, 'r') as f:
        data = json.load(f)
    return pd.json_normalize(data)


def load_excel(filepath, sheet_name=0, **kwargs):
    """Load Excel file into DataFrame.

    Args:
        filepath (str | Path): Path to Excel file
        sheet_name (str|int|list[str|int]|None): Sheets to read
        **kwargs: Additional arguments for pd.read_excel()

    Returns:
        pd.DataFrame | dict[str, pd.DataFrame]: Loaded data. Dict when multiple sheets requested.

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If the sheet doesn't exist or file is invalid
        ImportError: If the required Excel engine isn't installed
        Exception: For other read errors

    Example:
        >>> df = load_excel('../data/catalogue.xlsx', sheet_name='Catalogue')
        >>> print(len(df))
    """
    filepath = Path(filepath)

    # Check file exists
    if not filepath.exists():
        logger.error(f"Excel File not found: {filepath}")
        raise FileNotFoundError(f"Excel File not found: {filepath}")

    try:
        logger.info(f"Loading Excel from {filepath} (sheet_name={sheet_name})")
        df = pd.read_excel(filepath, sheet_name=sheet_name, **kwargs)

        if isinstance(df, dict):
            total_rows = sum(len(v) for v in df.values())
            line = f"Successfully loaded {len(df)} sheets, total {total_rows} rows from {filepath}"
            logger.info(line)
        else:
            logger.info(f"Successfully loaded {len(df)} rows from {filepath}")

        return df

    except ValueError as e:
        logger.error(f"Value error loading Excel {filepath}: {e}")
        raise
    except ImportError as e:
        logger.error(f"Missing Excel engine for {filepath}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading Excel {filepath}: {e}")
        raise
