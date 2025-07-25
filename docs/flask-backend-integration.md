# 3️⃣ Flask Backend Integration

In `server.py`, connect to your SQLite database:

```python
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

DB_PATH = os.getenv('SQLITE_DB_PATH', 'petclinic.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # So you can access columns by name
    return conn
```

Replace all JSON file operations with SQL queries using the connection above. 