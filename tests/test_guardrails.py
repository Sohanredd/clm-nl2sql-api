"""
Unit tests for NL→SQL and DB guardrails
"""
import pytest
from services.nl2sql import nl2sql_with_guardrails
from services.db import safe_execute_select

def test_nl2sql_guardrails():
    # Only SELECT allowed
    with pytest.raises(ValueError):
        nl2sql_with_guardrails("Drop table cure_table1")
    # Only whitelisted tables
    with pytest.raises(ValueError):
        nl2sql_with_guardrails("Show me data from forbidden_table")
    # Valid question
    result = nl2sql_with_guardrails("Show monthly failures by machine")
    assert result["sql"].lower().startswith("select")

def test_safe_execute_select():
    # Only SELECT allowed
    with pytest.raises(ValueError):
        safe_execute_select("DELETE FROM cure_table1")
    # Forbidden keywords
    with pytest.raises(ValueError):
        safe_execute_select("DROP TABLE cure_table1")
    # Valid SQL
    df = safe_execute_select("SELECT * FROM cure_table1 LIMIT 1")
    assert df.shape[0] >= 0
