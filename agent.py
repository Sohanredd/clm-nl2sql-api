import duckdb, pandas as pd, pathlib, re

class FCLMAgent:
    def __init__(self, db_path):
        self.con = duckdb.connect(db_path, read_only=True)
        self.db_path = db_path

    def nl2sql(self, question, llm_func):
        """
        Use an LLM function to convert NL to SQL. llm_func should accept a prompt and return SQL.
        """
        prompt = f"Convert this business question to SQL for DuckDB: {question}"
        sql = llm_func(prompt)
        return sql

    def run_query(self, sql):
        try:
            result = self.con.execute(sql).fetchdf()
            return result
        except Exception as e:
            return f"Error: {e}"

    def data_quality_check(self, table):
        """
        Check for missing values in all columns of a table.
        """
        sql = f"SELECT COUNT(*) AS total_rows, " + ", ".join([
            f"SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) AS {col}_missing"
            for col in self.con.execute(f"PRAGMA table_info('{table}')").fetchdf()['name']
        ]) + f" FROM {table}"
        return self.run_query(sql)

    def refresh_data(self, raw_dir="data/raw"):
        """Re-ingest all CSVs from raw_dir into DuckDB."""
        RAW = pathlib.Path(raw_dir)
        for csv_path in RAW.glob("*.csv"):
            table = re.sub(r"[^a-z0-9_]", "_", csv_path.stem.lower())
            self.con.execute(f"""
                CREATE OR REPLACE TABLE {table} AS
                SELECT * FROM read_csv_auto('{csv_path.as_posix()}', header=True, sample_size=-1);
            """)
        return "✅ Data refresh complete."

    def export_data(self, table, fmt="csv", out_dir="outputs"):
        """Export a table to CSV, Excel, or Parquet."""
        df = self.run_query(f"SELECT * FROM {table}")
        out_path = pathlib.Path(out_dir) / f"{table}_export.{fmt}"
        if isinstance(df, pd.DataFrame):
            if fmt == "csv":
                df.to_csv(out_path, index=False)
            elif fmt == "xlsx":
                df.to_excel(out_path, index=False)
            elif fmt == "parquet":
                df.to_parquet(out_path, index=False)
            else:
                return f"Unsupported format: {fmt}"
            return f"Exported to {out_path}"
        return df

    def guide_workflow(self, workflow_name):
        """Provide step-by-step guidance for analytics workflows."""
        workflows = {
            "monthly_failures": [
                "Step 1: Select the 'cure_table1' table.",
                "Step 2: Group by 'machine' and 'month'.",
                "Step 3: Count failures per group.",
                "Step 4: Visualize as bar chart."
            ],
            "data_quality": [
                "Step 1: Choose a table.",
                "Step 2: Run missing value check.",
                "Step 3: Review columns with high nulls.",
                "Step 4: Export results if needed."
            ]
        }
        return workflows.get(workflow_name, ["Workflow not found."])

    def monitor_anomalies(self, table, column):
        """Detect simple outliers (z-score > 3) in a numeric column."""
        sql = f"""
        SELECT {column}, AVG({column}) AS mean, STDDEV_SAMP({column}) AS std
        FROM {table}
        WHERE {column} IS NOT NULL
        """
        stats = self.run_query(sql)
        if isinstance(stats, pd.DataFrame) and not stats.empty:
            mean = stats['mean'][0]
            std = stats['std'][0]
            outlier_sql = f"""
            SELECT * FROM {table}
            WHERE ABS({column} - {mean}) > 3 * {std}
            """
            return self.run_query(outlier_sql)
        return stats

    def integrate_external_api(self, api_name, params):
        """Stub for external API integration (Power BI, SAP, etc.)."""
        # Implement actual API calls here
        return f"Called external API '{api_name}' with params {params}"

    def multi_step_task(self, steps):
        """Orchestrate multi-step agent actions."""
        results = []
        for step in steps:
            action = step.get("action")
            args = step.get("args", {})
            if hasattr(self, action):
                results.append(getattr(self, action)(**args))
            else:
                results.append(f"Unknown action: {action}")
        return results

# Example usage (replace llm_func with your LLM call):
# agent = FCLMAgent('db/fclm.duckdb')
# sql = agent.nl2sql('Show monthly failures by machine', llm_func)
# result = agent.run_query(sql)
# dq = agent.data_quality_check('cure_table1')
# agent.refresh_data()
# agent.export_data('cure_table1', fmt='xlsx')
# guide = agent.guide_workflow('monthly_failures')
# anomalies = agent.monitor_anomalies('cure_table1', 'failure_rate')
# api_response = agent.integrate_external_api('PowerBI', {'param1': 'value1'})
# multi_step_results = agent.multi_step_task([
#     {"action": "nl2sql", "args": {"question": "Show monthly failures by machine", "llm_func": llm_func}},
#     {"action": "run_query", "args": {"sql": "SELECT * FROM monthly_failures_summary"}},
#     {"action": "export_data", "args": {"table": "monthly_failures_summary", "fmt": "csv"}}
# ])
