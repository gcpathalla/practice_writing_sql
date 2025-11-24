import sqlite3
import pandas as pd
import os
import re
from pathlib import Path
from typing import Optional, List

def _clean_column_name(col: str) -> str:
    """Clean a single column name: strip, lower, replace non-alnum with underscore, collapse underscores."""
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


if __name__ == "__main__":
    # Example usage for your two CSVs (paths can be relative or absolute)
    try:
        create_db_from_csv("Sample - Superstore.csv")      # will create Sample_-_Superstore.db and table name 'sample_superstore'
    except Exception as e:
        print("Superstore import error:", e)

    try:
        create_db_from_csv("HRDataset_v14.csv")            # will create HRDataset_v14.db
    except Exception as e:
        print("HR import error:", e)
