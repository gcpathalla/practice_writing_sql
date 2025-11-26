# CSV to SQLite Database Generator

A Python tool to automatically generate SQLite databases from CSV files with cleaned, standardized column names.

## Features

- ✅ **Automatic column name cleaning**: Converts all column names to lowercase, replaces spaces and special characters with underscores
- ✅ **Handles all special characters**: Parentheses, brackets, quotes, hyphens, slashes, dots, commas, etc.
- ✅ **Smart encoding detection**: Tries multiple encodings (UTF-8, Latin1, ISO-8859-1, CP1252)
- ✅ **Automatic indexing**: Suggests and creates indexes on appropriate columns
- ✅ **Config file support**: Process multiple CSV files with a single command
- ✅ **Duplicate column handling**: Automatically renames duplicate columns with suffixes

## Column Cleaning Rules

The script automatically cleans column names using these rules:

| Original | Cleaned | Rule |
|----------|---------|------|
| `Order ID` | `order_id` | Spaces → underscore, lowercase |
| `Sub-Category` | `sub_category` | Hyphens → underscore |
| `Sales (USD)` | `sales_usd` | Parentheses removed |
| `Start/End Date` | `start_end_date` | Slashes → underscore |
| `Amount.Total` | `amount_total` | Dots → underscore |
| `"Product Name"` | `product_name` | Quotes removed |
| `Region  [US]` | `region_us` | Multiple special chars → single underscore |
| `123_count` | `c_123_count` | Prefix 'c_' if starts with digit |
| Duplicate `name` | `name`, `name_2`, `name_3` | Auto-suffix for duplicates |

## Installation

1. **Install Python dependencies**:
   ```bash
   cd generate_db_from_dataset
   pip install -r requirements.txt
   ```

2. **Verify installation**:
   ```bash
   python db_generator.py --help
   ```

## Usage

### Method 1: Using Config File (Recommended)

This is the easiest way to process multiple CSV files at once.

1. **Edit `config.yaml`** to specify your CSV files and database locations:

   ```yaml
   databases:
     - csv: ../datasets/your_data.csv
       db: ../databases/your_database.db
       table: your_table_name
       # Optional: index_columns: [column1, column2]
   ```

2. **Run the generator**:
   ```bash
   python db_generator.py --config config.yaml
   ```

### Method 2: Direct CSV Processing

Process a single CSV file directly:

```bash
python db_generator.py --csv ../datasets/data.csv --db ../databases/mydata.db --table mytable
```

## Adding New Datasets

To create a database from a new CSV file:

1. **Place your CSV file** in the `datasets/` folder:
   ```
   datasets/
   ├── Sample - Superstore.csv
   ├── HRDataset_v14.csv
   └── your_new_data.csv          ← Add here
   ```

2. **Add entry to `config.yaml`**:
   ```yaml
   databases:
     # ... existing entries ...

     # Your new dataset
     - csv: ../datasets/your_new_data.csv
       db: ../databases/your_new_data.db
       table: your_table_name
   ```

3. **Run the generator**:
   ```bash
   python db_generator.py --config config.yaml
   ```

4. **Your database will be created** in the `databases/` folder with cleaned column names!

## Output

The script will show:
- ✅ Progress for each database being created
- ✅ Cleaned column names and their data types
- ✅ Number of rows inserted
- ✅ Indexes created
- ✅ Sample rows from the data
- ✅ Summary of successes and failures

Example output:
```
================================================================================
Processing database 1/2
================================================================================
Written table 'superstore' to database: /path/to/databases/superstore.db
Rows inserted: 9,994
Columns:
  - row_id  (dtype: int64)
  - order_id  (dtype: object)
  - order_date  (dtype: object)
  - customer_id  (dtype: object)
  - sales  (dtype: float64)
  ...
Indexes created on columns: ['customer_id', 'region', 'category']
```

## Directory Structure

```
practice_writing_sql/
├── datasets/                    # Place your CSV files here
│   ├── Sample - Superstore.csv
│   └── HRDataset_v14.csv
├── databases/                   # Generated SQLite databases
│   ├── superstore.db
│   └── hr_data.db
└── generate_db_from_dataset/    # Generator scripts
    ├── db_generator.py
    ├── config.yaml
    ├── requirements.txt
    └── README.md
```

## Advanced Options

### Manual Index Specification

By default, the script automatically suggests indexes. To manually specify:

```yaml
databases:
  - csv: ../datasets/data.csv
    db: ../databases/data.db
    table: mytable
    index_columns: [customer_id, date, region]  # Manual indexes
```

### Custom Encodings

The script tries these encodings automatically:
1. UTF-8
2. Latin1
3. ISO-8859-1
4. CP1252

If your CSV uses a different encoding, you can modify the `encodings` parameter in the script.

## Troubleshooting

**Problem**: "CSV file not found"
- **Solution**: Check that the CSV path in config.yaml is correct (relative to config file or absolute path)

**Problem**: "Failed to read CSV"
- **Solution**: The script tries multiple encodings. Check your CSV file for corruption or unusual encoding

**Problem**: No indexes created
- **Solution**: This is normal for small datasets or datasets without categorical columns. You can manually specify indexes.

**Problem**: Column names still look wrong
- **Solution**: The cleaning is automatic. If you need custom rules, modify the `_clean_column_name()` function.

## Examples

### Example 1: Single CSV
```bash
python db_generator.py --csv ../datasets/sales.csv --db ../databases/sales.db --table sales_data
```

### Example 2: Multiple CSVs via config
```bash
python db_generator.py --config config.yaml
```

### Example 3: Get help
```bash
python db_generator.py --help
```

## Notes

- Original CSV files are never modified - they remain in the `datasets/` folder
- Generated databases are placed in the `databases/` folder
- Column cleaning is automatic and comprehensive
- The script is safe to run multiple times (overwrites existing databases by default)
