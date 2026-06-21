import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="F1 Race Engineer v3 - Actually Works", layout="wide")
st.title("F1 Automated Race Engineer v3")
st.caption("Real telemetry analysis. No more generic bullshit. Upload your CSV.")

uploaded_file = st.file_uploader("Drop your F1 2025/2026 telemetry CSV", type=["csv", "txt"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
    except:
        df = pd.read_csv(uploaded_file, sep='\t')

    # Filter valid data
    if 'validBin' in df.columns:
        df = df[df['validBin'] == 1].copy()

    # Calculate speed
    df['speed_kmh'] = np.sqrt(df['velocity_X']**2 + df['velocity_Y']**2 + df['velocity_Z']**2) * 3.6

    recommendations = []
    issues = []

    # === HIGH SPEED AERO (only trigger if actually sliding) ===
    high_speed = df[df['speed_kmh'] > 220]
    if len(high_speed) > 100:
        avg_lat = high_speed['gforce_Y'].abs().mean()
        if avg_lat > 1.55:
            recommendations.append("HIGH SPEED: +3 to +5 clicks rear wing — car is sliding too much above 220 km/h")
            issues.append("High-speed instability / understeer")
        elif avg_lat < 0.95:
            recommendations.append("HIGH SPEED: -2 to -4 clicks rear wing or + front wing — too planted, add rotation")
            issues.append("High-speed under-rotation (car won't turn)")

    # === MID-CORNER BALANCE (yaw rate) ===
    mid = df[(df['speed_kmh'] > 80) & (df['speed_kmh'] < 200)]
    if len(mid) > 50:
        avg_yaw = mid['angular_vel_Y'].abs().mean()
        if avg_yaw > 0.72:
            recommendations.append("MID-CORNER: Stiffen front ARB +1 click or soften rear ARB — oversteer detected")
            issues.append("Oversteer in mid-corner")
        elif avg_yaw < 0.38:
            recommendations.append("MID-CORNER: Soften front ARB -1 click or stiffen rear ARB — pushing / understeer")
            issues.append("Understeer / pushing in mid-corner")

    # === TRACTION ON EXIT ===
    exit_df = df[(df['throttle'] > 0.7) & (df['speed_kmh'] > 70)]
    if len(exit_df) > 30:
        for w in ['wheel_speed_0', 'wheel_speed_1', 'wheel_speed_2', 'wheel_speed_3']:
            if w in exit_df.columns:
                slip = (exit_df[w] - exit_df['speed_kmh']).mean()
                if slip > 15:
                    recommendations.append(f"TRACTION: +2 clicks diff on-throttle preload — wheelspin on exit (wheel {w[-1]})")
                    issues.append("Wheelspin / traction loss on corner exit")
                    break

    # === BRAKING ===
    brake_df = df[(df['brake'] > 0.5) & (df['speed_kmh'] > 50)]
    if len(brake_df) > 30:
        for w in ['wheel_speed_0', 'wheel_speed_1', 'wheel_speed_2', 'wheel_speed_3']:
            if w in brake_df.columns:
                drop = brake_df[w].diff().mean()
                if drop < -7:
                    recommendations.append("BRAKING: Move brake bias forward 1-2% — rear lock detected")
                    issues.append("Rear brake lockup")
                    break

    # Deduplicate
    seen = set()
    final_recs = [r for r in recommendations if not (r in seen or seen.add(r))]

    # Output
    st.subheader("What this lap actually shows")
    if issues:
        for i in issues:
            st.error(i)
    else:
        st.success("No major issues flagged in this sample. Car looks reasonably balanced at the points checked.")

    st.subheader("Setup Recommendations (only when symptoms exist)")
    if final_recs:
        for r in final_recs:
            st.warning(r)
    else:
        st.info("Nothing screaming for big changes based on the thresholds. Try a hotter lap or push harder.")

    # Quick stats
    st.subheader("Lap Stats")
    c1, c2, c3 = st.columns(3)
    c1.metric("Max Speed", f"{df['speed_kmh'].max():.0f} km/h")
    c2.metric("Avg Speed", f"{df['speed_kmh'].mean():.0f} km/h")
    c3.metric("Data Points", f"{len(df):,}")

else:
    st.info("Upload a CSV and I’ll give you real, lap-specific advice instead of the same two lines every time.")
