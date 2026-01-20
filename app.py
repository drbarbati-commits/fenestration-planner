import streamlit as st
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import matplotlib.pyplot as plt
import numpy as np

# --- PAGE TITLE ---
st.set_page_config(page_title="PMEG Template Generator", layout="wide")
st.title("🎯 PMEG Template Generator")
st.subheader("Physician-Modified Endograft Planning Tool")

# --- SIDEBAR: GRAFT SELECTION ---
st.sidebar.header("1. Select Graft Template")
graft_type = st.sidebar.selectbox(
    "Graft Template",
    ["Device A (24mm × 145mm)", "Device B (28mm × 150mm)", "Device C (32mm × 155mm)"]
)

graft_specs = {
    "Device A (24mm × 145mm)": {"diameter": 24, "length": 145, "name": "A"},
    "Device B (28mm × 150mm)": {"diameter": 28, "length": 150, "name": "B"},
    "Device C (32mm × 155mm)": {"diameter": 32, "length": 155, "name": "C"}
}

graft = graft_specs[graft_type]
diameter = graft["diameter"]
length = graft["length"]
circumference = math.pi * diameter

st.sidebar.info(f"**Diameter:** {diameter}mm\n**Circumference:** {circumference:.1f}mm\n**Length:** {length}mm")

# --- VESSEL ORDERING ---
VESSEL_OPTIONS = [
    "Celiac trunk",
    "SMA", 
    "Right renal artery",
    "Left renal artery",
    "Accessory renal artery 1",
    "Accessory renal artery 2",
    "IMA"
]

VESSEL_SHORT = {
    "Celiac trunk": "CELIAC",
    "SMA": "SMA",
    "Right renal artery": "R-REN",
    "Left renal artery": "L-REN",
    "Accessory renal artery 1": "ACC-1",
    "Accessory renal artery 2": "ACC-2",
    "IMA": "IMA"
}

# --- ADD FENESTRATIONS ---
st.header("2. Add Fenestrations")
col1, col2 = st.columns(2)

with col1:
    vessel_type = st.selectbox("Vessel (anatomical order)", VESSEL_OPTIONS)
    distance = st.slider("Distance from Proximal End (mm)", 0, length, 50, 5,
                        help=f"0 = Proximal end (top), {length} = Distal end (bottom)")
    st.caption(f"📍 Position: {distance}mm from TOP of graft")

with col2:
    # CLOCK SELECTION
    hour = st.selectbox("Clock Position (12 = anterior)", [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], index=0)
    clock_pos = 0 if hour == 12 else hour * 30
    
    # Visual clock reference
    fig_clock, ax_clock = plt.subplots(figsize=(1.5, 1.5))
    circle = plt.Circle((0, 0), 1, color='lightgray', fill=False)
    ax_clock.add_patch(circle)
    ax_clock.plot([0, 0], [0.8, 1], 'r-', linewidth=3)
    ax_clock.text(0, 1.1, '12\nANT', ha='center', va='center', color='red', fontweight='bold', fontsize=8)
    ax_clock.set_xlim(-1.2, 1.2)
    ax_clock.set_ylim(-1.2, 1.2)
    ax_clock.axis('off')
    st.pyplot(fig_clock)
    
    st.success(f"Angle: {clock_pos}°")
    fen_size = st.number_input("Fenestration Diameter (mm)", 4.0, 12.0, 6.0, 0.5)

if st.button("➕ Add Fenestration"):
    if 'fens' not in st.session_state:
        st.session_state.fens = []
    
    # Distance collision check
    for f in st.session_state.fens:
        if abs(f['d'] - distance) < 4:
            st.error("⚠️ Too close to existing fenestration!")
            st.stop()
    
    st.session_state.fens.append({
        "v": vessel_type,
        "d": distance,
        "c": clock_pos,
        "s": fen_size
    })
    st.success(f"✅ Added {VESSEL_SHORT[vessel_type]}")
    st.rerun()

# --- DISPLAY LIST ---
if 'fens' in st.session_state and st.session_state.fens:
    st.write("**Current Fenestrations:**")
    for i, f in enumerate(st.session_state.fens):
        hour_disp = "12" if f['c'] == 0 else str(int(f['c'] / 30))
        col1, col2 = st.columns([5, 1])
        col1.write(f"🔴 {VESSEL_SHORT[f['v']]} | @{f['d']}mm | {hour_disp} o'clock | Ø{f['s']}mm")
        if col2.button("Delete", key=f"del_{i}"):
            st.session_state.fens.pop(i)
            st.rerun()

# --- LIVE VISUALIZATION ---
st.header("3
