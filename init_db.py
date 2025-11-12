import sqlite3

DB = 'uam.db'

schema = """
CREATE TABLE IF NOT EXISTS users(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  fullname TEXT
);

CREATE TABLE IF NOT EXISTS schedules(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  day_of_week INTEGER NOT NULL,
  start_time TEXT NOT NULL,
  end_time TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS access_logs(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  timestamp TEXT NOT NULL,
  action TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
"""

def main():
    conn = sqlite3.connect(DB)
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    main()
