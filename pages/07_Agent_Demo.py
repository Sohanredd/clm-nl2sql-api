import streamlit as st
import pandas as pd
from services.agent import FCLMAgent
from services.claude_llm import ClaudeLLM
import os

agent = FCLMAgent("db/fclm.duckdb")
llm = ClaudeLLM()

st.title("\U0001F916 FCLM Agent Chatbot (Claude + Data)")

st.header("Ask Anything!")
question = st.text_input("Type your question for the agent (business, data, or general)")
if st.button("Ask Agent"):
    # Simple routing: if question mentions table/data, use agent; else use Claude
    business_keywords = ["table", "data", "failures", "machine", "refresh", "export", "duckdb", "monthly", "quality"]
    if any(kw in question.lower() for kw in business_keywords):
        def llm_func(prompt):
            sql_prompt = f"Translate to SQL: {prompt}"
            return llm.ask(sql_prompt)
        sql = agent.nl2sql(question, llm_func)
        st.write(f"**Generated SQL:** `{sql}`")
        result = agent.run_query(sql)
        if isinstance(result, pd.DataFrame):
            st.dataframe(result)
        else:
            st.error(result)
    else:
        answer = llm.ask(question)
        st.write(f"**Claude says:** {answer}")

st.header("Export Data for Power BI")
export_table = st.text_input("Table to export (e.g., 'cure_table1')")
export_fmt = st.selectbox("Format", ["csv", "xlsx", "parquet"])
if st.button("Export & Download Data"):
    msg = agent.export_data(export_table, fmt=export_fmt)
    st.success(msg)
    st.info("You can now import this file into Power BI for analysis.")

st.header("Automate Data Refresh for Power BI")
if st.button("Refresh Data from CSVs"):
    msg = agent.refresh_data()
    st.success(msg)
    st.info("All tables reloaded. You can now export fresh data for Power BI.")

st.header("Power BI Integration Help")
st.markdown("""
**How to use exported data in Power BI:**
1. Click 'Export & Download Data' above.
2. Download the file from the 'outputs' folder.
3. Open Power BI Desktop.
4. Click 'Get Data' and choose your file format (CSV, Excel, Parquet).
5. Load the data and start building your report!

**Advanced:**
- Connect Power BI directly to DuckDB using ODBC or custom API endpoints.
- Use the agent to automate data refresh and export for scheduled Power BI updates.
""")

st.caption("For direct Power BI integration, see the Help section above.")
