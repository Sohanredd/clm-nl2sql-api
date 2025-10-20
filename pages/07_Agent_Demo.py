import streamlit as st
import pandas as pd
from typing import Any

from services.agent import FCLMAgent
from services.claude_llm import ClaudeLLM

st.set_page_config(page_title="FCLM Agent Demo", layout="wide")

agent = FCLMAgent("db/fclm.duckdb")
llm = ClaudeLLM()

st.title("\U0001F916 FCLM Agent Chatbot (Claude + Data)")

st.markdown("""
Use the agent as a chatbot. Choose the question type:
- "General" for general knowledge / instructions (handled by Claude)
- "Data" for business/data questions (NL→SQL -> executed against DuckDB)
""")

mode = st.radio("Question type", ["Data", "General"], index=0, horizontal=True)
question = st.text_area("Ask your question", height=140, placeholder="e.g. Show monthly failures by machine")
run = st.button("Ask Agent")

# helper to extract text from LLM response (supports dict or str)
def llm_text(resp: Any) -> str:
    if isinstance(resp, dict):
        # common keys used by wrappers
        for k in ("text", "answer", "completion", "raw_text"):
            if k in resp and isinstance(resp[k], str):
                return resp[k]
        # fallback to string representation
        return str(resp.get("text") or resp.get("completion") or resp)
    return str(resp)

if run:
    q = (question or "").strip()
    if not q:
        st.warning("Please enter a question first.")
    else:
        try:
            with st.spinner("Processing..."):
                if mode == "General":
                    # general Q&A via Claude
                    resp = llm.ask(q)
                    text = llm_text(resp)

                    st.subheader("Answer")
                    st.write(text)

                    with st.expander("Raw LLM output"):
                        st.write(resp)

                else:
                    # Data question: convert NL -> SQL using LLM, then execute
                    # llm_func should return SQL string (handle dict/string)
                    def llm_func(prompt: str):
                        r = llm.ask(prompt)
                        return llm_text(r)

                    nl2sql_out = agent.nl2sql(q, llm_func)

                    # nl2sql_out may be string SQL or structured dict; handle both
                    raw_output = nl2sql_out
                    sql = ""
                    rationale = ""

                    if isinstance(nl2sql_out, dict):
                        sql = nl2sql_out.get("sql") or nl2sql_out.get("query") or nl2sql_out.get("cleaned_sql") or ""
                        rationale = nl2sql_out.get("rationale") or nl2sql_out.get("notes") or ""
                        raw_output = nl2sql_out.get("raw") or nl2sql_out.get("llm") or nl2sql_out
                    elif isinstance(nl2sql_out, str):
                        sql = nl2sql_out

                    st.subheader("Generated SQL")
                    if sql:
                        st.code(sql)
                    else:
                        st.info("No SQL produced by the LLM. Showing raw output below.")

                    with st.expander("Raw NL→SQL output"):
                        st.write(raw_output)

                    if rationale:
                        with st.expander("Rationale / Notes"):
                            st.write(rationale)

                    # Guardrail: only allow SELECT statements
                    sql_to_run = (sql or "").strip()
                    if not sql_to_run:
                        st.error("No SQL to execute. Refine your question or check raw LLM output.")
                    else:
                        first_word = sql_to_run.split()[0].lower()
                        if first_word != "select":
                            st.error("Generated SQL is not a SELECT statement. Execution aborted for safety.")
                            with st.expander("SQL (for debugging)"):
                                st.code(sql_to_run)
                        else:
                            try:
                                result = agent.run_query(sql_to_run)
                                if isinstance(result, pd.DataFrame):
                                    if result.empty:
                                        st.info("Query ran successfully but returned no rows.")
                                    else:
                                        st.dataframe(result)
                                else:
                                    st.error(f"Query execution returned an error: {result}")
                            except Exception as e:
                                st.error(f"Error running query: {e}")
                                with st.expander("SQL (for debugging)"):
                                    st.code(sql_to_run)
        except Exception as e:
            st.error(f"Agent failed: {e}")

st.markdown("---")

st.header("Utilities")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Export Data for Power BI")
    export_table = st.text_input("Table to export (e.g., 'cure_table1')", key="export_table")
    export_fmt = st.selectbox("Format", ["csv", "xlsx", "parquet"], key="export_fmt")
    if st.button("Export & Download Data", key="export"):
        msg = agent.export_data(export_table, fmt=export_fmt)
        if isinstance(msg, str) and msg.startswith("Exported"):
            st.success(msg)
            st.info("You can now import this file into Power BI for analysis.")
        else:
            st.error(msg)

with col2:
    st.subheader("Automate Data Refresh")
    if st.button("Refresh Data from CSVs", key="refresh"):
        msg = agent.refresh_data()
        st.success(msg)
        st.info("All tables reloaded.")

st.caption("If Claude (Anthropic) is unavailable the agent will fall back to a safe demo response. To enable real LLM answers install 'anthropic' and set ANTHROPIC_API_KEY.")
