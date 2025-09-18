"""
NL→SQL wrapper with guardrails for Power BI agent
"""
from typing import Dict
import re

def nl2sql_with_guardrails(question: str) -> Dict:
    # Dummy implementation: replace with real Claude-powered NL→SQL
    # Guardrails: only SELECT, whitelisted tables/columns
    allowed_tables = {"cure_table1", "gas_mixing_system", "o2_gas_data_fclm"}
    sql = "SELECT * FROM cure_table1 LIMIT 10" if "failures" in question else "SELECT * FROM cure_table1 LIMIT 5"
    rationale = "Generated SQL for your business question."
    viz_hints = ["bar_chart", "table"]
    # Guardrail: block non-SELECT
    if not sql.strip().lower().startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")
    # Guardrail: check table usage
    tables = set(re.findall(r"from\s+([a-z0-9_]+)", sql, re.I))
    if not tables.issubset(allowed_tables):
        raise ValueError(f"Table(s) not allowed: {tables - allowed_tables}")
    return {"sql": sql, "rationale": rationale, "viz_hints": viz_hints}
