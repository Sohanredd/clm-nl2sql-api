# scripts/analysis.py
import duckdb
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import seaborn as sns

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB   = ROOT / "db" / "fclm.duckdb"
OUT  = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(DB.as_posix())

def get_tables_and_counts():
    tables = con.execute("SHOW TABLES").fetchall()
    result = []
    for t in tables:
        name = t[0]
        count = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        result.append({'table': name, 'row_count': count})
    return pd.DataFrame(result)

def find_col(table, *candidates):
    cols = [r[1] for r in con.execute(f"PRAGMA table_info('{table}')").fetchall()]
    name_map = {c.lower(): c for c in cols}
    for cand in candidates:
        lc = cand.lower()
        if lc in name_map:
            return name_map[lc]
    for cand in candidates:
        lc = cand.lower()
        for k, original in name_map.items():
            if lc in k:
                return original
    return None

def join_tables_on_key(tables, key_candidates=("lot_id", "batch_id", "order_id")):
    # Find common key
    key_map = {}
    for t in tables:
        key = find_col(t, *key_candidates)
        if key:
            key_map[t] = key
    if len(key_map) < 2:
        return []
    # Join each pair of tables on the first found key
    joins = []
    key_items = list(key_map.items())
    for i in range(len(key_items)):
        for j in range(i+1, len(key_items)):
            t1, k1 = key_items[i]
            t2, k2 = key_items[j]
            if k1 == k2:
                query = f"SELECT * FROM {t1} LEFT JOIN {t2} USING ({k1})"
                df = con.execute(query).fetchdf()
                joins.append((f"{t1}__{t2}", df, k1))
    return joins

def compute_kpis(df, base_key):
    # Failure/rework rate
    status_col = None
    for c in df.columns:
        if any(x in c.lower() for x in ["status", "defect", "result", "outcome", "remarks"]):
            status_col = c
            break
    if not status_col:
        return None
    failure_keywords = ("fail", "rework", "leak", "reject", "error")
    df["is_failure"] = df[status_col].astype(str).str.lower().apply(lambda x: any(kw in x for kw in failure_keywords))
    failure_rate = df["is_failure"].mean()
    status_counts = df[status_col].value_counts().reset_index().rename(columns={"index": status_col, status_col: "count"})
    # Monthly throughput
    dt_col = None
    for c in df.columns:
        if any(x in c.lower() for x in ["datetime", "date_time", "timestamp", "date", "time"]):
            dt_col = c
            break
    monthly = None
    if dt_col:
        df["parsed_date"] = pd.to_datetime(df[dt_col], errors="coerce")
        monthly = df.dropna(subset=["parsed_date"]).groupby(pd.Grouper(key="parsed_date", freq="M")).size().reset_index(name="count")
    return {
        "failure_rate": failure_rate,
        "status_counts": status_counts,
        "monthly_throughput": monthly
    }

def plot_failure_correlation(joins):
    """Create a heatmap of failure correlations between tables."""
    failure_rates = {}
    # Extract failure info from each join
    for join_name, df, _ in joins:
        tables = join_name.split('__')
        status_cols = []
        # Find status columns for both tables
        for c in df.columns:
            if any(x in c.lower() for x in ["status", "defect", "result", "outcome", "remarks"]):
                for t in tables:
                    if t in c:  # Match column to its source table
                        status_cols.append((t, c))
        
        if len(status_cols) == 2:  # We need both tables' status
            failure_keywords = ("fail", "rework", "leak", "reject", "error")
            for table, col in status_cols:
                df[f"{table}_failure"] = df[col].astype(str).str.lower().apply(
                    lambda x: any(kw in x for kw in failure_keywords)
                )
            failure_rates[join_name] = df[[f"{t}_failure" for t, _ in status_cols]]

    # Create correlation matrix
    all_tables = list(set(t for join in joins for t in join[0].split('__')))
    corr_matrix = pd.DataFrame(index=all_tables, columns=all_tables, dtype=float)
    
    # Fill correlation matrix
    for join_name, failures in failure_rates.items():
        t1, t2 = join_name.split('__')
        corr = failures.corr().iloc[0,1]  # Get correlation between the two failure columns
        corr_matrix.loc[t1, t2] = corr
        corr_matrix.loc[t2, t1] = corr
    
    # Fill diagonal with 1.0
    for t in all_tables:
        corr_matrix.loc[t, t] = 1.0
    
    # Create heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='RdYlBu_r', center=0, vmin=-1, vmax=1)
    plt.title('Failure Correlation Between Processes')
    plt.tight_layout()
    plt.savefig(OUT / 'failure_correlation_heatmap.png')
    plt.close()
    print("📊 Saved failure correlation heatmap")

def main():
    # 1. Show tables and row counts
    tables_df = get_tables_and_counts()
    tables_df.to_csv(OUT / "tables_and_counts.csv", index=False)
    print(tables_df)
    # 2. Join tables pairwise
    tables = tables_df['table'].tolist()
    joins = join_tables_on_key(tables)
    if not joins:
        print("No common key found for joining tables.")
        return
    
    # Add visualization
    plot_failure_correlation(joins)
    
    for join_name, joined_df, join_key in joins:
        joined_df.to_csv(OUT / f"joined_data_{join_name}.csv", index=False)
        # 3. Compute KPIs
        kpis = compute_kpis(joined_df, join_key)
        if not kpis:
            print(f"No status column found for KPI computation in join {join_name}.")
            continue
        # 4. Save results
        pd.DataFrame({"failure_rate": [kpis["failure_rate"]]}).to_csv(OUT / f"failure_rate_{join_name}.csv", index=False)
        kpis["status_counts"].to_csv(OUT / f"status_counts_{join_name}.csv", index=False)
        if kpis["monthly_throughput"] is not None:
            kpis["monthly_throughput"].to_csv(OUT / f"monthly_throughput_{join_name}.csv", index=False)
        print(f"Results for join {join_name} saved to outputs/")

if __name__ == "__main__":
    main()
