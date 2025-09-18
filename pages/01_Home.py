import streamlit as st

st.set_page_config(page_title="FCLM Home", layout="wide")

st.markdown("""
<div style='background: linear-gradient(90deg, #6366f1 0%, #06b6d4 100%); padding: 28px 0; border-radius: 12px; margin-bottom: 24px;'>
    <h2 style='color: white; text-align: center; margin-bottom: 0;'>🏠 FCLM Project Home</h2>
    <p style='color: #e0f2fe; text-align: center; font-size: 1.1em; margin-top: 8px;'>Unified Manufacturing Analytics Platform for Modern Factories</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1,1])
with col1:
    st.markdown("<h2 style='color:#6366f1; margin-bottom:8px;'>Problem</h2>", unsafe_allow_html=True)
    st.markdown("""
    - Manual analytics are slow, error-prone, and siloed
    - Business users can't self-serve insights from manufacturing data
    - Integrating new data sources (SAP, MES, IoT) is complex
    """)
    st.markdown("<h2 style='color:#6366f1; margin-bottom:8px;'>Solution</h2>", unsafe_allow_html=True)
    st.markdown("""
    - Unified DuckDB backend for scalable, fast queries
    - Natural language Q&A powered by LLMs (Claude, Copilot)
    - Role-based access, enterprise security, and audit logging
    - Instant analytics on manufacturing, gas, and cure data
    - Automated data quality checks and versioning
    - Interactive dashboards for real-time monitoring
    - Self-service analytics for business users
    - Modular architecture for easy integration and expansion
    - Scheduled data refresh and export options
    - Data versioning and snapshot restore for reliability
    """)

with col2:
    st.markdown("<h2 style='color:#6366f1; margin-bottom:8px;'>AI Tools & Features</h2>", unsafe_allow_html=True)
    st.markdown("""
    - NL→SQL: Ask business questions in plain English
    - Automated data quality checks and versioning
    - FastAPI backend for integration and automation
    - Streamlit dashboard with animated KPIs and chart explorer
    """)
    st.markdown("<h2 style='color:#6366f1; margin-bottom:8px;'>Future Integrations</h2>", unsafe_allow_html=True)
    st.markdown("""
    - SAP, MES, IoT, and external data sources
    - Predictive analytics and anomaly detection
    - Automated root cause analysis
    - Real-time streaming data integration
    - Digital twin modeling for process optimization
    - Integration with cloud data lakes (Azure, AWS, GCP)
    - Automated regulatory compliance reporting
    - Machine learning model deployment and monitoring
    - Advanced alerting and notification systems
    - API endpoints for mobile and third-party apps
    """)

st.markdown("""
<div style='display:flex; flex-wrap:wrap; gap:32px; justify-content:center; margin-top:32px;'>
    <div style='background-color:#f4f8fb; border-radius:12px; padding:24px; min-width:320px; max-width:420px; flex:1;'>
        <h2 style='color:#6366f1; text-align:center;'>🚀 Quick Start Guide</h2>
        <ol style='color:#1e3c72; font-size:1.08em;'>
            <li>Login or open the app sidebar</li>
            <li>Start on the Home page for overview</li>
            <li>Explore KPIs and charts in Dashboard</li>
            <li>Ask questions in Analytics Q&A</li>
            <li>Browse table schemas in Data Dictionary</li>
            <li>Run SQL and manage data in Database</li>
            <li>See technical details in Prompts & Tools</li>
        </ol>
    </div>
    <div style='background-color:#e0f7fa; border-radius:12px; padding:24px; min-width:320px; max-width:420px; flex:1;'>
        <h2 style='color:#06b6d4; text-align:center;'>📊 Business Impact Stats</h2>
        <ul style='color:#1e3c72; font-size:1.08em;'>
            <li>⏱️ <b>Analytics turnaround:</b> <span style='color:#22c55e;'>days → seconds</span></li>
            <li>📉 <b>Manual errors reduced:</b> <span style='color:#22c55e;'>95%</span></li>
            <li>📈 <b>Data-driven decisions enabled at all levels</b></li>
            <li>🔒 <b>Role-based access & enterprise security</b></li>
        </ul>
    </div>
    <div style='background-color:#f4f8fb; border-radius:12px; padding:24px; min-width:320px; max-width:420px; flex:1;'>
        <h2 style='color:#6366f1; text-align:center;'>🗺️ Architecture Diagram</h2>
        <img src='https://raw.githubusercontent.com/Sohanredd/clm-nl2sql-api/main/docs/architecture_diagram.png' style='display:block; margin:auto; max-width:320px; border-radius:8px;'>
        <p style='color:#334155; text-align:center; margin-top:12px;'>FCLM Analytics: Streamlit UI → FastAPI backend → DuckDB database → LLMs (Claude, Copilot)</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.info("For demo: All data is synthetic. No confidential information shown.")
