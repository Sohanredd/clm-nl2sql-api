import duckdb
import pandas as pd
import os

def connect_db(db_path=None):
    db_path = db_path or os.path.join("db", "fclm.duckdb")
    return duckdb.connect(db_path, read_only=True)

def list_tables(conn):
    return [row[0] for row in conn.execute("SHOW TABLES").fetchall()]

def get_table(conn, table):
    return conn.execute(f"SELECT * FROM {table} LIMIT 1000").fetchdf()

def get_schema(conn, table):
    cols = conn.execute(f"PRAGMA table_info('{table}')").fetchdf()
    return {"columns": cols["name"].tolist(), "types": cols["type"].tolist()}
