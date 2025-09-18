import streamlit as st
from lib.data_io import connect_db, list_tables, get_table

st.set_page_config(page_title="FCLM Data Browser", layout="wide")
st.markdown("""
<div style='background: linear-gradient(90deg, #6366f1 0%, #06b6d4 100%); padding: 28px 0; border-radius: 12px; margin-bottom: 24px;'>
    <h2 style='color: white; text-align: center; margin-bottom: 0;'>FCLM Data Browser & Table Explorer</h2>
</div>
""", unsafe_allow_html=True)

conn = connect_db()
tables = list_tables(conn)
selected_table = st.selectbox("Select table", tables)
if selected_table:
    df = get_table(conn, selected_table)
    st.dataframe(df.head(50))
    st.download_button("Download CSV", df.to_csv(index=False), f"{selected_table}_preview.csv")
    st.markdown("---")
    st.markdown(f"### Table Explorer for {selected_table}")
    st.write(f"Rows: {len(df)} | Columns: {', '.join(df.columns)}")
    st.dataframe(df.describe(include='all').transpose())
