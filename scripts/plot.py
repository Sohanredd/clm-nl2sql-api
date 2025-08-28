# scripts/plot.py
import duckdb, pathlib
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB   = ROOT / "db" / "fclm.duckdb"
OUT  = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(DB.as_posix())

def cols(table):
    """Return list of column names for a table."""
    return [r[1] for r in con.execute(f"PRAGMA table_info('{table}')").fetchall()]

def find_col(table, *candidates):
    """
    Return the FIRST matching column (case-insensitive, substring ok).
    Examples: find_col('orders', 'status', 'result'), find_col('t', 'datetime','timestamp','date')
    """
    name_map = {c.lower(): c for c in cols(table)}
    # exact (case-insensitive)
    for cand in candidates:
        lc = cand.lower()
        if lc in name_map:
            return name_map[lc]
    # substring contains
    for cand in candidates:
        lc = cand.lower()
        for k, original in name_map.items():
            if lc in k:
                return original
    return None

tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
print("Tables:", tables)

# -----------------------------
# 1) STATUS COUNTS per table
# -----------------------------
for t in tables:
    status_col = find_col(t, "status", "defect_type", "remarks", "result", "outcome")
    if not status_col:
        continue
    df = con.execute(f"""
        SELECT {status_col} AS status, COUNT(*) AS n
        FROM {t}
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 15
    """).fetchdf()
    if df.empty:
        continue
    ax = df.plot(kind="bar", x="status", y="n", title=f"{t}: counts by {status_col}")
    plt.tight_layout()
    plt.savefig(OUT / f"{t}_status_counts.png")
    plt.clf()
    print(f"📸 saved {t}_status_counts.png")

# ------------------------------------------
# 2) FAILURES by Machine/Tool (if available)
# ------------------------------------------
failure_keywords = ("fail", "rework", "leak", "reject", "error")
for t in tables:
    status_col  = find_col(t, "status", "defect_type", "remarks", "result", "outcome")
    machine_col = find_col(t, "machine_id", "machine", "tool", "station")
    if not (status_col and machine_col):
        continue
    where = " OR ".join([f"lower({status_col}) LIKE '%{kw}%'" for kw in failure_keywords])
    df = con.execute(f"""
        SELECT {machine_col} AS machine, COUNT(*) AS failures
        FROM {t}
        WHERE {where}
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 20
    """).fetchdf()
    if df.empty:
        continue
    ax = df.plot(kind="bar", x="machine", y="failures",
                 title=f"{t}: failures by {machine_col} (keywords: {', '.join(failure_keywords)})")
    plt.tight_layout()
    plt.savefig(OUT / f"{t}_failures_by_machine.png")
    plt.clf()
    print(f"📸 saved {t}_failures_by_machine.png")

# ---------------------------------------------------------
# 3) MONTHLY THROUGHPUT (robust casting from string dates)
# ---------------------------------------------------------
# We try TIMESTAMP first, then DATE, using TRY_CAST and COALESCE
# so varchar datetime columns will still work.
for t in tables:
    dt_col = find_col(t, "datetime", "date_time", "timestamp", "date", "time")
    if not dt_col:
        continue
    df = con.execute(f"""
        SELECT
          date_trunc(
            'month',
            COALESCE(
              TRY_CAST({dt_col} AS TIMESTAMP),
              TRY_CAST({dt_col} AS DATE)
            )
          ) AS month,
          COUNT(*) AS n
        FROM {t}
        WHERE COALESCE(
                TRY_CAST({dt_col} AS TIMESTAMP),
                TRY_CAST({dt_col} AS DATE)
              ) IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """).fetchdf()
    if df.empty:
        continue
    ax = df.plot(x="month", y="n", title=f"{t}: monthly counts")
    plt.tight_layout()
    plt.savefig(OUT / f"{t}_monthly_counts.png")
    plt.clf()
    print(f"📸 saved {t}_monthly_counts.png")

print("✅ Charts (if data/columns available) written to:", OUT)
