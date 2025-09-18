import os
import duckdb
import pandas as pd
from sqlalchemy import create_engine, text
from settings import DB_ENGINE, DB_PATH

# Pluggable DB connection (default: DuckDB)
def get_engine():
    if DB_ENGINE == 'duckdb':
        return duckdb.connect(DB_PATH)
    elif DB_ENGINE == 'postgresql':
        # Example: postgresql://user:pass@host:port/dbname
        dsn = os.getenv('DB_DSN')
        return create_engine(dsn)
    else:
        raise ValueError(f"Unsupported DB_ENGINE: {DB_ENGINE}")

def get_schema_info():
    if DB_ENGINE == 'duckdb':
        con = duckdb.connect(DB_PATH)
        tables = con.execute("SHOW TABLES").fetchdf()['name'].tolist()
        schema = {}
        for t in tables:
            cols = con.execute(f"DESCRIBE {t}").fetchdf()[['column_name', 'column_type']]
            schema[t] = cols.to_dict('records')
        return schema
    # Add Postgres/other support as needed
    raise NotImplementedError()
