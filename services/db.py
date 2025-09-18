"""
DuckDB connection and safe SELECT execution for Power BI agent
"""
import duckdb, pandas as pd
from typing import Any
import re

def safe_execute_select(sql: str) -> pd.DataFrame:
    # Guardrail: only SELECT allowed
    if not sql.strip().lower().startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")
    # Optionally, check for forbidden keywords
    forbidden = ["insert", "update", "delete", "drop", "alter"]
    for word in forbidden:
        if re.search(rf"\b{word}\b", sql, re.I):
            raise ValueError(f"Forbidden SQL keyword: {word}")
    con = duckdb.connect("db/fclm.duckdb", read_only=True)
    try:
        df = con.execute(sql).fetchdf()
    finally:
        con.close()
    return df
