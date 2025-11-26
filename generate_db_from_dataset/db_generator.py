import sqlite3
import pandas as pd
import os
import re
import argparse
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any

def _clean_column_name(col: str) -> str:
    """
    Clean a single column name: strip, lower, replace non-alnum with underscore, collapse underscores.

    Handles all special characters including:
    - Spaces → underscore
    - Hyphens/dashes → underscore
    - Parentheses, brackets → removed
    - Slashes, dots, commas → underscore
    - Quotes, percent, dollar, hash, ampersand, etc. → underscore
    - Multiple consecutive special chars → single underscore
    - Leading/trailing underscores → removed
    """
    col = str(col).strip().lower()
    # replace any sequence of non-alphanumeric characters with underscore
    col = re.sub(r'[^0-9a-z]+', '_', col)
    # remove leading/trailing underscores
    col = col.strip('_')
    # if it starts with a digit, prefix with 'c_'
    if re.match(r'^\d', col):
        col = 'c_' + col
    # ensure not empty
    return col or 'col'

def _make_unique_columns(cols: List[str]) -> List[str]:
    """Ensure column names are unique by appending suffixes."""
    seen = {}
    new_cols = []
    for c in cols:
        base = c
        if base in seen:
            seen[base] += 1
            c = f"{base}_{seen[base]}"
        else:
            seen[base] = 0
        new_cols.append(c)
    return new_cols

def _suggest_index_columns(df: pd.DataFrame, max_unique_ratio: float = 0.05, max_indexes: int = 5) -> List[str]:
    """
    Heuristic: return columns to index.
    - Prefer columns with low cardinality (categorical-like) or columns containing 'id'/'date'/'region'/'category'
    - Limit to max_indexes.
    """
    candidates = []
    for col in df.columns:
        ser = df[col]
        # skip entirely numeric with many unique values
        try:
            nunique = ser.nunique(dropna=True)
            ratio = nunique / max(1, len(ser))
        except Exception:
            nunique, ratio = 999999, 1.0

        lname = col.lower()
        score = 0
        if 'id' in lname and len(lname) <= 10:
            score += 4
        if any(k in lname for k in ('date', 'timestamp', 'time')):
            score += 3
        if any(k in lname for k in ('region', 'state', 'city', 'category', 'segment')):
            score += 2
        # lower cardinality gives better score
        if ratio < max_unique_ratio:
            score += 2
        elif ratio < (max_unique_ratio * 2):
            score += 1

        if score > 0:
            candidates.append((score, ratio, col))

    # sort by (score desc, ratio asc) so good categorical columns first
    candidates.sort(key=lambda x: (-x[0], x[1]))
    # return top column names up to max_indexes
    return [c for _, _, c in candidates[:max_indexes]]

