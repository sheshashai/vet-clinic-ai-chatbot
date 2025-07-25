# 1️⃣ Database Setup: SQLite Integration

No installation needed — SQLite comes with Python’s standard library (`sqlite3`).

## Create the Database File
- The database file (e.g., `petclinic.db`) is created automatically the first time you connect.

## Create Tables
Here’s an initial schema for users and appointments:

```sql
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS appointments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  pet_name TEXT NOT NULL,
  phone TEXT,
  date TEXT NOT NULL,   -- Store dates as ISO strings for SQLite
  time TEXT NOT NULL,
  service TEXT DEFAULT 'General Consultation',
  notes TEXT,
  status TEXT DEFAULT 'scheduled',
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
```

> (Optional) Add initial test data to your tables as needed. 

---

## How to Debug This

### 1. **Check Your Flask Server Terminal**
- Look at the terminal where your Flask server is running.
- You should see a traceback or error message when you run the test.
- **Copy and paste the full error message here**—it will tell us exactly what went wrong.

---

### 2. **Improve the Test Script for Debugging**
To help debug, you can modify your test script to print the raw response text if JSON decoding fails.  
Replace this in `test_flask_api.py`:

```python
try:
    print('Response:', resp.json())
except Exception:
    print('Raw response:', resp.text)
```

---

### 3. **Common Causes for 500 Errors on Registration**
- The `users` table might not exist or is missing a column.
- The database file is not writable.
- There is a bug in the SQL or Python code.

---

## **Next Steps**
1. **Check your Flask server terminal for the error traceback and share it here.**
2. (Optional) Update your test script as above to see the raw error response.
3. Let me know what you find, and I’ll help you fix the backend error!

Would you like me to update the test script for better error output? 