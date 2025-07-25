# 4️⃣ Update Your Flask API Endpoints

Refactor endpoints (e.g., `/login`, `/register`, `/appointments`, `/chat`) to use SQLite queries.
Use `with get_db_connection() as conn:` to open a connection for each request.

**Remember:**
- Use `conn.commit()` after `INSERT`, `UPDATE`, or `DELETE`.
- Use `conn.execute()` or `conn.executemany()` for SQL queries.

## Example: Register User

```python
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    with get_db_connection() as conn:
        try:
            conn.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (data['username'], data['email'], data['password'])
            )
            conn.commit()
            return jsonify({'success': True}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username or email already exists'}), 400
```

Test endpoints with Postman or your frontend. 