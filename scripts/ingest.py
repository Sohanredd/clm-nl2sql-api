import duckdb, pathlib, re

RAW = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"
DB  = pathlib.Path(__file__).resolve().parents[1] / "db" / "fclm.duckdb"
DB.parent.mkdir(parents=True, exist_ok=True)

print("RAW path:", RAW)
print("CSV files found:", [f.name for f in RAW.glob("*.csv")])

con = duckdb.connect(DB.as_posix())

# Load every CSV in data/raw as its own table
for csv_path in RAW.glob("*.csv"):
    table = re.sub(r"[^a-z0-9_]", "_", csv_path.stem.lower())
    print(f"--> Loading {csv_path.name}  as table  {table}")
    con.execute(f"""
        CREATE OR REPLACE TABLE {table} AS
        SELECT * FROM read_csv_auto('{csv_path.as_posix()}', header=True, sample_size=-1);
    """)

print("✅ All CSVs loaded into", DB)
