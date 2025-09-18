

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import streamlit as st
import duckdb
import pandas as pd

from ask_data.src.nl_to_sql import nl_to_sql


st.markdown("""
<div style='background: linear-gradient(90deg, #6366f1 0%, #06b6d4 100%); padding: 26px 0; border-radius: 12px; margin-bottom: 24px;'>
    <h2 style='color: white; text-align: center; margin-bottom: 0;'>🤖 Analytics QA: Natural Language to SQL</h2>
    <p style='color: #e0f2fe; text-align: center; font-size: 1.1em;'>
        <b>Ask questions in plain English. Get instant answers, SQL, and charts from FCLM data.</b>
    </p>
</div>
""", unsafe_allow_html=True)

db_path = "db/fclm.duckdb"
conn = duckdb.connect(db_path)

# --- Schema Introspection ---
def get_schema(conn): 
    tables = conn.execute("SHOW TABLES").fetchdf()["name"].tolist() 
    schema = {} 
    for t in tables: 
        cols = conn.execute(f"PRAGMA table_info('{t}')").fetchdf() 
        schema[t] = [{"column_name": row[1], "column_type": row[2]} for row in cols.values] 
    return schema 

schema = get_schema(conn)

# --- NL→SQL Parser/Router ---



# NL→SQL using Claude API only
def claude_nl_to_sql(question, schema):
    # schema is already a dict of table: list of dicts with column_name and column_type
    schema_json = schema
    result = nl_to_sql(question, schema_json)
    sql = result["sql"]
    rationale = result.get("rationale", "") + " (Claude API used)"
    st.markdown("**Raw Claude Output:**")
    st.code(result.get('raw_claude', ''), language="sql")
    st.markdown("**SQL to Run:**")
    st.code(sql, language="sql")
    # Visualization picking (simple)
    found_tables = [t for t in schema if t in question.lower()]
    found_cols = []
    for t in found_tables:
        for c in schema[t]:
            if c["column_name"].lower() in question.lower():
                found_cols.append((t, c["column_name"]))
    agg = None
    for a in ["count", "sum", "avg", "min", "max"]:
        if a in question.lower():
            agg = a
            break
    group_by = []
    import re
    m = re.findall(r"group by ([\w, ]+)", question.lower())
    if m:
        group_by = [g.strip() for g in m[0].split(",")]
    viz_type = pick_viz_type(sql, found_tables, found_cols, agg, group_by)
    x = pick_x(sql, found_cols, group_by)
    y = pick_y(sql, found_cols, agg)
    series = pick_series(sql, group_by)
    return {"sql": sql, "viz_type": viz_type, "x": x, "y": y, "series": series, "rationale": rationale}




# --- Visualization Picker ---
def pick_viz_type(sql, tables, cols, agg, group_by):
    if group_by and agg:
        if any("date" in g.lower() or "time" in g.lower() for g in group_by):
            return "line"
        else:
            return "bar"
    elif agg:
        return "bar"
    return "table"

def pick_x(sql, cols, group_by):
    if group_by:
        for g in group_by:
            if "date" in g.lower() or "time" in g.lower() or "month" in g.lower():
                return g
        return group_by[0]
    elif cols:
        return cols[0][1]
    return None

def pick_y(sql, cols, agg):
    if agg and cols:
        return cols[0][1]
    elif cols:
        return cols[-1][1]
    return None

def pick_series(sql, group_by):
    if group_by and len(group_by) > 1:
        return group_by[0]
    return None

def pick_chart(df, viz_type, x, y, series):
    if viz_type == "line" and x and y:
        st.line_chart(df.set_index(x)[y])
    elif viz_type == "bar" and x and y:
        st.bar_chart(df.set_index(x)[y])
    elif viz_type == "pie" and x and y:
        st.write("Pie chart not implemented, showing bar chart instead.")
        st.bar_chart(df.set_index(x)[y])
    else:
        st.dataframe(df)
        st.info("No suitable chart found, showing table.")

# --- UI ---

# --- Card-style input ---
st.markdown("""
<h3 style='color:#2a5298; margin-bottom:8px;'>📝 Ask a question about FCLM data</h3>
""", unsafe_allow_html=True)
question = st.text_input("E.g. Show monthly failures by machine, Total O2 usage by month, ...")

if question:
    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    with st.spinner("Generating answer..."):
        result = claude_nl_to_sql(question, schema)
        sql = result["sql"]
        rationale = result["rationale"]
        viz_type = result["viz_type"]
        x, y, series = result["x"], result["y"], result["series"]
    # --- Redesigned Rationale ---
    st.markdown(f"""
    <div style='border-radius:8px; padding:12px 18px; margin-bottom:18px; background: #e0f2fe;'>
        <span style='font-size:1.3em; vertical-align:middle;'>🧠</span>
        <span style='color:#0e7490; font-size:1.08em; font-weight:500; margin-left:6px;'>Rationale</span>
        <div style='color:#334155; font-size:1.04em; margin-top:6px;'>{rationale}</div>
    </div>
    """, unsafe_allow_html=True)
    try:
        df = conn.execute(sql).fetchdf()
        st.markdown("<div style='background-color:#f4f8fb; border-radius:10px; padding:16px 20px; margin-bottom:18px;'><h4 style='color:#2a5298; margin-bottom:8px;'>📊 Query Result</h4></div>", unsafe_allow_html=True)
        if df.empty:
            st.info("No results found for this query.")
        else:
            pick_chart(df, viz_type, x, y, series)
    except Exception as e:
        st.error(f"Query could not be executed: {e}")
