"""Data ingestion functions.

TODO: Complete these functions for the library project.
"""

import json

import logging
import pandas as pd
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_csv(filepath):
    """Load CSV file with error handling.

    Args:
        filepath: Path to CSV file

    Returns:
        DataFrame with loaded data

    TODO: Add error handling and logging
    """
    return pd.read_csv(filepath)


def load_json(filepath):
    """Load JSON file and flatten structure.

    Args:
        filepath: Path to JSON file

    Returns:
        DataFrame with flattened data

    TODO: Implement JSON loading and flattening
    """
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
