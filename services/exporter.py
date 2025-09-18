"""
Exporter for DataFrame to CSV, Parquet, XLSX for Power BI agent
"""
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import openpyxl
import os

def export_df(df: pd.DataFrame, out_path: str, fmt: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if fmt == "csv":
        df.to_csv(out_path, index=False)
    elif fmt == "parquet":
        table = pa.Table.from_pandas(df)
        pq.write_table(table, out_path)
    elif fmt == "xlsx":
        df.to_excel(out_path, index=False)
    else:
        raise ValueError(f"Unsupported export format: {fmt}")
