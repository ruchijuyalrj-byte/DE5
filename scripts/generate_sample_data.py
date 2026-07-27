"""
Generate sample library data with realistic quality issues.

This creates 4 files for the library pipeline project:
- circulation_data.csv (with duplicates, missing values, date format issues)
- events_data.json (flat array of events)
- feedback.txt (unstructured text)
- catalogue.xlsx (messy Excel with formatting issues)
"""

from faker import Faker
import pandas as pd
import json
import random
from datetime import date, datetime, timedelta
import numpy as np


# Set number of records
CIRCULATION = 5000
EVENTS = 500
FEEDBACK = 200
CATALOGUE = 5000

fake = Faker('en_GB')  # UK locale for London library
Faker.seed(42)  # Reproducible data
random.seed(42)
np.random.seed(42)

# ============================================
# 1. CIRCULATION DATA (CSV with quality issues)
# ============================================


def generate_circulation_data(n, isbn_pool):
    """Generate circulation data with intentional quality issues.

    isbn values are drawn from isbn_pool (the catalogue's ISBNs) so that
    circulation and catalogue can be joined on ISBN after cleaning.
    """

    data = []

    for i in range(n):
        record = {
            'transaction_id': f'TXN{i:06d}',
            'member_id': f'M{random.randint(10000, 99999)}',
            'isbn': random.choice(isbn_pool) if random.random() > 0.05 else None,  # 5% missing
            'checkout_date': fake.date_between(start_date='-2y', end_date='today'),
            'return_date': None,  # Will fill below
            'branch_id': f'BR{random.randint(1, 15):03d}'
        }

        # Add return date (usually after checkout)
        if random.random() > 0.1:  # 10% not returned yet
            checkout = record['checkout_date']
            return_days = random.randint(1, 30)
            record['return_date'] = checkout + timedelta(days=return_days)

        data.append(record)

    df = pd.DataFrame(data)

    # INJECT QUALITY ISSUES

    # 1. Duplicate transactions (2%)
    duplicate_indices = random.sample(range(len(df)), int(len(df) * 0.02))
    duplicates = df.iloc[duplicate_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    # 2. Inconsistent date formats (convert some to strings)
    date_format_issues = random.sample(range(len(df)), int(len(df) * 0.1))
    for idx in date_format_issues:
        if df.loc[idx, 'checkout_date']:
            # Mix of UK and US date formats
            if random.random() > 0.5:
                df.loc[idx, 'checkout_date'] = df.loc[idx, 'checkout_date'].strftime('%d/%m/%Y')
            else:
                df.loc[idx, 'checkout_date'] = df.loc[idx, 'checkout_date'].strftime('%m/%d/%Y')

    # 3. Some missing member_ids (2%)
    missing_members = random.sample(range(len(df)), int(len(df) * 0.02))
    df.loc[missing_members, 'member_id'] = None

    # 4. Whitespace issues in branch_id
    whitespace_issues = random.sample(range(len(df)), int(len(df) * 0.03))
    for idx in whitespace_issues:
        df.loc[idx, 'branch_id'] = '  ' + df.loc[idx, 'branch_id'] + ' '

    return df

# ============================================
# 2. EVENTS DATA (flat JSON array)
# ============================================


def generate_events_data(n):
    """Generate events data as a flat JSON array."""

    event_types = [
        'Children\'s Story Hour',
        'Book Club Meeting',
        'Author Talk',
        'Computer Skills Workshop',
        'Teen Gaming Night',
        'Homework Help Session'
    ]

    branches = [
        'Stratford', 'East Ham', 'Manor Park', 'Plaistow',
        'Custom House', 'North Woolwich', 'Beckton'
    ]

    events = []

    for i in range(n):
        event = {
            'event_id': f'EVT{i:04d}',
            'name': random.choice(event_types),
            'branch': random.choice(branches),  # ⚠️ Note: not branch_id!
            'date': fake.date_between(start_date='-1y', end_date='today').isoformat(),
            'attendance': {
                'registered': random.randint(10, 50),
                'actual': random.randint(5, 45),
                'age_breakdown': {
                    '0-5': random.randint(0, 10),
                    '6-12': random.randint(0, 15),
                    '13-17': random.randint(0, 10),
                    '18+': random.randint(0, 20)
                }
            },
            'feedback_score': round(random.uniform(3.0, 5.0), 1) if random.random() > 0.1 else None
        }

        events.append(event)

    return events

# ============================================
# 3. FEEDBACK DATA (Unstructured text)
# ============================================


def maybe_add_typo(text):
    """Randomly introduce a small typo or remove punctuation."""

    if random.random() < 0.1:
        # 10% chance of typo
        if random.random() < 0.5:
            # drop the last punctuation mark
            return text.rstrip('!.,')
        else:
            # simple character swap to simulate typo
            pos = random.randint(0, len(text) - 2)
            chars = list(text)
            chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
            return ''.join(chars)

    if random.random() < 0.02:
        return text.upper()

    return text


def generate_feedback_data(n):
    """Generate unstructured feedback text."""

    positive_templates = [
        "I love the {}! The staff were so helpful.",
        "Great selection of {}. Very impressed!",
        "The {} is wonderful. My children enjoy it so much.",
        "Excellent {} service. Thank you!",
        "Really appreciate the {}. Keep up the good work!"
    ]

    negative_templates = [
        "The {} is always {}. Very frustrating.",
        "Not happy with {}. Needs improvement.",
        "{} is terrible. Please fix this.",
        "Disappointed by {}. Expected better.",
        "The {} situation is unacceptable."
    ]

    features = [
        'wifi', 'children\'s section', 'book selection',
        'opening hours', 'study spaces', 'computer access',
        'staff', 'events', 'facilities'
    ]

    issues = ['down', 'broken', 'unavailable', 'too limited', 'overcrowded']

    branches = [
        'Stratford', 'East Ham', 'Manor Park', 'Plaistow',
        'Custom House', 'North Woolwich', 'Beckton'
    ]

    feedback_lines = []
    feedback_lines.append("Member Feedback - Library Services")
    feedback_lines.append("=" * 50)
    feedback_lines.append("")

    for i in range(n):
        branch = random.choice(branches)

        if random.random() > 0.4:  # 60% positive
            rating = random.randint(4, 5)
            feedback = random.choice(positive_templates).format(random.choice(features))
        else:  # 40% negative
            rating = random.randint(1, 3)
            feedback = random.choice(negative_templates).format(
                random.choice(features),
                random.choice(issues) if '{}' in random.choice(negative_templates) else ''
            )

        feedback = maybe_add_typo(feedback)

        # random date within the last 2 months
        days_back = random.randint(0, 60)
        random_date = date.today() - timedelta(days=days_back)
        feedback_lines.append(f"Feedback #{i+1} - {random_date} - {branch} Branch ~ {rating}⭐")

        feedback_lines.append(feedback)
        feedback_lines.append("---")
        feedback_lines.append("")

    return '\n'.join(feedback_lines)

# ============================================
# 4. CATALOGUE DATA (Messy Excel)
# ============================================


def generate_catalogue_data(n, isbn_pool):
    """Generate book catalogue with Excel-specific issues.

    isbn_pool supplies one ISBN per row (catalogue is the source of ISBNs
    that circulation later draws from).
    """

    genres = ['Fiction', 'Non-Fiction', 'Children', 'Young Adult', 'Reference']

    data = []

    for i in range(n):
        record = {
            'ISBN': isbn_pool[i],
            'Title': fake.catch_phrase(),  # Not real book titles, but works for demo
            'Author': fake.name(),
            'Genre': random.choice(genres),
            'Publication Year': random.randint(1950, 2024),
            'Copies Available': random.randint(0, 10),
            'Acquisition Date': fake.date_between(start_date='-10y', end_date='today'),
            'Status': random.choice(['Available', 'Checked Out', 'Reserved', 'Damaged', 'Missing'])
        }

        data.append(record)

    df = pd.DataFrame(data)

    # INJECT EXCEL-SPECIFIC ISSUES

    # 1. Some ISBNs stored as numbers (Excel removes leading zeros)
    df['ISBN'] = df['ISBN'].astype(object)  # allow mixed str/int values below
    numeric_isbns = random.sample(range(len(df)), int(len(df) * 0.1))
    for idx in numeric_isbns:
        if df.loc[idx, 'ISBN']:
            df.loc[idx, 'ISBN'] = int(df.loc[idx, 'ISBN'].replace('-', ''))

    # 2. Inconsistent column names (spaces vs underscores)
    # Will handle this when writing to Excel with multiple sheets

    return df

# ============================================
# GENERATE ALL FILES
# ============================================


def generate_all_sample_data(output_dir='data'):
    """Generate all sample data files."""

    import os
    os.makedirs(output_dir, exist_ok=True)

    print("Generating sample data...")

    # Shared pool of check-digit-valid ISBN-13s - catalogue assigns one per
    # book, circulation samples from the same pool so the two can be joined
    # on ISBN after cleaning.
    isbn_pool = [fake.isbn13() for _ in range(CATALOGUE)]

    # 1. Circulation CSV
    print(f"  - Generating circulation_data.csv ({CIRCULATION} rows)...")
    circ_df = generate_circulation_data(CIRCULATION, isbn_pool)
    circ_df.to_csv(f'{output_dir}/circulation_data.csv', index=False)
    print(f"    ✓ Created: {len(circ_df)} rows")
    print("    - Duplicates: ~2%")
    print("    - Missing ISBNs: ~5%")
    print("    - Date format issues: ~10%")

    # 2. Events JSON
    print("  - Generating events_data.json...")
    events = generate_events_data(EVENTS)
    with open(f'{output_dir}/events_data.json', 'w') as f:
        json.dump(events, f, indent=2)
    print(f"    ✓ Created: {len(events)} events")

    # 3. Feedback text
    print("  - Generating feedback.txt...")
    feedback = generate_feedback_data(FEEDBACK)
    with open(f'{output_dir}/feedback.txt', 'w') as f:
        f.write(feedback)
    print(f"    ✓ Created: {FEEDBACK} feedback entries")
    print("    - Unstructured text format")

    # 4. Catalogue Excel
    print("  - Generating catalogue.xlsx...")
    catalogue_df = generate_catalogue_data(CATALOGUE, isbn_pool)

    # Create Excel with some messiness
    with pd.ExcelWriter(f'{output_dir}/catalogue.xlsx', engine='openpyxl') as writer:
        # Sheet 1: Main catalogue
        catalogue_df.to_excel(writer, sheet_name='Catalogue', index=False)

        # Sheet 2: Summary (extra sheet they don't need - like real Excel files!)
        summary = pd.DataFrame({
            'Total Books': [len(catalogue_df)],
            'Genres': [len(catalogue_df['Genre'].unique())],
            'Available': [len(catalogue_df[catalogue_df['Status'] == 'Available'])]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)

    print(f"    ✓ Created: {len(catalogue_df)} books")
    print("    - Multiple sheets")
    print("    - ISBN format issues")

    print("\n✅ All sample data generated successfully!")
    print(f"\nFiles created in '{output_dir}/':")
    print("  - circulation_data.csv (messy CSV)")
    print("  - events_data.json (flat JSON array)")
    print("  - feedback.txt (unstructured text)")
    print("  - catalogue.xlsx (messy Excel)")

    # Generate data quality report
    print("\n" + "="*60)
    print("DATA QUALITY ISSUES INJECTED:")
    print("="*60)
    print("\ncirculation_data.csv:")
    print(f"  ~{int(CIRCULATION*0.02)} duplicate rows (~2%)")
    print(f"  ~{int(CIRCULATION*0.04)} missing ISBNs (~4%)")
    print(f"  ~{int(CIRCULATION*0.02)} missing member_ids (~2%)")
    print(f"  ~{int(CIRCULATION*0.10)} mixed date formats (~10%)")
    print(f"  ~{int(CIRCULATION*0.03)} whitespace issues in branch_id (~3%)")

    print("\nevents_data.json:")
    print("  ⚠️  Branch names don't match branch_id format")
    print(f"  ~{int(EVENTS*0.10)} missing feedback_scores (~10%)")

    print("\nfeedback.txt:")
    print("  ⚠️  Completely unstructured")
    print("  ⚠️  Requires parsing and sentiment analysis (optional)")

    print("\ncatalogue.xlsx:")
    print(f"  ~{int(CATALOGUE*0.10)} ISBNs stored as numbers (~10%)")
    print("  ⚠️  Multiple sheets (only need 'Catalogue')")
    print("  ⚠️  Mixed data types in ISBN column")


if __name__ == '__main__':
    generate_all_sample_data()
