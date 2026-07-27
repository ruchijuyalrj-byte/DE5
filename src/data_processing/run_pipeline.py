"""
Library Data Pipeline - Orchestration Script
============================================

This script orchestrates the complete data pipeline:
1. Load raw data from bronze layer
2. Clean and validate the data
3. Save cleaned data to silver layer
4. Print summary statistics

Author: [Your Name]
Date: [Today's Date]
Module: DE5 Module 5 - Product Development

Run this from the command line as follows:
> pip install -e .
> python -m data_processing.run_pipeline
"""

import re
import pandas as pd
from pathlib import Path
from datetime import datetime

# Import our custom functions
from data_processing.ingestion import load_csv, load_json, load_excel
from data_processing.cleaning import (
    remove_duplicates,
    handle_missing_values,
    standardise_dates,
)
from data_processing.validation import validate_isbn


# ============================================
# CONFIGURATION
# ============================================

# Define our data directories (medallion architecture)
BRONZE_DIR = Path('data')
SILVER_DIR = Path('data/silver')

# Create silver directory if it doesn't exist
SILVER_DIR.mkdir(parents=True, exist_ok=True)


# ============================================
# HELPER FUNCTIONS
# ============================================

def print_section_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_dataframe_info(df, name):
    """Print useful information about a DataFrame."""
    print(f"\n{name}:")
    print(f"  - Rows: {len(df):,}")
    print(f"  - Columns: {len(df.columns)}")
    print(f"  - Missing values: {df.isnull().sum().sum():,}")
    try:
        dupes = df.duplicated().sum()
    except TypeError:
        dupes = 'N/A'
    print(f"  - Duplicates: {dupes}")


def save_to_silver(df, filename):
    """Save DataFrame to silver layer as CSV."""
    filepath = SILVER_DIR / filename
    df.to_csv(filepath, index=False)
    return filepath


# ============================================
# PIPELINE STAGES
# ============================================

def process_circulation_data(warnings):
    """
    Process circulation data (borrowing transactions).

    Steps:
    1. Load from bronze
    2. Remove duplicates
    3. Handle missing values
    4. Standardise dates
    5. Clean ISBNs
    6. Save to silver
    """
    print_section_header("Processing Circulation Data")

    # Step 1: Load raw data
    print("\n[1/6] Loading raw data...")
    df = load_csv('data/circulation_data.csv')
    print_dataframe_info(df, "Raw data")

    # Step 2: Remove duplicates
    print("\n[2/6] Removing duplicates...")
    input_dupes = df.duplicated(subset=['transaction_id']).sum()
    df_clean = remove_duplicates(df, subset=['transaction_id'])
    rows_removed = len(df) - len(df_clean)
    print(f"  - Removed {rows_removed:,} duplicate rows")
    if input_dupes > 0 and df_clean.duplicated(subset=['transaction_id']).sum() == input_dupes:
        warnings.append(f"Circulation: remove_duplicates() left {input_dupes} duplicates unchanged - is it implemented?")

    # Step 3: Handle missing values
    print("\n[3/6] Handling missing values...")
    input_missing = df_clean.isnull().sum().sum()
    df_clean = handle_missing_values(df_clean, strategy='drop')
    output_missing = df_clean.isnull().sum().sum()
    print(f"  - Dropped rows with missing values")
    if input_missing > 0 and output_missing == input_missing:
        warnings.append(f"Circulation: handle_missing_values() left {input_missing:,} missing values unchanged - is it implemented?")

    # Step 4: Standardise dates
    print("\n[4/6] Standardising dates...")
    df_clean = standardise_dates(df_clean, date_columns=['checkout_date', 'return_date'])

    # Step 5: Clean ISBNs (if isbn column exists)
    if 'isbn' in df_clean.columns:
        print("\n[5/6] Cleaning ISBNs...")
        original_isbns = df_clean['isbn']
        df_clean['ISBN_Clean'] = df_clean['isbn'].apply(validate_isbn)
        invalid_count = df_clean['ISBN_Clean'].isnull().sum()
        unchanged_count = (df_clean['ISBN_Clean'] == original_isbns).sum()
        print(f"  - Found {invalid_count:,} invalid ISBNs")
        if unchanged_count == len(df_clean) and len(df_clean) > 0:
            warnings.append(f"Circulation: validate_isbn() returned input unchanged for all {len(df_clean):,} rows - is it implemented?")

    # Step 6: Save cleaned data
    print("\n[6/6] Saving cleaned data...")
    filepath = save_to_silver(df_clean, 'circulation_clean.csv')
    print(f"  [OK] Saved to: {filepath}")
    print_dataframe_info(df_clean, "Cleaned data")

    return df_clean


def process_events_data(warnings):
    """
    Process events data (library events from JSON).

    Steps:
    1. Load from bronze
    2. Flatten nested JSON
    3. Handle missing values
    4. Save to silver
    """
    print_section_header("Processing Events Data")

    # Step 1: Load raw data
    print("\n[1/3] Loading raw data...")
    df = load_json('data/events_data.json')
    print_dataframe_info(df, "Raw data")

    # Step 2: Handle missing values
    print("\n[2/3] Handling missing values...")
    input_missing = df.isnull().sum().sum()
    df_clean = handle_missing_values(df, strategy='drop')
    output_missing = df_clean.isnull().sum().sum()
    if input_missing > 0 and output_missing == input_missing:
        warnings.append(f"Events: handle_missing_values() left {input_missing:,} missing values unchanged - is it implemented?")

    # Step 3: Save cleaned data
    print("\n[3/3] Saving cleaned data...")
    filepath = save_to_silver(df_clean, 'events_clean.csv')
    print(f"  [OK] Saved to: {filepath}")

    print_dataframe_info(df_clean, "Cleaned data")

    return df_clean


