import sqlite3

DB_PATH = "request_log.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS request_count (
            company TEXT PRIMARY KEY,
            count INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def log_request(company: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Versuche die Firma zu aktualisieren (Zähler +1)
    cursor.execute("SELECT count FROM request_count WHERE company = ?", (company,))
    row = cursor.fetchone()

    if row:
        new_count = row[0] + 1
    else:
        new_count = 1
    cursor.execute("INSERT INTO request_count (count, company) VALUES (?, ?)", (new_count, company))

    conn.commit()
    conn.close()
    return new_count
