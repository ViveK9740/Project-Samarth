# src/app.py
import streamlit as st
import subprocess
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# import your NLP QA factory (returns an AgriQA instance)
from nlp_qa_system import get_answer

st.set_page_config(
    page_title="Project Samarth — Agri Q&A",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------
# Paths & helpers
# -------------------------
ROOT = Path(__file__).resolve().parents[1]  # project root
DATA_DIR = ROOT / "data"
CLEAN_CSV = DATA_DIR / "mandi_clean.csv"
API_FETCH_SCRIPT = ROOT / "src" / "api_fetch.py"
DATA_PROCESS_SCRIPT = ROOT / "src" / "data_process.py"

def file_age_hours(path: Path):
    if not path.exists():
        return None
    return (datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)).total_seconds() / 3600

def run_refresh():
    """Run api_fetch.py and data_process.py sequentially."""
    # Use non-blocking prints inside subprocess - show spinner in UI
    try:
        subprocess.run(["python", str(API_FETCH_SCRIPT)], check=True)
    except subprocess.CalledProcessError:
        return False, "api_fetch.py failed. Check logs in terminal."

    if DATA_PROCESS_SCRIPT.exists():
        try:
            subprocess.run(["python", str(DATA_PROCESS_SCRIPT)], check=True)
        except subprocess.CalledProcessError:
            return False, "data_process.py failed. Check logs in terminal."

    return True, "Data refresh completed."

# -------------------------
# Sidebar — Controls & Info
# -------------------------
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🔁 Refresh Data (manual)"):
        with st.spinner("Refreshing data (fetch -> clean)..."):
            ok, msg = run_refresh()
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    st.markdown("---")
    st.header("📊 Data Source")
    st.markdown("**Dataset:** Agmarknet (Ministry of Agriculture & Farmers Welfare)")
    st.markdown("[View dataset on data.gov.in](https://data.gov.in)")
    st.markdown("---")

    # show file status
    if CLEAN_CSV.exists():
        age = file_age_hours(CLEAN_CSV)
        st.write("**Cleaned dataset:**", f"`{CLEAN_CSV.name}`")
        st.write("Last updated:", datetime.fromtimestamp(CLEAN_CSV.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
        if age and age > 24:
            st.warning(f"Dataset is {age:.1f} hours old. Consider refreshing.")
    else:
        st.error("Clean dataset not found. Click 'Refresh Data' to fetch & prepare data.")

    st.markdown("---")
    st.header("💡 Tips")
    st.write("Try queries like:")
    st.write("- `Brinjal price in Gujarat`")
    st.write("- `Show trend of tomato in Bangalore`")
    st.write("- `Which market has highest potato price?`")
    st.markdown("---")
    st.caption("Project Samarth — one-click demo ready")

# If CSV missing or stale auto-refresh prompt
auto_refresh_needed = not CLEAN_CSV.exists() or (file_age_hours(CLEAN_CSV) or 9999) > 24
if auto_refresh_needed:
    st.info("Clean dataset missing or older than 24 hours. Click Refresh Data or allow auto-refresh.")
    if st.button("Auto-refresh now"):
        with st.spinner("Auto-refreshing data..."):
            ok, msg = run_refresh()
            if ok:
                st.success(msg)
            else:
                st.error(msg)

# -------------------------
# Main UI
# -------------------------
st.markdown("<div style='display:flex; gap: 18px; align-items: center'>"
            "<h1 style='margin:0'>🌾 Project Samarth — Intelligent Agri Q&A</h1>"
            "<div style='color:gray; padding-left:12px'>Interactive demo over Agmarknet mandi data</div>"
            "</div>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 💬 Ask a question")
    query = st.text_input("", placeholder="e.g., What is the price of Tomato in Bangalore market today?")

    # quick-buttons for sample queries
    c1, c2, c3 = st.columns(3)
    if c1.button("Brinjal price in Gujarat"):
        query = "Brinjal price in Gujarat"
    if c2.button("Tomato trend in Bangalore"):
        query = "Show trend of tomato in Bangalore"
    if c3.button("Which market has highest potato price"):
        query = "Which market has the highest potato price?"

    # Session state for conversation history
    if "history" not in st.session_state:
        st.session_state.history = []

    ask_btn = st.button("Get Answer")

    if ask_btn:
        if not query.strip():
            st.warning("Please enter a question first.")
        else:
            # instantiate QA (loads data inside)
            try:
                qa = get_answer()
            except Exception as e:
                st.error(f"Failed to initialize QA engine: {e}")
                qa = None

            if qa:
                with st.spinner("Analyzing question..."):
                    # The AgriQA instance in our design exposes answer_question()
                    try:
                        ans = qa.answer_question(query)
                    except Exception as e:
                        ans = f"Error while answering: {e}"

                # Save to history and display
                st.session_state.history.insert(0, {"q": query, "a": ans, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                st.success(ans)

                # If the answer is a trend response (we produce text containing 📈), try to show a chart
                # We'll attempt to find a commodity & location using the QA extractor (if present)
                try:
                    # try to access internal df to make a supportive table/plot
                    df = getattr(qa, "df", None)
                    if df is not None and not df.empty:
                        # basic attempt to detect commodity and location from question using the class helper if exists
                        # We try calling extract_entities if available
                        commodity, location, _ = None, None, None
                        if hasattr(qa, "extract_entities"):
                            commodity, location, _ = qa.extract_entities(query)
                        # filter df for a short supporting table
                        temp = df.copy()
                        if commodity:
                            temp = temp[temp["commodity"].str.contains(commodity, case=False, na=False)]
                        if location:
                            temp = temp[temp["market"].str.contains(location, case=False, na=False) |
                                        temp["state"].str.contains(location, case=False, na=False) |
                                        temp["district"].str.contains(location, case=False, na=False)]
                        if not temp.empty:
                            # show recent rows to support the answer
                            st.markdown("**Supporting data (recent rows)**")
                            st.dataframe(temp.sort_values("date", ascending=False).head(8))
                            # if trend-like answer, plot recent mean modal_price by date
                            if "trend" in ans.lower() or "📈" in ans:
                                if "date" in temp.columns and "modal_price" in temp.columns:
                                    plot_df = (temp.groupby("date")["modal_price"].mean().reset_index().sort_values("date"))
                                    # streamlit line chart
                                    st.markdown("**Price trend (from dataset)**")
                                    st.line_chart(plot_df.rename(columns={"date": "index"}).set_index("index")["modal_price"])
                    else:
                        st.info("No local dataset loaded in QA instance to show supporting table/plot.")
                except Exception as e:
                    st.warning(f"Could not generate supporting visuals: {e}")

with col2:
    st.markdown("### 🕘 Recent Q&A")
    if st.session_state.history:
        for h in st.session_state.history[:6]:
            st.markdown(f"**Q:** {h['q']}  \n**A:** {h['a']}  \n*{h['time']}*")
            st.markdown("---")
    else:
        st.write("No questions asked yet. Try the sample buttons or type your own question.")

    st.markdown("### 📁 Dataset Snapshot")
    if CLEAN_CSV.exists():
        try:
            df_sample = pd.read_csv(CLEAN_CSV).head(6)
            st.dataframe(df_sample)
        except Exception as e:
            st.write("Could not preview dataset:", e)
    else:
        st.write("Clean dataset not available. Use Refresh Data.")

# -------------------------
# Footer / status
# -------------------------
st.markdown("---")
file_status = f"Clean CSV: {'found' if CLEAN_CSV.exists() else 'missing'}"
st.caption(f"{file_status} • App powered by Agmarknet data • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
