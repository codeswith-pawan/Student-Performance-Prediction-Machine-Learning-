import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
import time

# ------------------ CONFIG & UI ------------------
st.set_page_config(page_title="EduSmart AI Pro", layout="wide", page_icon="🎓")

# Function for Lottie Animations
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

lottie_book = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_V9t630.json")
lottie_success = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_pqnfmone.json")

# ------------------ PREMIUM STYLING ------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
    
    /* Card Styling */
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        transition: transform 0.3s ease;
    }
    .stMetric:hover { transform: translateY(-5px); border-color: #3b82f6; }
    
    /* Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white; border: none; padding: 10px 24px;
        border-radius: 8px; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { opacity: 0.9; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4); }
    
    /* Custom Headers */
    .header-text { font-size: 2.5rem; font-weight: 800; background: -webkit-linear-gradient(#eee, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""", unsafe_allow_html=True)

# ------------------ LOGIC FUNCTIONS ------------------
def get_ai_feedback(score, name="Student"):
    if score >= 90: return f"🌟 **{name}** is a Superstar! Suggestion: Enroll in advanced olympiad programs."
    if score >= 75: return f"✅ **{name}** is doing great. Focus on time management during exams."
    if score >= 50: return f"⚠️ **{name}** is in the safe zone but needs consistent practice in logic-building."
    return f"🚨 **{name}** requires immediate intervention and foundational classes."

def analyze_weakness(row, cols):
    weak_in = [s.replace(' score', '').title() for s in cols if row[s] < 50]
    return ", ".join(weak_in) if weak_in else "✨ Strong in All"

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st_lottie(lottie_book, height=150)
    st.markdown("<h2 style='text-align: center;'>EduSmart AI</h2>", unsafe_allow_html=True)
    option = st.sidebar.segmented_control(
        "Navigate", 
        ["Individual", "Batch", "Toppers", "Analytics"],
        default="Individual"
    )
    st.divider()
    st.caption("Developed for Professional Educators v2.0")

# ================== 1. INDIVIDUAL DIAGNOSTIC ==================
if option == "Individual":
    st.markdown("<h1 class='header-text'>👤 Student Diagnostic</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.2], gap="large")
    
    with col1:
        st.markdown("### Enter Assessment Details")
        with st.container(border=True):
            name = st.text_input("Full Name", "Pawan Kumar")
            m = st.slider("Math Score", 0, 100, 75)
            r = st.slider("Reading Score", 0, 100, 60)
            w = st.slider("Writing Score", 0, 100, 65)
            run = st.button("Generate AI Report")
            
    if run:
        avg = (m+r+w)/3
        with col2:
            cols = st.columns(3)
            cols[0].metric("Avg Score", f"{avg:.1f}%")
            cols[1].metric("Proficiency", "High" if avg > 75 else "Mid")
            cols[2].metric("Status", "PASS" if avg >= 50 else "FAIL")
            
            st.markdown(f"### AI Analysis for {name}")
            st.info(get_ai_feedback(avg, name))
            
            # Radar Chart
            categories = ['Math', 'Reading', 'Writing']
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=[m, r, w], theta=categories, fill='toself', line_color='#3b82f6'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, 
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)

# ================== 2. BATCH INTELLIGENCE ==================
# ================== 2. BATCH INTELLIGENCE ==================
elif option == "Batch":
    st.markdown("<h1 class='header-text'>📂 Batch Intelligence</h1>", unsafe_allow_html=True)
    file = st.file_uploader("Upload Student CSV File", type="csv")
    
    if file:
        df = pd.read_csv(file)
        # Original columns save rakhte hain display ke liye
        original_cols = list(df.columns)
        # Clean columns for logic
        df.columns = [c.strip().lower() for c in df.columns]
        
        # --- FIX: SMART NAME DETECTOR ---
        # Agar 'name' nahi mil raha, toh pehle column ko hi Name maan lo
        name_col = 'name' if 'name' in df.columns else df.columns[0]
        
        # Required columns for marks
        required = ['math score', 'reading score', 'writing score']
        
        if all(col in df.columns for col in required):
            with st.spinner("AI is analyzing batch data..."):
                time.sleep(1)
                df['average'] = df[required].mean(axis=1).round(1)
                df['weakness'] = df.apply(lambda x: analyze_weakness(x, required), axis=1)
                
                t1, t2 = st.tabs(["📊 Full Report", "🚨 Intervention Needed"])
                
                with t1:
                    st.subheader("Class Overview")
                    # Displaying with original or identified name column
                    st.dataframe(df.style.background_gradient(subset=['average'], cmap='RdYlGn'), use_container_width=True)
                    
                with t2:
                    weak_df = df[df['weakness'] != "✨ Strong in All"]
                    if not weak_df.empty:
                        st.warning(f"Total {len(weak_df)} students need help.")
                        # YAHAN CHANGE KIYA HAI: 'name' ki jagah name_col use ho raha hai
                        st.table(weak_df[[name_col, 'average', 'weakness']])
                    else:
                        st_lottie(lottie_success, height=200)
                        st.success("Brilliant! Sabhi bachche pass hain.")
        else:
            st.error(f"Column mismatch! File headers must match: {required}")
            st.info(f"Aapki file mein ye headers hain: {list(df.columns)}")

# ================== 3. TOPPERS ==================
elif option == "Toppers":
    st.markdown("<h1 class='header-text'>🏆 Class Hall of Fame</h1>", unsafe_allow_html=True)
    # Using dynamic or mock data
    mock_data = pd.DataFrame({
        'Name': ['Zoya', 'Aman', 'Sita', 'Karan', 'Rahul'],
        'math score': [98, 95, 82, 70, 45],
        'reading score': [92, 88, 95, 60, 50],
        'writing score': [96, 92, 90, 65, 48]
    })
    mock_data['avg'] = mock_data[['math score', 'reading score', 'writing score']].mean(axis=1)

    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.subheader("🥇 Top 3 Overall")
        toppers = mock_data.sort_values(by='avg', ascending=False).head(3)
        for i, row in toppers.iterrows():
            st.success(f"**Rank {i+1}: {row['Name']}** - {row['avg']:.1f}%")

    with c2:
        st.subheader("🎯 Subject Champions")
        subject = st.selectbox("Select Subject", ['math score', 'reading score', 'writing score'])
        champ = mock_data.loc[mock_data[subject].idxmax()]
        st.info(f"The highest marks in **{subject.title()}** is **{champ[subject]}**, scored by **{champ['Name']}**.")

# ================== 4. ANALYTICS ==================
elif option == "Analytics":
    st.markdown("<h1 class='header-text'>📊 Class Performance Analytics</h1>", unsafe_allow_html=True)
    
    # Generate random data for class insights
    class_data = pd.DataFrame(np.random.randint(40,100, size=(30, 3)), columns=['Math', 'Reading', 'Writing'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Class Mean", f"{class_data.values.mean():.1f}%")
    col2.metric("Active Students", "30")
    col3.metric("Pass Rate", "92%", "4%")
    
    st.divider()
    
    fig = px.box(class_data, template="plotly_dark", color_discrete_sequence=['#3b82f6'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    
    st.success("💡 **Teacher's Strategy:** Focus 15% more time on 'Reading' exercises to normalize class scores.")