"""Data cleaning functions for library pipeline.

The cleaning module
This module contains functions for cleaning and standardising data.
All functions return new DataFrames without modifying the input.
"""

# Uncomment when needed:
# import pandas as pd
# from typing import List, Optional

import logging

logger = logging.getLogger(__name__)


def remove_duplicates(df, subset=None):
    """Remove duplicate rows from DataFrame."""
    df = df.copy()  # Work on a copy!
    return df


def handle_missing_values(df, strategy='drop', fill_value=None, columns=None):
    """Handle missing values in DataFrame."""
    df = df.copy()
    return df


def standardise_dates(df, date_columns, date_format='%Y-%m-%d'):
    """Standardise date columns to consistent format."""
    df = df.copy()
    return df
