import streamlit as st



st.set_page_config(page_title="FCLM Project Tools", layout="wide")
st.markdown("""
<div style='background: linear-gradient(90deg, #6366f1 0%, #06b6d4 100%); padding: 28px 0; border-radius: 12px; margin-bottom: 24px;'>
    <h2 style='color: white; text-align: center; margin-bottom: 0;'>🛠️ Project Tools & Technologies</h2>
</div>
""", unsafe_allow_html=True)


col1, col2 = st.columns(2)
with col1:
    st.markdown("<h2 style='color:#1e3c72;'>🤖 AI & LLMs</h2>", unsafe_allow_html=True)
    st.markdown("""
    - **Anthropic Claude API** (NL→SQL, prompt engineering)
    - **OpenAI GPT-4 & GPT-5** (prompt engineering, code generation, validation)
    - **GitHub Copilot** (AI-powered code completion, refactoring)
    - **FastAPI** (serving AI endpoints, backend integration)
    - **Hugging Face Transformers** (NLP, model experimentation)
    - **Streamlit** (UI, interactive analytics)
    """)
    st.markdown("<h2 style='color:#1e3c72;'>📝 Prompt Engineering</h2>", unsafe_allow_html=True)
    st.markdown("""
    - Custom schema-aware prompts for NL→SQL
    - Strict output cleaning and validation logic
    - Fallback and error handling strategies
    - Iterative prompt refinement using GPT-4, GPT-5, Claude
    """)

with col2:
    st.markdown("<h2 style='color:#1e3c72;'>🗄️ Database & Data Tools</h2>", unsafe_allow_html=True)
    st.markdown("""
    - **DuckDB** (in-memory analytics DB)
    - **Pandas** (data wrangling, profiling)
    - **CSV, Parquet** (raw datasets)
    """)
    st.markdown("<h2 style='color:#1e3c72;'>💻 Coding & Dev Platforms</h2>", unsafe_allow_html=True)
    st.markdown("""
    - **Python 3.10+** (core logic, data processing)
    - **VS Code** (IDE)
    - **GitHub** (version control, collaboration)
    - **Jupyter** (exploratory analysis, prototyping)
    """)

st.markdown("<h2 style='color:#1e3c72;'>🧰 Other Tools</h2>", unsafe_allow_html=True)
st.markdown("""
- **dotenv** (secure API key management)
- **Requests** (API calls)
- **Matplotlib, Seaborn** (custom visualizations)
- **pytest** (testing)
""")
