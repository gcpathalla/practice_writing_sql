# SQL Browser — Practice & Learn SQL

A powerful, no-setup SQL learning tool that runs entirely in your browser. Write, execute, and master SQL queries with built-in databases and an intuitive editor.

## ✨ Features

- **No Backend Required** — Completely client-side, no server needed
- **SQL Execution in Browser** — Run queries instantly using sql.js
- **Multiple Databases** — Load and switch between multiple SQLite databases
- **Syntax Highlighting** — Professional code editor with SQL support (CodeMirror)
- **Query Formatting** — Auto-format your SQL with one click
- **Tab-Based Queries** — Manage multiple queries in separate tabs
- **Save & Load Queries** — Persist your queries locally in browser storage
- **Results Export** — Copy results to clipboard or download as files
- **Dark & Light Modes** — Beautiful themes inspired by Claude Desktop
- **Responsive Design** — Works on desktop and tablet
- **Pre-Loaded Databases** — Includes sample databases for learning

## 🚀 Quick Start

### Opening the Application

1. **Open `SQL_Editor.html` in your browser** — Just double-click the file or open it with any modern browser
2. **Wait for loading** — The application initializes sql.js (takes a few seconds)
3. **Start using it** — No installation, no dependencies needed!

### Loading Databases

#### Option 1: Use Pre-Loaded Sample Databases
The application automatically loads sample databases from the `/databases/` folder:
- **ecommerce.db** — E-commerce sample with products, orders, customers
- **superstore.db** — Superstore sales data for analysis
- **hr_database.db** — Human Resources department data
- **company.db** — Company structure and departments
- **school.db** — School management data

#### Option 2: Load Your Own Databases
- Click **"Load databases"** button in the sidebar
- Select `.db`, `.sqlite`, or `.sqlite3` files from your computer
- Files are automatically added to the available databases list

## 📚 Usage Guide

### Writing Queries

1. **Select a Database** — Choose from the dropdown or click a database in the sidebar
2. **Write SQL** — Type your query in the editor area
3. **Execute** — Click **"Run"** or press `Ctrl+Enter` (or `Cmd+Enter` on Mac)
4. **View Results** — Results appear in the table below the editor

### Query Management

- **New Tab** — Click **"+ New query"** to create another query tab
- **Rename Tab** — Double-click a tab title to rename it
- **Close Tab** — Click the ✕ on a tab to close it
- **Run Selected** — If you have text selected, only that text runs
- **Run Current Statement** — Without selection, runs the statement at your cursor

### Save & Load Queries

- **Save Query** — Click **"Save"** to save the current query locally
- **Save All** — Save all open queries at once
- **Open Saved** — Click **"Open saved"** to view and restore saved queries
- **Download** — Export a query as a `.sql` file

### Results Management

- **Copy Results** — Copy all results to clipboard as tab-separated values
- **Adjust Display** — Set "Max chars/cell" to truncate long values
- **Row Limits** — Set "Default max rows" to limit results per query
- **Download Query** — Save your query as a `.sql` file for later use

### Formatting & Tools

- **Format Query** — Click **"Format"** or press `Shift+Alt+F` to auto-format SQL
- **Clear Query** — Remove all text and results from current tab
- **Expand Columns** — Enable "Expand columns in SELECT" to auto-expand column lists

## 🎨 Theme Modes

### Dark Mode (Default)
Professional dark theme inspired by Claude Desktop, perfect for extended work sessions:
- Deep background colors to reduce eye strain
- High contrast text for readability
- Syntax highlighting optimized for dark backgrounds

### Light Mode
Clean, bright theme for daytime use:
- Light backgrounds for natural reading experience
- Dark text with perfect contrast
- Easy on the eyes in bright environments

**Switch Themes** — Click the theme toggle button in the top-right corner

## 🛠️ Sample Queries

### E-Commerce Database
```sql
-- Top 10 products by sales
SELECT product_id, product_name, SUM(quantity) as total_sold
FROM orders
GROUP BY product_id
ORDER BY total_sold DESC
LIMIT 10;
```

### Superstore Data
```sql
-- Regional sales summary
SELECT Region, SUM(Sales) as total_sales, COUNT(*) as transactions
FROM Sales
GROUP BY Region
ORDER BY total_sales DESC;
```

### HR Database
```sql
-- Employees by department
SELECT Department, COUNT(*) as count, AVG(Salary) as avg_salary
FROM Employees
GROUP BY Department
ORDER BY count DESC;
```

## 📊 Database Contents

### Provided Sample Databases

#### ecommerce.db
- **products** — Product catalog
- **orders** — Order records
- **order_items** — Items per order
- **customers** — Customer information

