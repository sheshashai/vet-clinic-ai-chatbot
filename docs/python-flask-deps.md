# 2️⃣ Python & Flask Dependencies

No extra dependency needed! SQLite is supported natively in Python.

## requirements.txt
Add the following to your `requirements.txt`:

```
flask
python-dotenv
# sqlite3 is built-in, so nothing extra here!
```

## .env (Optional but Recommended)
Add your database path to your `.env` file:

```
SQLITE_DB_PATH=petclinic.db
``` 