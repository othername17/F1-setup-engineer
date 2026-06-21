import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="F1 Race Engineer v5", layout="wide")
st.title("🧑‍🔧 F1 Race Engineer v5")
st.caption("Now detects extreme-but-effective setups like yours • Exploits the weird physics you found")

uploaded_file = st.file_uploader("Drop CSV here", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep=None, engine='python')
    if 'validBin' in df.columns:
        df = df[df['validBin'] == 1].copy()
    
    df['speed_kmh'] = np.sqrt(df[['velocity_X','velocity_Y','velocity_Z']].pow(2).sum(axis=1)) * 3.6

    issues = []
    recs = []

    # Extreme setup detector (added because your Montreal + Silverstone files show insane numbers that actually work)
    front_wing = int(df['wing_setup_0'].iloc[0]) if 'wing_setup_0' in df.columns and len(df) > 0 else 0
    rear_wing = int(df['wing_setup_1'].iloc[0]) if 'wing_setup_1' in df.columns and len(df) > 0 else 0
    front_arb = int(df['arb_setup_0'].iloc[0]) if 'arb_setup_0' in df.columns and len(df) > 0 else 0
    rear_arb = int(df['arb_setup_1'].iloc[0]) if 'arb_setup_1' in
