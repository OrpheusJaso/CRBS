"""Throwaway helper: print the contents of crbs.db so you can see the data."""
import sqlite3

con = sqlite3.connect("crbs.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

tables = [r[0] for r in cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
print("TABLES IN crbs.db:", tables)
print()

for t in ["user", "resource", "booking"]:
    rows = cur.execute(f"SELECT * FROM {t}").fetchall()
    print(f"=== {t}  ({len(rows)} rows) ===")
    if rows:
        print("columns:", list(rows[0].keys()))
    for row in rows[:4]:
        print("  ", tuple(row))
    print()

con.close()
