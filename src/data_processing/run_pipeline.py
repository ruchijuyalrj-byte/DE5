from pathlib import Path
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from data_processing import run_pipeline as rp

# --- Helper function tests ---

def test_print_dataframe_info_handles_duplicated_typeerror(capsys):
    """Covers the try/except TypeError around df.duplicated()."""
    # A column of unhashable types (e.g. lists) makes .duplicated() raise TypeError
    df = pd.DataFrame({'a': [[1, 2], [3, 4]]})
    rp.print_dataframe_info(df, "Test Data")
    captured = capsys.readouterr()
    assert "Duplicates: N/A" in captured.out


def test_save_to_silver_writes_csv(tmp_path, monkeypatch):
    """Covers save_to_silver, redirecting SILVER_DIR to a temp folder."""
    monkeypatch.setattr(rp, 'SILVER_DIR', tmp_path)
    df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
    filepath = rp.save_to_silver(df, 'test_output.csv')
    assert filepath.exists()
    result = pd.read_csv(filepath)
    pd.testing.assert_frame_equal(result, df)


# --- process_circulation_data: warning branches ---

def test_process_circulation_data_warns_when_duplicates_not_removed():
    """Covers the warning branch when remove_duplicates() doesn't actually work."""
    raw_df = pd.DataFrame({
        'transaction_id': [1, 1, 2],
        'checkout_date': ['2024-01-01'] * 3,
        'return_date': ['2024-01-05'] * 3,
    })

    with patch.object(rp, 'load_csv', return_value=raw_df), \
         patch.object(rp, 'remove_duplicates', side_effect=lambda df, subset: df), \
         patch.object(rp, 'handle_missing_values', side_effect=lambda df, strategy: df), \
         patch.object(rp, 'standardise_dates', side_effect=lambda df, date_columns: df), \
         patch.object(rp, 'save_to_silver', return_value=Path('fake_path.csv')):

        warnings = []
        rp.process_circulation_data(warnings)
        assert any("remove_duplicates()" in w for w in warnings)


def test_process_circulation_data_warns_when_missing_values_not_handled():
    """Covers the warning branch when handle_missing_values() doesn't actually work."""
    raw_df = pd.DataFrame({
        'transaction_id': [1, 2],
        'checkout_date': ['2024-01-01', None],
        'return_date': ['2024-01-05', '2024-01-06'],
    })

    with patch.object(rp, 'load_csv', return_value=raw_df), \
         patch.object(rp, 'remove_duplicates', side_effect=lambda df, subset: df), \
         patch.object(rp, 'handle_missing_values', side_effect=lambda df, strategy: df), \
         patch.object(rp, 'standardise_dates', side_effect=lambda df, date_columns: df), \
         patch.object(rp, 'save_to_silver', return_value=Path('fake_path.csv')):

        warnings = []
        rp.process_circulation_data(warnings)
        assert any("handle_missing_values()" in w for w in warnings)


def test_process_circulation_data_warns_when_isbn_not_validated():
    """Covers the warning branch when validate_isbn() returns input unchanged."""
    raw_df = pd.DataFrame({
        'transaction_id': [1, 2],
        'checkout_date': ['2024-01-01', '2024-01-02'],
        'return_date': ['2024-01-05', '2024-01-06'],
        'isbn': ['123', '456'],
    })

    with patch.object(rp, 'load_csv', return_value=raw_df), \
         patch.object(rp, 'remove_duplicates', side_effect=lambda df, subset: df), \
         patch.object(rp, 'handle_missing_values', side_effect=lambda df, strategy: df), \
         patch.object(rp, 'standardise_dates', side_effect=lambda df, date_columns: df), \
         patch.object(rp, 'validate_isbn', side_effect=lambda x: x), \
         patch.object(rp, 'save_to_silver', return_value=Path('fake_path.csv')):

        warnings = []
        rp.process_circulation_data(warnings)
        assert any("validate_isbn()" in w for w in warnings)


# --- process_feedback_data: regex parsing ---

def test_process_feedback_data_parses_and_groups_correctly():
    """Covers the regex parsing + groupby logic in process_feedback_data."""
    fake_content = (
        "Feedback #1\n- Central Branch ~ 5⭐\n"
        "Feedback #2\n- Central Branch ~ 5⭐\n"
        "Feedback #3\n- North Branch ~ 3⭐\n"
    )

    with patch('builtins.open', mock_open(read_data=fake_content)), \
         patch.object(rp, 'save_to_silver', return_value=Path('fake_path.csv')):

        result = rp.process_feedback_data()
        assert len(result) == 3
        assert set(result['branch']) == {'Central Branch', 'North Branch'}
        assert result['rating'].tolist() == [5, 5, 3]


# --- run_pipeline: success and failure paths ---

def test_run_pipeline_success_path(tmp_path, monkeypatch, capsys):
    """Covers the try block's happy path, including the warnings-printed branch."""
    monkeypatch.setattr(rp, 'SILVER_DIR', tmp_path)

    dummy_df = pd.DataFrame({'a': [1]})

    with patch.object(rp, 'process_circulation_data', return_value=dummy_df) as mock_circ, \
         patch.object(rp, 'process_events_data', return_value=dummy_df), \
         patch.object(rp, 'process_catalogue_data', return_value=dummy_df), \
         patch.object(rp, 'process_feedback_data', return_value=dummy_df):

        # simulate a warning being appended by process_circulation_data
        def add_warning(warnings):
            warnings.append("Fake warning for test")
            return dummy_df
        mock_circ.side_effect = add_warning

        result = rp.run_pipeline()
        captured = capsys.readouterr()
        assert "PIPELINE SUMMARY" in captured.out
        assert "warning(s)" in captured.out
        assert 'circulation' in result


def test_run_pipeline_failure_path_reraises(capsys):
    """Covers the except Exception block — error is printed and re-raised."""
    with patch.object(rp, 'process_circulation_data', side_effect=ValueError("boom")):
        with pytest.raises(ValueError, match="boom"):
            rp.run_pipeline()
        captured = capsys.readouterr()
        assert "[ERROR] Pipeline failed" in captured.out