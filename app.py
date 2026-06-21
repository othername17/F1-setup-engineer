import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="F1 Race Engineer v5", layout="wide")
st.title("🧑‍🔧 F1 Race Engineer v5")
st.caption("Extreme-setup detector added because your files prove insane numbers work amazingly")

uploaded_file = st.file_uploader("Drop CSV here", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep=None, engine='python')
    if 'validBin' in df.columns:
        df = df[df['validBin'] == 1].copy()
    
    df['speed_kmh'] = np.sqrt(df[['velocity_X','velocity_Y','velocity_Z']].pow(2).sum(axis=1)) * 3.6

    issues = []
    recs = []

    # Extreme setup detector
    front_wing = 0
    rear_wing = 0
    front_arb = 0
    rear_arb = 0
    if len(df) > 0:
        if 'wing_setup_0' in df.columns:
            front_wing = int(df['wing_setup_0'].iloc[0])
        if 'wing_setup_1' in df.columns:
            rear_wing = int(df['wing_setup_1'].iloc[0])
        if 'arb_setup_0' in df.columns:
            front_arb = int(df['arb_setup_0'].iloc[0])
        if 'arb_setup_1' in df.columns:
            rear_arb = int(df['arb_setup_1'].iloc[0])
    
    tyre_cols = [c for c in df.columns if any(x in c.lower() for x in ['tyre_wear', 'tyre_damage', 'tyre_blister'])]
    avg_wear = df[tyre_cols].mean().mean() if tyre_cols and len(df) > 0 else 5.0
    
    if (front_wing > 35 or rear_wing > 35 or front_arb > 15 or rear_arb > 15) and avg_wear < 2.0:
        recs.append("🔥 EXTREME SETUP EXPLOIT: Wings + ARBs maxed but car is stable + tires barely wear • This is the meta sweet spot")
        recs.append("PUSH FURTHER: Try front wing +2 more or rear ARB max on high-speed tracks • One-less-stop potential is real")
        issues.append("Your insane-looking setup is actually god-tier in this physics model")

    # High speed
    hs = df[df['speed_kmh'] > 205]
    if len(hs) > 70:
        lat = hs['gforce_Y'].abs().mean()
        if lat < 1.25:
            recs.append("HIGH SPEED: Reduce rear wing 4-7 clicks — too planted")
            issues.append("High-speed under-rotation")
        elif lat > 1.65:
            recs.append("HIGH SPEED: Add rear wing +4-6 clicks")

    # Mid-corner
    mid = df[(df['speed_kmh'] > 80) & (df['speed_kmh'] < 210)]
    if len(mid) > 50:
        yaw = mid['angular_vel_Y'].abs().mean()
        if yaw < 0.48:
            recs.append("MID-CORNER: Soften front ARB -2 or stiffen rear +2 — pushing")

    # Exit
    if 'wheel_speed_2' in df.columns:
        ex = df[df['throttle'] > 0.7]
        slip = (ex['wheel_speed_2'] - ex['speed_kmh']).abs().mean()
        if slip > 12:
            recs.append("EXIT: Increase diff preload +3 — wheelspin")

    st.subheader("Lap Diagnosis")
    for i in issues:
        st.error(i)
    if not issues:
        st.success("Setup is unusually effective despite extreme numbers")

    st.subheader("Setup Recommendations")
    for r in recs:
        st.warning(r)

    st.caption("v5 • Syntax fully fixed • Extreme detector added because your files prove it works")
else:
    st.info("Upload CSV")
