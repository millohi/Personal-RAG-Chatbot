import shutil
import datetime
import sqlite3
import os

DB_PATH = ""

def init_db(db_path="request_log.db"):
    global DB_PATH
    if os.path.dirname(db_path) != "" and not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
    elif os.path.exists(db_path):
        shutil.move(db_path, db_path+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+".archiv")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS request_count (
            company TEXT PRIMARY KEY,
            count INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    DB_PATH = db_path

def log_request(company: str) -> int:
    if not os.path.exists(DB_PATH):
        return 0
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Versuche die Firma zu aktualisieren (Zähler +1)
    cursor.execute("SELECT count FROM request_count WHERE company = ?", (company,))
    row = cursor.fetchone()

    if row:
        new_count = row[0] + 1
        cursor.execute("UPDATE request_count SET count = ? WHERE company = ?", (new_count, company))
    else:
        new_count = 1
        cursor.execute("INSERT INTO request_count (company, count) VALUES (?, ?)", (company, new_count))

    conn.commit()
    conn.close()
    return new_count
