"""Load the model into SQLite, run the SQL reports, and write them to reports/."""
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent
TABLES = ["companies", "ledger_accounts", "cost_centers", "projects", "funds", "assets", "fx_rates", "hierarchy", "journal_lines"]
NUMERIC = {"requires_fund", "cost_local", "life_months", "debit_local", "credit_local", "rate_to_aud", "requires_cost_center", "requires_project", "is_intercompany"}


def load(con):
    for t in TABLES:
        with open(ROOT / "data" / f"{t}.csv", newline="") as f:
            rows = list(csv.DictReader(f))
        cols = list(rows[0].keys())
        con.execute(f"CREATE TABLE {t} ({', '.join(c + (' REAL' if c in NUMERIC else '') for c in cols)})")
        con.executemany(f"INSERT INTO {t} VALUES ({','.join('?' * len(cols))})",
                        [[(float(r[c]) if c in NUMERIC else r[c]) for c in cols] for r in rows])


def main():
    con = sqlite3.connect(":memory:")
    load(con)
    con.executescript((ROOT / "sql" / "00_views.sql").read_text())
    (ROOT / "reports").mkdir(exist_ok=True)
    for sql in sorted((ROOT / "sql").glob("0[1-9]_*.sql")):
        cur = con.execute(sql.read_text())
        headers = [d[0] for d in cur.description]
        rows = cur.fetchall()
        out = ROOT / "reports" / f"{sql.stem}.csv"
        with open(out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(headers)
            w.writerows(rows)
        print(f"{out.relative_to(ROOT)}: {len(rows)} rows")


if __name__ == "__main__":
    main()
