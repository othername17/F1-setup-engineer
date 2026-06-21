import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="F1 Race Engineer v4 — Fixed & Mean", layout="wide")
st.title("🧑‍🔧 F1 Race Engineer v4 — Fixed & Mean")
st.caption("Tuned on your Silverstone barge laps • Now catches high-speed planted + mid push + exit spin")

uploaded_file = st.file_uploader("Drop your F1 2026 CSV here", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep=None, engine='python')
    if 'validBin' in df.columns:
        df = df[df['validBin'] == 1].copy()
    
    # Speed calculation
    df['speed_kmh'] = np.sqrt(df[['velocity_X','velocity_Y','velocity_Z']].pow(2).sum(axis=1)) * 3.6

    issues = []
    recs = set()  # dedup

    # HIGH SPEED - tuned for your max-front glued shit
    hs = df[df['speed_kmh'] > 205]
    if len(hs) > 70:
        lat = hs['gforce_Y'].abs().mean()
        if lat < 1.25:
            recs.add("🔥 HIGH SPEED: Pull rear wing -5 to -8 clicks — car is WAY too planted, zero rotation")
            issues.append("High-speed under-rotation (too much front wing)")
        elif lat > 1.65:
            recs.add("🔥 HIGH SPEED: Add rear wing +5 — sliding badly")

    # MID-CORNER
    mid = df[(df['speed_kmh'] > 80) & (df['speed_kmh'] < 210)]
    if len(mid) > 50:
        yaw = mid['angular_vel_Y'].abs().mean()
        if yaw < 0.48:
            recs.add("🔥 MID-CORNER: Soften front ARB -2 or stiffen rear +2 — heavy push/understeer")
            issues.append("Understeer / pushing in mid-corner")

    # EXIT TRACTION
    ex = df[df['throttle'] > 0.7]
    if len(ex) > 35 and 'wheel_speed_2' in ex.columns:
        slip = (ex['wheel_speed_2'] - ex['speed_kmh']).mean()
        if slip > 12:
            recs.add("🔥 EXIT: Increase diff on-throttle preload +3 — wheelspin city")
            issues.append("Traction loss on exit")

    # BRAKING (lockup check)
    br = df[df['brake'] > 0.6]
    if len(br) > 20 and 'wheel_speed_0' in br.columns:
        lock = (br['speed_kmh'] - br['wheel_speed_0']).mean()
        if lock > 8:
            recs.add("🔥 BRAKING: Move brake bias forward 5-8% — front locking")
            issues.append("Brake lockup")

    # Output
    st.subheader("What this lap actually shows")
    if issues:
        for i in issues:
            st.error(i)
    else:
        st.success("Car is suspiciously good… or you drove it too clean again")

    st.subheader("Setup Recommendations")
    for r in recs:
        st.warning(r)

    st.caption("Full functional version • No spam • Tuned on your exact files • Drop next CSV to test")
else:
    st.info("Upload the CSV and it will roast the setup properly now.")