def create_db_from_csv(csv_path: str,
                       db_path: Optional[str] = None,
                       table_name: Optional[str] = None,
                       index_columns: Optional[List[str]] = None,
                       encodings: Optional[List[str]] = None,
                       if_exists: str = 'replace'):
    """
    Read csv_path and write to SQLite DB (db_path). All column names are cleaned (lowercase,
    non-alnum -> underscore, deduplicated). The function will try multiple encodings if needed.

    Parameters:
      - csv_path: path to CSV file
      - db_path: path to sqlite DB file. If None, placed beside CSV with .db extension.
      - table_name: table name to use. If None, derived from CSV filename (safe cleaned).
      - index_columns: list of columns to create indexes on. If None, they are suggested automatically.
      - encodings: list of encodings to attempt (defaults provided).
      - if_exists: 'replace' (default) or 'append' etc passed to pandas.to_sql.
    """

    if encodings is None:
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']

    csv_path = str(csv_path)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Determine db_path
    if db_path is None:
        p = Path(csv_path)
        db_path = str(p.with_suffix('.db'))

    # Derive default table name from CSV filename if not provided
    if table_name is None:
        stem = Path(csv_path).stem
        table_name = re.sub(r'[^0-9a-zA-Z]+', '_', stem).lower().strip('_')
        if not table_name:
            table_name = 'table_data'

    # Attempt to read CSV with multiple encodings
    df = None
    last_exception = None
    for enc in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=enc)
            # success
            break
        except Exception as e:
            last_exception = e
            # try next
    if df is None:
        # final attempt letting pandas guess with engine='python'
        try:
            df = pd.read_csv(csv_path, engine='python')
        except Exception as e:
            raise Exception(f"Failed to read CSV {csv_path}. Last error: {last_exception!r}; final attempt error: {e!r}")

    # Clean column names
    cleaned = [_clean_column_name(c) for c in df.columns]
    cleaned = _make_unique_columns(cleaned)
    df.columns = cleaned

    # Basic type inference: try to parse datetime-like columns (columns that contain 'date' or 'time')
    # but do not coerce too aggressively.
    for col in df.columns:
        if re.search(r'date|time|timestamp', col, flags=re.I):
            try:
                df[col] = pd.to_datetime(df[col], errors='ignore', infer_datetime_format=True)
            except Exception:
                # leave as-is on failure
                pass

    # Connect and write to sqlite
    conn = sqlite3.connect(db_path)
    try:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        # Determine index columns if not provided
        if index_columns is None:
            suggested = _suggest_index_columns(df)
            index_columns = suggested
        # Create indexes (if any)
        cursor = conn.cursor()
        for col in index_columns or []:
            # Only create index if column exists
            if col in df.columns:
                # sanitize index name
                idx_name = f"idx_{table_name}_{col}"
                sql = f'CREATE INDEX IF NOT EXISTS "{idx_name}" ON "{table_name}" ("{col}");'
                try:
                    cursor.execute(sql)
                except Exception:
                    # ignore index creation errors but continue
                    pass
        conn.commit()

        # Print summary
        print(f"Written table '{table_name}' to database: {os.path.abspath(db_path)}")
        print(f"Rows inserted: {len(df):,}")
        print("Columns:")
        for c in df.columns:
            print(f"  - {c}  (dtype: {df[c].dtype})")
        if index_columns:
            print("Indexes created on columns:", index_columns)
        else:
            print("No indexes created (no suggestions).")

        # show a tiny sample
        print("\nSample rows:")
        print(df.head(3).to_string(index=False))
    finally:
        conn.close()


def process_config_file(config_path: str):
    """
    Process a YAML config file containing database generation specifications.

    Config format:
    databases:
      - csv: path/to/file.csv
        db: path/to/output.db
        table: table_name
        index_columns: [col1, col2]  # optional
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    if 'databases' not in config:
        raise ValueError("Config file must contain 'databases' key")

    databases = config['databases']
    if not isinstance(databases, list):
        raise ValueError("'databases' must be a list")

    success_count = 0
    error_count = 0

    for idx, db_config in enumerate(databases):
        print(f"\n{'='*80}")
        print(f"Processing database {idx + 1}/{len(databases)}")
        print(f"{'='*80}")

        try:
            csv_path = db_config.get('csv')
            db_path = db_config.get('db')
            table_name = db_config.get('table')
            index_columns = db_config.get('index_columns')

            if not csv_path:
                raise ValueError(f"Config entry {idx + 1} missing 'csv' field")

            # Create db directory if it doesn't exist
            if db_path:
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir)
                    print(f"Created directory: {db_dir}")

            create_db_from_csv(
                csv_path=csv_path,
                db_path=db_path,
                table_name=table_name,
                index_columns=index_columns
            )
            success_count += 1

        except Exception as e:
            print(f"ERROR processing config entry {idx + 1}: {e}")
            error_count += 1

    print(f"\n{'='*80}")
    print(f"Summary: {success_count} successful, {error_count} failed")
    print(f"{'='*80}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate SQLite databases from CSV files with cleaned column names",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using config file (recommended):
  python db_generator.py --config config.yaml

  # Direct CSV processing:
  python db_generator.py --csv datasets/data.csv --db databases/mydata.db --table mytable

Note: When using config file, all CSV paths are relative to the config file location,
      or you can use absolute paths.
        """
    )

    parser.add_argument('--config', '-c', type=str,
                        help='Path to YAML config file')
    parser.add_argument('--csv', type=str,
                        help='Path to CSV file (for direct processing)')
    parser.add_argument('--db', type=str,
                        help='Path to output database file')
    parser.add_argument('--table', type=str,
                        help='Table name in the database')

    args = parser.parse_args()

    if args.config:
        # Process config file
        process_config_file(args.config)
    elif args.csv:
        # Direct CSV processing
        create_db_from_csv(
            csv_path=args.csv,
            db_path=args.db,
            table_name=args.table
        )
    else:
        parser.print_help()
        print("\nERROR: You must specify either --config or --csv")
        exit(1)
