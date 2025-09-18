import duckdb, pandas as pd, pathlib, re

class FCLMAgent:
    def __init__(self, db_path):
        self.con = duckdb.connect(db_path, read_only=True)
        self.db_path = db_path
    # ...existing code...
