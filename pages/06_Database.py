import streamlit as st
import os
from lib.data_io import connect_db, list_tables
from datetime import datetime

st.set_page_config(page_title="FCLM Database Info", layout="wide")
st.markdown("""
<div style='background: linear-gradient(90deg, #6366f1 0%, #06b6d4 100%); padding: 28px 0; border-radius: 12px; margin-bottom: 24px;'>
    <h2 style='color: white; text-align: center; margin-bottom: 0;'>FCLM Database Info</h2>
</div>
""", unsafe_allow_html=True)

DB_PATH = "db/fclm.duckdb"
conn = connect_db()  # single write connection for all operations
tables = list_tables(conn)

st.markdown(f"**Database Path:** {DB_PATH}")
if os.path.exists(DB_PATH):
    st.markdown(f"**File Size:** {os.path.getsize(DB_PATH)//1024} KB")
    st.markdown(f"**Last Modified:** {datetime.fromtimestamp(os.path.getmtime(DB_PATH)).strftime('%Y-%m-%d %H:%M:%S')}")

# --- Data Quality Checks ---
st.markdown("### Data Quality Checks")
import numpy as np
for t in tables:
    df = conn.execute(f"SELECT * FROM {t} LIMIT 1000").fetchdf()
    missing = df.isnull().sum().sum()
    outliers = 0
    for col in df.select_dtypes(include=[np.number]).columns:
        vals = df[col].dropna()
        if len(vals) > 0:
            q1, q3 = np.percentile(vals, [25, 75])
            iqr = q3 - q1
            outliers += ((vals < q1 - 1.5*iqr) | (vals > q3 + 1.5*iqr)).sum()
    schema = conn.execute(f"PRAGMA table_info('{t}')").fetchdf()
    mismatches = 0
    for i, col in enumerate(schema['name']):
        expected = schema['type'][i]
        actual = str(df[col].dtype)
        if expected.lower() not in actual.lower():
            mismatches += 1
    st.write(f"**{t}**: {len(df)} rows | Missing: {missing} | Outliers: {outliers} | Schema mismatches: {mismatches}")

st.markdown("### Tables and Row Counts")
for t in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    st.write(f"{t}: {count} rows")

st.markdown("### Read-Only SQL Runner (SELECT only)")

# --- Audit Logging ---
import time
AUDIT_TABLE = "_audit_log"
conn.execute(f"CREATE TABLE IF NOT EXISTS {AUDIT_TABLE} (timestamp DOUBLE, sql TEXT)")
sql = st.text_area("Enter SQL (SELECT only, LIMIT 1000):", "SELECT * FROM cure_table1 LIMIT 10")
if sql.strip().lower().startswith("select"):
    try:
        df = conn.execute(sql).fetchdf()
        st.dataframe(df)
        conn.execute(f"INSERT INTO {AUDIT_TABLE} VALUES (?, ?)", [time.time(), sql])
    except Exception as e:
        st.error(f"SQL error: {e}")
else:
    st.warning("Only SELECT queries are allowed.")

st.markdown("### Audit Log (last 20 queries)")

# --- Data Versioning ---
st.markdown("### Data Versioning (Snapshot & Restore)")
selected_table = st.selectbox("Select table to snapshot/restore", tables)
SNAPSHOT_TABLE = f"{selected_table}_snapshot"
if st.button(f"Snapshot {selected_table}"):
    conn.execute(f"CREATE OR REPLACE TABLE {SNAPSHOT_TABLE} AS SELECT * FROM {selected_table}")
    st.success(f"Snapshot of {selected_table} saved as {SNAPSHOT_TABLE}")
if st.button(f"Restore {selected_table} from snapshot"):
    try:
        conn.execute(f"CREATE OR REPLACE TABLE {selected_table} AS SELECT * FROM {SNAPSHOT_TABLE}")
        st.success(f"{selected_table} restored from snapshot.")
    except Exception as e:
        st.error(f"Restore failed: {e}")

# --- Scheduled Data Refresh (Manual Trigger) ---
st.markdown("### Data Refresh")
import subprocess
if st.button("Refresh Data from CSVs"):
    try:
        result = subprocess.run(["python3", "scripts/ingest.py"], capture_output=True, text=True)
        if result.returncode == 0:
            st.success("Data refreshed from CSVs.")
        else:
            st.error(f"Refresh failed: {result.stderr}")
    except Exception as e:
        st.error(f"Refresh error: {e}")

# --- Export/Download Options ---
st.markdown("### Export/Download Table")
export_table = st.selectbox("Select table to export", tables, key="export_table")
export_format = st.selectbox("Format", ["CSV", "Excel", "Parquet"])
df_export = conn.execute(f"SELECT * FROM {export_table}").fetchdf()
if export_format == "CSV":
    st.download_button("Download CSV", df_export.to_csv(index=False), f"{export_table}.csv")
elif export_format == "Excel":
    import io
    buf = io.BytesIO()
    df_export.to_excel(buf, index=False)
    st.download_button("Download Excel", buf.getvalue(), f"{export_table}.xlsx")
elif export_format == "Parquet":
    import io
    buf = io.BytesIO()
    df_export.to_parquet(buf)
    st.download_button("Download Parquet", buf.getvalue(), f"{export_table}.parquet")
