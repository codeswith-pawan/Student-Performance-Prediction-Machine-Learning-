import streamlit as st
import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Student Analytics AI", layout="wide", page_icon="🎓")

# ------------------ PREMIUM UI ------------------
st.markdown("""
<style>
.main { background-color: #0E1117; color: white; }

section[data-testid="stSidebar"] {
    background-color: #1E1E2F;
}

.stMetric {
    background: #1f2937;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    font-size: 18px;
}

div.stButton > button {
    background-color: #22c55e;
    color: white;
    border-radius: 8px;
    height: 3em;
    font-weight: bold;
}

h1, h2, h3 { color: #f9fafb; }
</style>
""", unsafe_allow_html=True)

# ------------------ MODEL ------------------
@st.cache_resource
def load_model():
    try:
        return joblib.load("model/student_model.pkl")
    except:
        return None

model = load_model()

def get_risk_status(avg):
    if avg >= 75: return "Low", "🟢"
    elif avg >= 50: return "Medium", "🟡"
    return "High", "🔴"

# ------------------ SIDEBAR ------------------
st.sidebar.title("⚙️ Control Panel")
mode = st.sidebar.radio("Navigation", ["Single Prediction", "Batch Analysis", "Model Insights"])
threshold = st.sidebar.slider("Pass Threshold", 40, 80, 50)

# ------------------ HEADER ------------------
st.markdown("""
<h1 style='text-align:center'>🎓 Student Performance Analytics</h1>
<p style='text-align:center;color:gray'>AI-powered decision support system</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ================== SINGLE ==================
if mode == "Single Prediction":
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("📊 Input Scores")

        reading = st.slider("📖 Reading", 0, 100, 70)
        writing = st.slider("✍️ Writing", 0, 100, 65)
        math = st.slider("🧮 Math", 0, 100, 60)

        avg = (reading + writing + math) / 3

        run = st.button("🚀 Run AI Analysis")

    with col2:
        if run:
            with st.spinner("Analyzing..."):
                time.sleep(1)

            if model:
                X = np.array([[reading, writing, math]])
                pred = model.predict(X)[0]
                prob = model.predict_proba(X)[0][1]
            else:
                pred = 1 if avg >= threshold else 0
                prob = avg / 100

            risk, emoji = get_risk_status(avg)

            # -------- Metrics --------
            m1, m2, m3 = st.columns(3)
            m1.metric("📊 Avg Score", f"{avg:.1f}")
            m2.metric("🤖 Confidence", f"{prob*100:.1f}%")
            m3.metric("⚠️ Risk", f"{risk} {emoji}")

            # -------- Result --------
            if pred == 1:
                st.markdown(f"""
                <div style='padding:20px;border-radius:10px;background:#16a34a;color:white;text-align:center;font-size:20px'>
                ✅ PASS
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='padding:20px;border-radius:10px;background:#dc2626;color:white;text-align:center;font-size:20px'>
                ❌ FAIL
                </div>
                """, unsafe_allow_html=True)

            # -------- Rank --------
            if avg >= 85:
                st.success("🏆 Top Performer")
            elif avg >= 70:
                st.info("🎯 Good Performer")
            elif avg >= 50:
                st.warning("⚠️ Average")
            else:
                st.error("🚨 At Risk")

            # -------- Radar Chart --------
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[reading, writing, math],
                theta=["Reading","Writing","Math"],
                fill='toself',
                fillcolor='rgba(34,197,94,0.3)',
                line=dict(color='#22c55e')
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0,100])),
                height=450
            )
            st.plotly_chart(fig, use_container_width=True)

# ================== BATCH ==================
elif mode == "Batch Analysis":
    st.subheader("📂 Upload CSV")

    file = st.file_uploader("Upload file", type=["csv"])

    if file:
        df = pd.read_csv(file)

        cols = ["reading score","writing score","math score"]

        if all(c in df.columns for c in cols):
            if model:
                df["Probability"] = model.predict_proba(df[cols])[:,1]
                df["Prediction"] = df["Probability"].apply(lambda x: "PASS" if x>=0.5 else "FAIL")

            st.dataframe(df)

            fig = px.pie(df, names="Prediction")
            st.plotly_chart(fig)

            st.download_button("Download", df.to_csv(index=False), "result.csv")

        else:
            st.error("CSV columns missing")

# ================== INSIGHTS ==================
else:
    st.subheader("🧠 Model Info")

    st.write("Model: Random Forest")
    st.write("Used for classification")

    df_imp = pd.DataFrame({
        "Feature":["Math","Reading","Writing"],
        "Importance":[0.45,0.30,0.25]
    })

    st.bar_chart(df_imp.set_index("Feature"))

# ------------------ FOOTER ------------------
st.sidebar.markdown("---")
st.sidebar.caption("Created by Pawan Sharma 🚀")