#### superstore.db
- **Sales** — Sales transactions and metrics

#### hr_database.db
- **Employees** — Employee records with salary info
- **Departments** — Department structure

#### company.db
- **Company structure** — Organizational hierarchy

#### school.db
- **Students** — Student records
- **Classes** — Course information
- **Enrollment** — Student-course mappings

## 🎯 Tips & Tricks

- **Keyboard Shortcuts**
  - `Ctrl+Enter` / `Cmd+Enter` — Execute query
  - `Shift+Alt+F` — Format query
  - `Ctrl+/` — Toggle line comment
  - Double-click tab — Rename query

- **Pro Tips**
  - Use comments to organize long queries (`-- comment here`)
  - Save frequently used queries for quick access
  - The dirty indicator (white dot) shows unsaved changes
  - Results are cached per tab, switching tabs preserves results
  - Maximum query size is limited by browser memory

- **Performance**
  - Large result sets may slow down rendering
  - Use `LIMIT` clauses to restrict result rows
  - Adjust "Max chars/cell" to improve display performance

## 📁 Project Structure

```
practice_writing_sql/
├── SQL_Editor.html              # Main application (all-in-one)
├── README.md                    # This file
├── databases/
│   ├── ecommerce.db
│   ├── superstore.db
│   ├── hr_database.db
│   ├── company.db
│   └── school.db
├── datasets/
│   ├── HRDataset_v14.csv
│   └── Sample - Superstore.csv
└── generate_db_from_dataset/
    └── db_generator.py          # Python utility for CSV → SQLite conversion
```

## 🔧 Creating Databases from CSV

The included `db_generator.py` script converts CSV files to SQLite databases:

```bash
python generate_db_from_dataset/db_generator.py <input.csv> <output.db>
```

**Features:**
- Auto-detects data types
- Handles multiple character encodings
- Creates intelligent indexes
- Parses dates automatically
- Cleans and normalizes column names

## 🔐 Data & Privacy

- **Completely Offline** — All processing happens in your browser
- **No Network Calls** — Queries never leave your machine
- **No Data Collection** — We don't track or store anything
- **Browser Storage** — Saved queries are stored locally in your browser (LocalStorage)
- **Read-Only Tables** — Pre-loaded databases are protected from modifications

## 💻 Technical Stack

- **Frontend**
  - HTML5, CSS3, JavaScript (ES6+)
  - [CodeMirror 5.65.2](https://codemirror.net/) — Code editor
  - [sql.js 1.8.0](https://sql.js.org/) — SQLite in browser
  - [sql-formatter 4.0.2](https://github.com/sql-formatter-org/sql-formatter) — Query formatting
  - [Font Awesome 6.0.0](https://fontawesome.com/) — Icons

- **Databases**
  - SQLite (via sql.js in-browser)

- **Tools**
  - Python 3 (for database generation)
  - Pandas (for data processing)

## 🌐 Browser Support

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 📝 Learning Path

### Beginner
1. Load the **ecommerce.db** database
2. Run: `SELECT * FROM products LIMIT 5;`
3. Explore: `SELECT * FROM customers;`
4. Practice: Filter results with `WHERE` clauses

### Intermediate
1. Try `JOIN` operations: Combine products and orders
2. Use `GROUP BY` for aggregations
3. Practice `ORDER BY` and `LIMIT`
4. Save your queries for reference

### Advanced
1. Window functions and CTEs
2. Complex joins and subqueries
3. Performance optimization with indexes
4. Data analysis and reporting queries

## 🐛 Troubleshooting

### Application won't load
- **Solution:** Clear browser cache and refresh the page
- Check browser console for errors (F12)

### Databases not loading
- **Solution:** Try manually clicking "Load databases"
- Ensure files are valid SQLite 3 format

### Query errors
- **Solution:** Check SQL syntax in the error message
- Verify table and column names (SQL is case-sensitive)
- Use the Format button to check syntax

### Performance issues
- **Solution:** Reduce LIMIT values in queries
- Disable "Expand columns" if slow
- Reduce "Max chars/cell" value

## 📞 Support

For issues or feature requests:
1. Check that your browser is up-to-date
2. Clear browser cache and LocalStorage if needed
3. Try a different browser to isolate issues
4. Review error messages in browser console (F12)

## 📄 License

This project is provided for learning and practice purposes.

## 🎓 Educational Use

Perfect for:
- SQL courses and bootcamps
- Database learning and practice
- Teaching SQL fundamentals
- Interview preparation
- Data analysis practice

---

**Happy Learning!** Start writing SQL queries and explore the power of database queries. 🚀