def process_catalogue_data(warnings):
    """
    Process catalogue data (book catalogue from Excel).

    Steps:
    1. Load from bronze
    2. Remove duplicates
    3. Clean ISBNs
    4. Handle missing values
    5. Save to silver
    """
    print_section_header("Processing Catalogue Data")

    # Step 1: Load raw data
    print("\n[1/4] Loading raw data...")
    df = load_excel('data/catalogue.xlsx')
    print_dataframe_info(df, "Raw data")

    # Step 2: Remove duplicates
    print("\n[2/4] Removing duplicates...")
    input_dupes = df.duplicated(subset=['ISBN']).sum()
    df_clean = remove_duplicates(df, subset=['ISBN'])
    rows_removed = len(df) - len(df_clean)
    print(f"  - Removed {rows_removed:,} duplicate rows")
    if input_dupes > 0 and df_clean.duplicated(subset=['ISBN']).sum() == input_dupes:
        warnings.append(f"Catalogue: remove_duplicates() left {input_dupes} duplicates unchanged - is it implemented?")

    # Step 3: Clean ISBNs (if ISBN column exists)
    if 'ISBN' in df_clean.columns:
        print("\n[3/4] Cleaning ISBNs...")
        original_isbns = df_clean['ISBN']
        df_clean['ISBN_Clean'] = df_clean['ISBN'].apply(validate_isbn)
        invalid_count = df_clean['ISBN_Clean'].isnull().sum()
        unchanged_count = (df_clean['ISBN_Clean'] == original_isbns).sum()
        print(f"  - Found {invalid_count:,} invalid ISBNs")
        if unchanged_count == len(df_clean) and len(df_clean) > 0:
            warnings.append(f"Catalogue: validate_isbn() returned input unchanged for all {len(df_clean):,} rows - is it implemented?")

    # Step 4: Save cleaned data
    print("\n[4/4] Saving cleaned data...")
    filepath = save_to_silver(df_clean, 'catalogue_clean.csv')
    print(f"  [OK] Saved to: {filepath}")

    print_dataframe_info(df_clean, "Cleaned data")

    return df_clean


def process_feedback_data():
    """
    Process feedback data (unstructured text).

    Note: This is a simplified version.
    In practice, you'd parse the text file properly.

    Steps:
    1. Load raw text
    2. Parse into structured format
    3. Save to silver
    """
    print_section_header("Processing Feedback Data")

    print("\n[1/2] Loading and parsing feedback text...")

    # Read the text file
    with open('data/feedback.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    # Count the feedbacks
    feedback_count = content.count('Feedback #')
    print(f"  - Found {feedback_count} feedback entries")

    # Capture both branch name and rating number
    pattern = r"- ([A-Za-z\s]+ Branch) ~ (\d)⭐"
    matches = re.findall(pattern, content)

    # Convert to DataFrame
    df = pd.DataFrame(matches, columns=["branch", "rating"])
    df["rating"] = df["rating"].astype(int)

    # Group by SBranch and Rating
    df_summary = (
        df.groupby(["branch", "rating"], as_index=False).size().rename(columns={"size": "count"})
    )

    # Step 2: Save
    print("\n[2/2] Saving processed feedback...")
    filepath = save_to_silver(df_summary, "feedback_summary.csv")
    print(f"  [OK] Saved to: {filepath}")

    print(f"  - Processed {feedback_count} feedback entries")

    return df


# ============================================
# MAIN PIPELINE
# ============================================

def run_pipeline():
    """
    Run the complete data pipeline.

    This orchestrates all data processing stages and
    produces a summary report.
    """
    print("\n" + "=" * 60)
    print("  LIBRARY DATA PIPELINE")
    print("  Starting pipeline execution...")
    print("  Time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    # Track pipeline metrics
    start_time = datetime.now()
    results = {}
    warnings = []

    try:
        # Process each data source
        results['circulation'] = process_circulation_data(warnings)
        results['events'] = process_events_data(warnings)
        results['catalogue'] = process_catalogue_data(warnings)
        results['feedback'] = process_feedback_data()

        # Calculate pipeline statistics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Print final summary
        print_section_header("PIPELINE SUMMARY")
        print("\n[OK] Pipeline completed successfully!")
        print(f"  - Duration: {duration:.2f} seconds")
        print(f"  - Files processed: {len(results)}")
        print(f"  - Output directory: {SILVER_DIR}")

        print("\nCleaned files created:")
        for file in SILVER_DIR.glob("*.csv"):
            print(f"  - {file.name}")

        if warnings:
            print(f"\n  [!] {len(warnings)} warning(s) - review before submitting:")
            for w in warnings:
                print(f"    [!] {w}")

        print("\n" + "=" * 60)
        print("  Next steps:")
        print("  1. Review the cleaned data in data/silver/")
        print("  2. Run your data quality analysis")
        print("  3. Deploy to Microsoft Fabric")
        print("=" * 60 + "\n")

        return results

    except Exception as e:
        print(f"\n[ERROR] Pipeline failed with error: {str(e)}")
        print("  - Check your data files exist")
        print("  - Check your functions are working")
        raise


# ============================================
# SCRIPT ENTRY POINT
# ============================================

if __name__ == "__main__":
    """
    This runs when you execute: python -m data_processing.run_pipeline
    """
    results = run_pipeline()
