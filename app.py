# app.py
from flask import Flask, request, redirect, url_for, render_template
import sqlite3, datetime, os

DB = 'uam.db'
app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db()
    users = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    schedules = conn.execute(
        "SELECT s.*, u.username FROM schedules s JOIN users u ON s.user_id=u.id ORDER BY s.id"
    ).fetchall()
    logs = conn.execute(
        "SELECT l.*, u.username FROM access_logs l JOIN users u ON l.user_id=u.id ORDER BY l.id DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return render_template('index.html', users=users, schedules=schedules, logs=logs)

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username'].strip()
    fullname = request.form.get('fullname','').strip()
    if not username:
        return "username required", 400
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO users(username, fullname) VALUES (?,?)", (username, fullname))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/add_schedule', methods=['POST'])
def add_schedule():
    user_id = int(request.form['user_id'])
    day = int(request.form['day_of_week'])
    start = request.form['start_time']
    end = request.form['end_time']
    conn = get_db()
    conn.execute("INSERT INTO schedules(user_id, day_of_week, start_time, end_time) VALUES (?,?,?,?)",
                 (user_id, day, start, end))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    conn = get_db()
    conn.execute("DELETE FROM access_logs")
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # create DB if missing
    if not os.path.exists(DB):
        import init_db
        init_db.main()
    app.run(host='0.0.0.0', port=5000, debug=True)
