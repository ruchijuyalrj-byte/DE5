"""Example test to demonstrate pytest.

Copy this pattern for your own tests!
"""

import pytest
import pandas as pd


@pytest.fixture
def sample_df():
    """Sample DataFrame for testing."""
    return pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie']
    })


def test_example(sample_df):
    """Example test - shows pytest working."""
    assert len(sample_df) == 3
    assert 'id' in sample_df.columns
    assert sample_df['id'].is_unique
