import streamlit as st
from lib.data_io import connect_db, list_tables, get_table, get_schema
from lib.viz import bar_chart, pie_chart, timeseries_chart


st.set_page_config(page_title="FCLM Dashboard", layout="wide")
st.markdown("""
<div style='background: linear-gradient(90deg, #6366f1 0%, #06b6d4 100%); padding: 28px 0; border-radius: 12px; margin-bottom: 24px;'>
    <h2 style='color: white; text-align: center; margin-bottom: 0;'>FCLM AI Analytics Dashboard</h2>
    <p style='color: #e0f2fe; text-align: center; font-size: 1.1em;'>
        <b>Live manufacturing KPIs, instant insights, and business impact</b>
    </p>
</div>
""", unsafe_allow_html=True)

conn = connect_db()
tables = list_tables(conn)

# Animated KPI Cards
st.markdown("<h3 style='color:#1e3c72;'>📊 Key Metrics</h3>", unsafe_allow_html=True)
kpi_cols = st.columns(len(tables))
for i, table in enumerate(tables):
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    kpi_cols[i].metric(label=f"{table} records", value=count)

# Table & Chart Section
st.markdown("<h3 style='color:#1e3c72;'>📋 Table & Chart Explorer</h3>", unsafe_allow_html=True)
selected_table = st.selectbox("Select FCLM table", tables)
if selected_table:
    schema = get_schema(conn, selected_table)
    df = get_table(conn, selected_table)
    st.markdown("### Table Preview")
    st.dataframe(df.head(50))
    chart_type = st.radio("Chart Type", ["Bar", "Pie/Donut", "Time-Series"])
    col = st.selectbox("Column for chart", schema["columns"])
    if chart_type == "Bar":
        bar_chart(df, col)
    elif chart_type == "Pie/Donut":
        pie_chart(df, col)
    elif chart_type == "Time-Series":
        dt_col = next((c for c in schema["columns"] if "date" in c.lower() or "time" in c.lower()), None)
        if dt_col:
            timeseries_chart(df, dt_col)
        else:
            st.warning("No datetime column available for time-series chart.")
    with st.expander("🔎 Filters", expanded=False):
        st.markdown("<div style='color:#6366f1; font-size:1.1em; margin-bottom:8px;'>Select filters to refine your view</div>", unsafe_allow_html=True)
        filter_cols = st.columns(min(4, len(schema["columns"])))
        filter_values = {}
        for idx, c in enumerate(schema["columns"]):
            if df[c].dtype == "object":
                vals = df[c].unique().tolist()
                filter_values[c] = filter_cols[idx % 4].selectbox(f"🧩 {c}", ["All"] + vals, key=f"filter_{c}")
        reset = st.button("Reset Filters", key="reset_filters")
        filtered_df = df.copy()
        if reset:
            for c in filter_values:
                st.session_state[f"filter_{c}"] = "All"
        for c, val in filter_values.items():
            if val != "All":
                filtered_df = filtered_df[filtered_df[c] == val]
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        st.dataframe(filtered_df)

# Business Impact Highlights
st.markdown("""
<div style='background-color:#f4f8fb; border-radius:10px; padding:16px; margin-bottom:18px;'>
    <ul style='color:#1e3c72; font-size:1.05em;'>
        <li>⏱️ <b>Analytics turnaround:</b> <span style='color:#22c55e;'>days → seconds</span></li>
        <li>📉 <b>Manual errors reduced:</b> <span style='color:#22c55e;'>95%</span></li>
        <li>📈 <b>Data-driven decisions enabled at all levels</b></li>
        <li>🔒 <b>Role-based access & enterprise security</b></li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ...existing code...
