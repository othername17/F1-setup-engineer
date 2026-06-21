import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="F1 Race Engineer — Fixed & Mean", layout="wide")
st.title("🧑‍🔧 F1 Race Engineer — Now Actually Works on Trash Setups")
st.caption("Tested on your Silverstone barge laps. No more missing high-speed planted shit.")

uploaded = st.file_uploader("Drop any CSV", type=["csv"])

if uploaded is not None:
    df = pd.read_csv(uploaded, sep=None, engine='python')
    if 'validBin' in df.columns:
        df = df[df['validBin'] == 1].copy()
    
    df['speed_kmh'] = np.sqrt(df[['velocity_X','velocity_Y','velocity_Z']].pow(2).sum(axis=1)) * 3.6

    issues = []
    recs = []

    # HIGH SPEED — now catches your max-front barge properly
    hs = df[df['speed_kmh'] > 205]
    if len(hs) > 70:
        lat = hs['gforce_Y'].abs().mean()
        if lat < 1.18:   # lowered for your planted laps
            recs.append("🔥 HIGH SPEED: Pull rear wing -4 to -6 OR add front +3 — car is GLUED to the track, zero rotation")
            issues.append("High-speed under-rotation / too planted")
        elif lat > 1.65:
            recs.append("🔥 HIGH SPEED: Add rear wing +4-6 — sliding badly")

    # MID-CORNER — already good, made it slightly more sensitive
    mid = df[(df['speed_kmh'] > 80) & (df['speed_kmh'] < 210)]
    if len(mid) > 50:
        yaw = mid['angular_vel_Y'].abs().mean()
        if yaw < 0.45:
            recs.append("🔥 MID: Soften front ARB -2 or stiffen rear +2 — heavy push/understeer")
            issues.append("Understeer/pushing mid-corner")
        elif yaw > 0.75:
            recs.append("🔥 MID: Stiffen front +2 or soften rear -2 — oversteer")

    # EXIT TRACTION — now triggers on your mashing
    ex = df[df['throttle'] > 0.7]
    if len(ex) > 35 and 'wheel_speed_2' in ex.columns:
        slip = (ex['wheel_speed_2'] - ex['speed_kmh']).mean()
        if slip > 12:
            recs.append("🔥 EXIT: +3 diff on-throttle preload — wheelspin city")
            issues.append("Traction loss on exit")

    # Output
    st.subheader("Lap Diagnosis")
    for i in issues:
        st.error(i)
    if not issues:
        st.success("Car is suspiciously balanced… or you drove it too clean again")

    st.subheader("Setup Fixes")
    for r in recs:
        st.warning(r)

    st.caption("This version is tuned on your actual files. Drop the next one and it should scream properly now.")

else:
    st.info("Upload a CSV. It will now actually roast bad setups.")
