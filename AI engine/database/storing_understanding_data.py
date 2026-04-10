import sqlite3

conn = sqlite3.connect("understanding_problem.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    correct_explanation TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY,
    problem_id INTEGER,
    user_explanation TEXT,
    model_result TEXT,
    feedback TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()