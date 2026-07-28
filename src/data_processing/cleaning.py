import pandas as pd
import pytest

from data_processing.cleaning import (
    handle_missing_values,
    standardise_dates,
)


def test_handle_missing_forward_fill():
    """Covers the elif strategy == 'forward_fill' branch."""
    df = pd.DataFrame({'id': [1, 2, 3], 'value': [10, None, 30]})
    result = handle_missing_values(df, strategy='forward_fill')
    assert result['value'].tolist() == [10, 10, 30]


def test_handle_missing_invalid_strategy_raises():
    """Covers the final else: raise ValueError branch."""
    df = pd.DataFrame({'id': [1, 2], 'value': [10, None]})
    with pytest.raises(ValueError, match="Unknown strategy"):
        handle_missing_values(df, strategy='bogus_strategy')


def test_handle_missing_fill_without_value_raises():
    """Covers 'if fill_value is None: raise ValueError' branch."""
    df = pd.DataFrame({'id': [1, 2], 'value': [10, None]})
    with pytest.raises(ValueError, match="fill_value must be provided"):
        handle_missing_values(df, strategy='fill')


def test_standardise_dates_skips_missing_column():
    """Covers 'if col not in df.columns: continue' branch."""
    df = pd.DataFrame({'date': ['2024-01-01', '2024-06-15']})
    result = standardise_dates(df, date_columns=['date', 'does_not_exist'])
    assert 'does_not_exist' not in result.columns
    assert pd.api.types.is_datetime64_any_dtype(result['date'])


def test_standardise_dates_invalid_dtype_raises():
    """Attempts to trigger the except Exception -> raise branch.
    Note: pd.to_datetime with errors='coerce' rarely raises — it usually
    returns NaT instead. This test tries an input type that can genuinely
    break the conversion (e.g. a column of dicts), to force an exception.
    """
    df = pd.DataFrame({'date': [{'bad': 'data'}, {'bad': 'data2'}]})
    with pytest.raises(Exception):
        standardise_dates(df, date_columns='date')