#!/usr/bin/env python3
# access_checker.py
# Only check users who have schedules for the current weekday.
# This prevents users with no schedules today from being logged.

import sqlite3
import datetime
import os

DB = 'uam.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def is_within(start, end, current):
    # Compare "HH:MM" strings (no overnight handling)
    return start <= current <= end

def log_action(conn, user_id, action):
    timestamp = datetime.datetime.now().isoformat(timespec='seconds')
    conn.execute(
        "INSERT INTO access_logs(user_id, timestamp, action) VALUES (?, ?, ?)",
        (user_id, timestamp, action)
    )

def main():
    now = datetime.datetime.now()
    current_day = now.weekday()        # 0=Mon .. 6=Sun
    current_time = now.strftime("%H:%M")

    if not os.path.exists(DB):
        print("Database not found. Run init_db.py first.")
        return

    conn = get_db()

    # Get distinct user_ids that have schedules for today
    rows = conn.execute(
        "SELECT DISTINCT user_id FROM schedules WHERE day_of_week=?",
        (current_day,)
    ).fetchall()

    if not rows:
        print("No schedules for today found. Nothing to check.")
        conn.close()
        return

    user_ids = [r["user_id"] for r in rows]

    for uid in user_ids:
        # Get username
        user = conn.execute("SELECT username FROM users WHERE id=?", (uid,)).fetchone()
        username = user["username"] if user else f"user_{uid}"

        # Get today's schedules for this user
        schedules = conn.execute(
            "SELECT * FROM schedules WHERE user_id=? AND day_of_week=?",
            (uid, current_day)
        ).fetchall()
        if not schedules:
            continue

        # Check if any schedule allows the current time
        allowed = any(is_within(s["start_time"], s["end_time"], current_time) for s in schedules)
        action = "ALLOWED" if allowed else "DENIED"

        # Log and print only for users who have schedules for today
        log_action(conn, uid, action)
        print(f"{username}: {action} at {current_time}")

    conn.commit()
    conn.close()
    print("✅ Check completed and logs updated.")

if __name__ == "__main__":
    main()
