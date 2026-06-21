import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="F1 Race Engineer v2", layout="wide")
st.title("F1 Automated Race Engineer — Proper Version")
st.caption("Upload your telemetry CSV. Gets specific advice based on what the lap actually shows. No more copy-paste bullshit.")

uploaded_file = st.file_uploader("Drop your F1 telemetry CSV here", type=["csv", "txt"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
    except:
        df = pd.read_csv(uploaded_file, sep='\t')

    # Clean + calculate speed
    if 'validBin' in df.columns:
        df = df[df['validBin'] == 1].copy()

    df['speed_kmh'] = np.sqrt(df['velocity_X']**2 + df['velocity_Y']**2 + df['velocity_Z']**2) * 3.6

    recommendations = []
    issues_found = []

    # === HIGH SPEED AERO ===
    high_speed = df[df['speed_kmh'] > 240]
    if len(high_speed) > 50:
        avg_lat = high_speed['gforce_Y'].abs().mean()
        if avg_lat > 1.9:
            recommendations.append("HIGH SPEED: Add +3 to +5 clicks rear wing — car is sliding too much at speed")
            issues_found.append("High-speed understeer / instability")
        elif avg_lat < 1.1:
            recommendations.append("HIGH SPEED: Reduce rear wing 2-4 clicks or add front wing — car feels planted but won't rotate")

    # === MID-CORNER BALANCE (yaw rate) ===
    mid_corner = df[(df['speed_kmh'] > 90) & (df['speed_kmh'] < 220) & (df['angular_vel_Y'].abs() > 0.4)]
    if len(mid_corner) > 30:
        avg_yaw = mid_corner['angular_vel_Y'].mean()
        if avg_yaw > 0.85:
            recommendations.append("MID-CORNER: Stiffen front ARB +1 or soften rear ARB — oversteer detected")
            issues_found.append("Oversteer in mid-corner")
        elif avg_yaw < 0.35:
            recommendations.append("MID-CORNER: Soften front ARB -1 or stiffen rear ARB — understeer / pushing")
            issues_found.append("Understeer in mid-corner")

    # === TRACTION ON EXIT ===
    exit_phase = df[(df['throttle'] > 0.75) & (df['speed_kmh'] > 80)]
    if len(exit_phase) > 40:
        for wheel in ['wheel_speed_0', 'wheel_speed_1', 'wheel_speed_2', 'wheel_speed_3']:
            if wheel in exit_phase.columns:
                avg_slip = (exit_phase[wheel] - exit_phase['speed_kmh']).mean()
                if avg_slip > 18:
                    recommendations.append(f"TRACTION: Increase differential on-throttle preload +2 clicks (wheel {wheel[-1]})")
                    issues_found.append("Wheelspin on corner exit")
                    break

    # === BRAKING STABILITY ===
    braking = df[(df['brake'] > 0.6) & (df['speed_kmh'] > 60)]
    if len(braking) > 30:
        lock_detected = False
        for wheel in ['wheel_speed_0', 'wheel_speed_1', 'wheel_speed_2', 'wheel_speed_3']:
            if wheel in braking.columns:
                speed_drop = braking[wheel].diff().mean()
                if speed_drop < -8:
                    lock_detected = True
                    break
        if lock_detected:
            recommendations.append("BRAKING: Move brake bias forward 1-2% or reduce rear brake pressure — rear lock detected")
            issues_found.append("Brake lockup")

    # === Remove duplicates while keeping order ===
    seen = set()
    final_recs = []
    for rec in recommendations:
        if rec not in seen:
            seen.add(rec)
            final_recs.append(rec)

    # === OUTPUT ===
    st.subheader("What the lap actually shows")
    if issues_found:
        for issue in issues_found:
            st.error(issue)
    else:
        st.success("No major balance issues detected in this lap.")

    st.subheader("Setup Recommendations")
    if final_recs:
        for rec in final_recs:
            st.warning(rec)
    else:
        st.info("Car looks reasonably balanced. Try a different lap or push harder to see clearer issues.")

    # Quick metrics
    st.subheader("Quick Lap Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Max Speed", f"{df['speed_kmh'].max():.0f} km/h")
    col2.metric("Avg Speed", f"{df['speed_kmh'].mean():.0f} km/h")
    col3.metric("Samples Analyzed", len(df))

else:
    st.info("Upload a CSV from F1 2025 or 2026 and I'll give you real, lap-specific setup advice instead of the same two lines every time.")
