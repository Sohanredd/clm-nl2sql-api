import duckdb, pathlib, pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB   = ROOT / "db" / "fclm.duckdb"
OUT  = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(DB.as_posix())
tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]

lines = ["# FCLM Demo — Data Dictionary\n"]
for t in tables:
    info = con.execute(f"DESCRIBE {t}").fetchdf()
    head = con.execute(f"SELECT * FROM {t} LIMIT 5").fetchdf()
    lines.append(f"## {t}\n\n**Schema**\n\n{info.to_markdown(index=False)}\n")
    lines.append(f"**Sample rows**\n\n{head.to_markdown(index=False)}\n")
    head.to_csv(OUT / f"{t}_preview.csv", index=False)

(OUT / "data_dictionary.md").write_text("\n".join(lines))
print("📄 Wrote outputs/data_dictionary.md and *_preview.csv")
