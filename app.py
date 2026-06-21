import streamlit as st
import pandas as pd
import numpy as np
from collections import defaultdict

st.set_page_config(page_title="F1 Virtual Race Engineer", layout="wide")
st.title("🏎️ F1 25/26 Virtual Race Engineer")
st.markdown("**Focused on Car Setup** — I tell you exactly what to change.")

# ========================== LOAD DATA ==========================
@st.cache_data
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, sep='\t')
        if 'validBin' in df.columns:
            df = df == 1 'velocity_Y' 'gforce_Y'].abs()
        return df
    except Exception as e:
        st.error(f"Failed to load file: {e}")
        return None

# ========================== ANALYSIS ==========================
def analyze_setup(df):
    recs = defaultdict(list)
    
    # 1. Aero / Wing Balance (High speed corners)
    high_speed = df[df['speed_kmh' 'g_lat'].mean()
        if avg_lat_g < 1.65:
            recs .append("**+4 to +6 clicks** - Car lacks rotation in high-speed corners")
        elif avg_lat_g > 2.35:
            recs .append("**-3 to -5 clicks** - Too much front grip / push at high speed")
    
    # 2. Mid-corner balance
    mid = df > 90) & (df < 0.15) & (df['brake'] < 0.15)]
    if not mid.empty:
        yaw_rate = mid .abs().mean()
        if yaw_rate < 0.75:
            recs .append("**Soften 3-4 clicks**")
            recs .append("**+2 clicks**")
        elif yaw_rate > 1.55:
            recs .append("**Stiffen 2-3 clicks**")
    
    # 3. Corner Exit Traction
    exit_data = df > 0.65 'wheel_speed_0','wheel_speed_1'].mean(axis=1)*3.6 - exit_data ).abs().mean()
        if rear_slip > 15:
            recs .append("**Increase on-throttle diff** by 15-25%")
            recs .append("**Add more toe-in**")
    
    # 4. Braking Stability
    braking = df > 0.75]
    if not braking.empty:
        front_lockup = ((braking - braking['wheel_speed_2','wheel_speed_3'].mean(axis=1)*3.6) > 20).mean()
        if front_lockup > 0.3:
            recs .append("**Move bias rearward** 3-5%")
    
    # ========================== DISPLAY ==========================
    st.subheader("🔧 Recommended Setup Changes")
    if recs:
        for part, suggestions in recs.items():
            for suggestion in suggestions:
                st.warning(f"**{part}**: {suggestion}")
    else:
        st.success("✅ Your current setup looks well balanced.")

    # Quick stats
    st.subheader("📊 Session Overview")
    cols = st.columns(4)
    cols[0 'speed_kmh' 1].metric("Peak Lateral G", f"{df .max():.2f}g")
    cols[2].metric("Highest Brake Temp", f"{df['brake_temp_0','brake_temp_1','brake_temp_2','brake_temp_3' 3].metric("Lap Count", df .nunique())

uploaded_file = st.file_uploader("Upload Telemetry CSV (SRT format)", type= )

if uploaded_file is not None:
    df = load_data(uploaded_file)
    if df is not None:
        analyze_setup(df)
else:
    st.info("👆 Upload a telemetry file to get setup recommendations.")
