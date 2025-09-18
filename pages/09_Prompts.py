
import streamlit as st

st.set_page_config(page_title="Project Prompts", layout="wide")

st.markdown("""
<div style='background: linear-gradient(90deg, #6366f1 0%, #06b6d4 100%); padding: 26px 0; border-radius: 12px; margin-bottom: 24px;'>
    <h2 style='color: white; text-align: center; margin-bottom: 0;'>📝 Project Prompts</h2>
    <p style='color: #e0f2fe; text-align: center; font-size: 1.1em;'>
        <b>Key instructions given to GitHub Copilot to build this FCLM Analytics Demo</b>
    </p>
</div>
""", unsafe_allow_html=True)

prompts = [
    {
        "title": "Workspace and File Structure",
        "prompt": "Create a project workspace with the following structure: data/raw (for CSVs), db (for DuckDB database), outputs (for charts and previews), scripts (for Python scripts), and pages (for Streamlit app pages)."
    },
    {
        "title": "Ingest CSV Files as Tables",
        "prompt": "Write a Python script to ingest CSV files from data/raw into DuckDB. Each CSV (cure_table1.csv, gas_mixing_system.csv, O2_Gas_Data_FCLM.csv) should become a table in the database with matching names. Handle schema inference and data types automatically."
    },
    {
        "title": "Dataset to Database Workflow",
        "prompt": "Automate the process of loading datasets into DuckDB, ensuring each table is accessible for analytics and preview. Validate row counts and schema for each table after ingestion."
    },
    {
        "title": "Claude API Integration",
        "prompt": "Integrate Anthropic Claude API to translate natural language questions into SQL queries. Use Claude’s LLM capabilities to parse user intent, generate safe SQL, and provide step-by-step rationale for each query."
    },
    {
        "title": "Natural Language to SQL (NL→SQL)",
        "prompt": "Develop a module to convert natural language questions into SQL queries using the project schema. Integrate with LLMs for parsing and rationale. Return SQL, rationale, and visualization hints for each query."
    },
    {
        "title": "FastAPI Integration",
        "prompt": "Create a FastAPI backend to expose endpoints for NL→SQL conversion and database querying. Ensure endpoints accept questions, return SQL, and provide query results in JSON format."
    },
    {
        "title": "Streamlit App Creation",
        "prompt": "Build a multi-page Streamlit app with the following pages: Home, Dashboard, Analytics QA, Data Browser, Database, Test Cases, Tools, and Prompts. Each page should have a clear purpose and professional UI."
    },
    {
        "title": "UI/UX Enhancements",
        "prompt": "Refine the app's UI with custom banners, animated KPIs, chart explorers, expandable filter sections, and styled markdown. Ensure all backgrounds use blue/gray tones consistent with the app theme."
    }
]



for p in prompts:
    st.markdown(f"""
<div style='background: #fff; box-shadow: 0 2px 12px rgba(56,189,248,0.12); border-radius: 10px; padding: 18px 22px; margin-bottom: 18px;'>
    <h4 style='color: #6366f1; margin-bottom: 8px;'>🟦 {p['title']}</h4>
    <div style='color: #334155; font-size: 1.08em;'>{p['prompt']}</div>
</div>
""", unsafe_allow_html=True)

