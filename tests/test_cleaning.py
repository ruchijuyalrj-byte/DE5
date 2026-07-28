import pandas as pd
import pytest

from data_processing.cleaning import (
    handle_missing_values,
    remove_duplicates,
    standardise_dates,
)


@pytest.fixture
def sample_with_duplicates():
    return pd.DataFrame({
        'id': [1, 2, 2, 3],
        'name': ['Alice', 'Bob', 'Bob', 'Charlie']
    })

@pytest.fixture
def sample_with_missing():
    return pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', None, 'Charlie'],
        'value': [10, None, 30]
    })

def test_remove_duplicates_reduces_rows(sample_with_duplicates):
    result = remove_duplicates(sample_with_duplicates, subset=['id'])
    # TODO: assert result has 3 rows

def test_remove_duplicates_ids_are_unique(sample_with_duplicates):
    result = remove_duplicates(sample_with_duplicates, subset=['id'])
    # TODO: assert that id values are unique

def test_handle_missing_drop(sample_with_missing):
    result = handle_missing_values(sample_with_missing, strategy='drop')
    # TODO: assert result has no missing values

def test_handle_missing_fill(sample_with_missing):
    result = handle_missing_values(sample_with_missing, strategy='fill', fill_value=0)
    # TODO: assert result has 3 rows

def test_standardise_dates():
    df = pd.DataFrame({'date': ['2024-01-01', '2024-06-15']})
    result = standardise_dates(df, date_columns=['date'])
    # TODO: assert the date column is datetime type

def test_handle_missing_fill(sample_with_missing):
    result = handle_missing_values(sample_with_missing, strategy='fill', fill_value=0)
    assert len(result) == 3

# --- handle_missing_values: 'forward_fill' strategy is never tested ---
def test_handle_missing_forward_fill():
    df = pd.DataFrame({'id': [1, 2, 3], 'value': [10, None, 30]})
    result = handle_missing_values(df, strategy='forward_fill')
    assert result['value'].tolist() == [10, 10, 30]


# --- handle_missing_values: invalid strategy should raise ValueError ---
def test_handle_missing_invalid_strategy_raises():
    df = pd.DataFrame({'id': [1, 2], 'value': [10, None]})
    with pytest.raises(ValueError, match="Unknown strategy"):
        handle_missing_values(df, strategy='not_a_real_strategy')


# --- handle_missing_values: strategy='fill' with no fill_value should raise ---
def test_handle_missing_fill_without_fill_value_raises():
    df = pd.DataFrame({'id': [1, 2], 'value': [10, None]})
    with pytest.raises(ValueError, match="fill_value must be provided"):
        handle_missing_values(df, strategy='fill')


# --- handle_missing_values: specific 'columns' param is respected ---
def test_handle_missing_targets_specific_columns_only():
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'value': [10, None, 30],
        'other': [None, None, None]
    })
    result = handle_missing_values(df, strategy='drop', columns=['value'])
    # only rows with missing 'value' are dropped; 'other' column's NaNs are ignored
    assert len(result) == 2
    assert result['value'].isnull().sum() == 0


# --- standardise_dates: column not present in df should warn and skip, not crash ---
def test_standardise_dates_missing_column_is_skipped(caplog):
    df = pd.DataFrame({'date': ['2024-01-01', '2024-06-15']})
    result = standardise_dates(df, date_columns=['date', 'nonexistent_col'])
    assert 'nonexistent_col' not in result.columns
    assert pd.api.types.is_datetime64_any_dtype(result['date'])