import streamlit as st
import pandas as pd
import db
import nl_to_sql
import chart_picker
import settings
from tenacity import retry, stop_after_attempt, wait_fixed
import diskcache

# Disk cache for schema and query results
cache = diskcache.Cache(".askdata_cache")


# --- Welcome Banner / Hero Section ---
st.markdown(
    """
    <div style='background: linear-gradient(90deg, #3b82f6 0%, #06b6d4 100%); padding: 32px 0; border-radius: 12px; margin-bottom: 24px;'>
        <h1 style='color: white; text-align: center; margin-bottom: 0;'>Ask Data: FCLM Self-Service Analytics</h1>
        <p style='color: #e0f2fe; text-align: center; font-size: 1.2em;'>
            Ask questions about your FCLM manufacturing data and get instant answers, charts, and insights.<br>
            <b>Powered by DuckDB, Streamlit, and AI.</b>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Query Templates / Suggestions ---
st.markdown("**Try these example questions:**")
example_questions = [
    "How many failures occurred in July?",
    "Show the top 5 machines with the most downtime last month.",
    "What is the average cure time by machine for August?",
    "List all batches with status 'Failed' in the last 7 days.",
    "What is the total O2 gas usage by month this year?"
]
cols = st.columns(len(example_questions))
for i, q in enumerate(example_questions):
    if cols[i].button(q):
        st.session_state["question"] = q

# --- Chart/Table Toggle ---
if "show_table" not in st.session_state:
    st.session_state["show_table"] = False

# --- Schema Preview in Sidebar ---
with st.sidebar.expander("📊 Data Schema Preview", expanded=False):
    schema_preview = db.get_schema_info()
    for t, cols in schema_preview.items():
        st.markdown(f"**{t}**: " + ", ".join([c['column_name'] for c in cols]))

# --- Branding / Help / Feedback ---
st.sidebar.markdown("---")
st.sidebar.markdown("<b>FCLM Analytics Team</b><br><a href='mailto:support@fclm.com'>Contact Support</a>", unsafe_allow_html=True)
st.sidebar.button("💡 Help / Feedback")

# Sidebar: connection, schema refresh, history, safe mode
def sidebar():
    st.sidebar.header("Settings")
    st.sidebar.write(f"**DB Engine:** {settings.DB_ENGINE}")
    if st.sidebar.button("Refresh Schema"):
        cache.pop("schema", None)
    safe_mode = st.sidebar.checkbox("Safe Mode", value=settings.SAFE_MODE)
    history = cache.get("history", [])
    st.sidebar.subheader("Query History")
    for i, h in enumerate(reversed(history[-20:])):
        if st.sidebar.button(f"{h['question'][:40]}", key=f"hist_{i}"):
            st.session_state["question"] = h["question"]
    return safe_mode

safe_mode = sidebar()

# Get schema (cached)
@st.cache_data(ttl=600)
def get_schema():
    return db.get_schema_info()

schema = get_schema()

# Main chat input
if "question" not in st.session_state:
    st.session_state["question"] = ""

st.write("### Ask a question about your FCLM data:")
question = st.text_input("Question", st.session_state["question"])

if st.button("Submit") and question.strip():
    st.session_state["question"] = question
    # NL→SQL
    try:
        sql_info = nl_to_sql.nl_to_sql(question, schema)
        sql = sql_info["sql"]
        rationale = sql_info["rationale"]
        st.code(sql, language="sql")
        st.caption(f"Why this SQL: {rationale}")
        # Guardrails
        if safe_mode:
            # Only allow tables in schema, SELECT only, LIMIT
            import re
            tables_in_sql = set(re.findall(r'from\s+([\w_]+)', sql, re.I))
            allowed_tables = set(db.get_schema_info().keys())
            if not tables_in_sql.issubset(allowed_tables):
                raise ValueError(f"Table(s) {tables_in_sql - allowed_tables} not allowed in SQL.")
            if not sql.lower().startswith("select"):
                raise ValueError("Only SELECT allowed.")
            if "limit" not in sql.lower():
                sql += f" LIMIT {settings.ROW_LIMIT}"
        # Run query
        @retry(stop=stop_after_attempt(2), wait=wait_fixed(2))
        def run_query():
            con = db.get_engine()
            if settings.DB_ENGINE == "duckdb":
                return con.execute(sql).fetchdf()
            else:
                return pd.read_sql(sql, con)
        df = run_query()
        # --- Result Summary Cards ---
        st.markdown("#### Result Summary")
        card_cols = st.columns(3)
        card_cols[0].metric("Rows", len(df))
        card_cols[1].metric("Columns", len(df.columns))
        card_cols[2].metric("First Column", df.columns[0] if len(df.columns) > 0 else "-")
        # --- Chart/Table Toggle ---
        toggle = st.toggle("Show Table", value=st.session_state["show_table"])
        st.session_state["show_table"] = toggle
        if not toggle:
            chart_picker.pick_chart(df)
        else:
            st.dataframe(df)
        # --- Improved Downloads ---
        st.download_button("Download CSV", df.to_csv(index=False), "result.csv")
        try:
            import io
            import plotly.io as pio
            fig = chart_picker.pick_chart(df)
            if fig is not None:
                buf = io.BytesIO()
                pio.write_image(fig, buf, format="png")
                st.download_button("Download Chart as PNG", buf.getvalue(), "chart.png")
        except Exception:
            pass
        # Narrative (placeholder)
        st.info(f"This result answers: '{question}'. (Narrative generation coming soon.)")
        # Save to history
        history = cache.get("history", [])
        history.append({"question": question, "sql": sql})
        cache["history"] = history[-20:]
    except Exception as e:
        st.error(f"Error: {e}")
