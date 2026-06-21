import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="F1 Virtual Race Engineer", layout="wide")
st.title("🏎️ F1 25/26 Virtual Race Engineer")
st.markdown("**Setup-Focused Telemetry Analysis** — tells you exactly what to change on the car.")

uploaded_file = st.file_uploader("Upload Telemetry CSV", type=["csv"])

@st.cache_data
def load_data(file):
    if file is None:
        return None
    try:
        df = pd.read_csv(file, sep='\t')
        if 'validBin' in df.columns:
            df = df[df['validBin'] == 1].copy()
        if all(col in df.columns for col in ['velocity_X', 'velocity_Y', 'velocity_Z']):
            df['speed_kmh'] = np.sqrt(
                df['velocity_X']**2 + df['velocity_Y']**2 + df['velocity_Z']**2
            ) * 3.6
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def analyze_setup(df):
    if df is None or df.empty:
        st.warning("No valid data to analyze.")
        return

    st.subheader("🔧 Setup Recommendations")

    recommendations = []

    # High-speed aero balance
    if 'speed_kmh' in df.columns and 'gforce_Y' in df.columns:
        high_speed = df[df['speed_kmh'] > 180]
        if not high_speed.empty:
            avg_lat_g = high_speed['gforce_Y'].abs().mean()
            if avg_lat_g < 1.7:
                recommendations.append(("Rear Wing", "+4 to +6 clicks — car lacks rotation in high-speed corners"))
            elif avg_lat_g > 2.3:
                recommendations.append(("Front Wing", "-3 to -5 clicks — too much front grip / pushing at high speed"))

    # Mid-corner balance (yaw rate)
    if all(col in df.columns for col in ['angular_vel_Y', 'speed_kmh', 'throttle', 'brake']):
        mid_corner = df[
            (df['throttle'] < 0.1) & 
            (df['brake'] < 0.1) & 
            (df['speed_kmh'] > 90)
        ]
        if not mid_corner.empty:
            avg_yaw = mid_corner['angular_vel_Y'].abs().mean()
            if avg_yaw < 0.75:
                recommendations.append(("Front ARB", "Soften front ARB by 3-4 clicks"))
                recommendations.append(("Rear Wing", "+2 clicks for more rotation"))
            elif avg_yaw > 1.5:
                recommendations.append(("Rear ARB", "Stiffen rear ARB by 2-3 clicks"))
                recommendations.append(("Front Wing", "-2 clicks to reduce over-rotation"))

    # Corner exit traction
    if all(col in df.columns for col in ['throttle', 'wheel_speed_0', 'wheel_speed_1', 'speed_kmh']):
        exit_data = df[df['throttle'] > 0.6]
        if not exit_data.empty:
            rear_wheel_speed = exit_data[['wheel_speed_0', 'wheel_speed_1']].mean(axis=1) * 3.6
            slip = (rear_wheel_speed - exit_data['speed_kmh']).abs().mean()
            if slip > 12:
                recommendations.append(("Differential", "Increase on-throttle diff preload by 15-25%"))
                recommendations.append(("Rear Toe", "Add more toe-in"))

    # Braking stability
    if all(col in df.columns for col in ['brake', 'wheel_speed_2', 'wheel_speed_3', 'speed_kmh']):
        braking = df[df['brake'] > 0.7]
        if not braking.empty:
            front_wheel_speed = braking[['wheel_speed_2', 'wheel_speed_3']].mean(axis=1) * 3.6
            lockup = (braking['speed_kmh'] - front_wheel_speed).mean()
            if lockup > 18:
                recommendations.append(("Brake Bias", "Move brake bias 3-5% rearward"))

    if recommendations:
        for component, advice in recommendations:
            st.warning(f"**{component}**: {advice}")
    else:
        st.success("✅ Your current setup looks well balanced. No major changes recommended.")

    # Key metrics
    st.subheader("📊 Key Session Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'speed_kmh' in df.columns:
            st.metric("Max Speed", f"{df['speed_kmh'].max():.1f} km/h")
    
    with col2:
        if 'gforce_Y' in df.columns:
            st.metric("Peak Lateral G", f"{df['gforce_Y'].abs().max():.2f} g")
    
    with col3:
        brake_cols = ['brake_temp_0', 'brake_temp_1', 'brake_temp_2', 'brake_temp_3']
        if all(col in df.columns for col in brake_cols):
            max_brake = df[brake_cols].max().max()
            st.metric("Max Brake Temp", f"{max_brake:.0f} °C")
    
    with col4:
        if 'lapNum' in df.columns:
            st.metric("Laps Analyzed", df['lapNum'].nunique())

if uploaded_file is not None:
    df = load_data(uploaded_file)
    if df is not None:
        analyze_setup(df)
else:
    st.info("👆 Upload your F1 25/26 telemetry CSV to get setup recommendations.")
