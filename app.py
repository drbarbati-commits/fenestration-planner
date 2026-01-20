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

# --- VESSEL ORDERING & SHORT LABELS ---
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
    "Right renal artery": "R-RENAL",
    "Left renal artery": "L-RENAL",
    "Accessory renal artery 1": "ACC-REN1",
    "Accessory renal artery 2": "ACC-REN2",
    "IMA": "IMA"
}

# --- MAIN: ADD FENESTRATIONS ---
st.header("2. Add Fenestrations")
col1, col2 = st.columns(2)

with col1:
    vessel_type = st.selectbox("Vessel (anatomical order)", VESSEL_OPTIONS)
    
    # DISTANCE SLIDER WITH VISUAL FEEDBACK
    st.write("**Distance from Proximal End (mm)**")
    distance = st.slider(
        "Slide to position along graft length",
        0, length, 50, 5,
        help="0 = Proximal end (top), {} = Distal end (bottom)".format(length)
    )
    st.caption(f"📍 Position: {distance}mm from proximal end (top)")

with col2:
    # CLOCK INTERFACE
    st.write("**Clock Position**")
    
    # Create a visual clock reference
    clock_col1, clock_col2 = st.columns([1, 2])
    with clock_col1:
        hour = st.selectbox(
            "Hour (12 = anterior)",
            [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            index=0  # Default to 12
        )
        # Convert hour to degrees
        if hour == 12:
            clock_pos = 0
        else:
            clock_pos = hour * 30
        st.success(f"Selected: {hour} o'clock ({clock_pos}°)")
    
    with clock_col2:
        st.caption("Visual reference:")
        # Show a simple clock diagram
        fig_clock, ax_clock = plt.subplots(figsize=(2, 2))
        circle = plt.Circle((0, 0), 1, color='lightgray', fill=False)
        ax_clock.add_patch(circle)
        # Mark 12 o'clock (anterior)
        ax_clock.plot([0, 0], [0.8, 1], 'r-', linewidth=3)
        ax_clock.text(0, 1.1, '12\n(ANT)', ha='center', va='center', color='red', fontweight='bold')
        ax_clock.set_xlim(-1.2, 1.2)
        ax_clock.set_ylim(-1.2, 1.2)
        ax_clock.axis('off')
        st.pyplot(fig_clock)
    
    fen_size = st.number_input("Fenestration Diameter (mm)", 4.0, 12.0, 6.0, 0.5)

if st.button("➕ Add Fenestration"):
    if 'fens' not in st.session_state:
        st.session_state.fens = []
    
    # Collision detection (distance-based)
    for f in st.session_state.fens:
        if abs(f['d'] - distance) < 4:
            st.error("⚠️ Warning: Within 4mm of existing fenestration!")
            st.stop()
    
    st.session_state.fens.append({
        "v": vessel_type,
        "d": distance,
        "c": clock_pos,
        "s": fen_size
    })
    st.success(f"✅ Added {vessel_type} at {hour} o'clock")
    st.rerun()

# --- DISPLAY LIST ---
if 'fens' in st.session_state and st.session_state.fens:
    st.write("**Current Fenestrations:**")
    for i, f in enumerate(st.session_state.fens):
        hour_display = "12" if f['c'] == 0 else str(int(f['c'] / 30))
        col1, col2 = st.columns([5, 1])
        col1.write(f"🔴 {VESSEL_SHORT[f['v']]} | @{f['d']}mm | {hour_display} o'clock | Ø{f['s']}mm")
        if col2.button("Delete", key=f"del_{i}"):
            st.session_state.fens.pop(i)
            st.rerun()

# --- LIVE VISUALIZATION (PROXIMAL AT TOP) ---
st.header("3. Live Graft Preview")
st.caption("❗**IMPORTANT**: Proximal end is at TOP of image")

if 'fens' in st.session_state and st.session_state.fens:
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Draw unrolled graft rectangle (proximal at TOP)
    ax.set_ylim(length, 0)  # Invert Y-axis
    
    # Graft outline
    ax.plot([0, circumference, circumference, 0, 0], 
            [0, 0, length, length, 0], 
            'k-', linewidth=3, label="Graft Edge")
    
    # Stent rings (every 15mm)
    for i in range(0, length, 15):
        ax.plot([0, circumference], [i, i], 'gray', linestyle=':', alpha=0.5)
        ax.text(-5, i, f"{i}", ha='right', va='center', fontsize=8)
    
    # Radiopaque markers
    for pos in [30, 60, 90, 120]:
        ax.plot([0, circumference], [pos, pos], 'gold', linewidth=4, alpha=0.8)
        ax.text(circumference + 5, pos, "MARKER", fontsize=8, color='gold', fontweight='bold')
    
    # Proximal/Distal labels
    ax.text(circumference/2, -5, "PROXIMAL END (0mm)", ha='center', fontsize=12, 
            fontweight='bold', color='red', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="pink", alpha=0.5))
    ax.text(circumference/2, length+5, "DISTAL END ({}mm)".format(length), ha='center', fontsize=12, 
            fontweight='bold', color='blue',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
    
    # Fenestrations
    colors = {
        "Celiac trunk": '#FF6B6B',
        "SMA": '#4ECDC4',
        "Right renal artery": '#45B7D1',
        "Left renal artery": '#96CEB4',
        "Accessory renal artery 1": '#FFEAA7',
        "Accessory renal artery 2": '#DDA0DD',
        "IMA": '#FFB347'
    }
    
    for f in st.session_state.fens:
        x = (f['c'] / 360) * circumference
        y = length - f['d']  # Invert Y to place proximal at top
        
        # Draw circle
        circle = plt.Circle((x, y), f['s'], 
                           color=colors.get(f['v'], 'black'), 
                           alpha=0.6, fill=True, linewidth=2)
        ax.ax.add_patch(circle)
        
        # Label vessel (short form)
        hour_display = "12" if f['c'] == 0 else str(int(f['c'] / 30))
        ax.text(x, y, VESSEL_SHORT[f['v']], ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white',
                bbox=dict(boxstyle="round,pad=0.2", facecolor="black", alpha=0.5))
        
        # Add details below circle
        ax.text(x, y + f['s'] + 3, 
                f"Ø{f['s']}mm @{f['d']}mm\n{hour_display} o'clock", 
                ha='center', fontsize=7)
    
    # Axes labels
    ax.set_xlim(0, circumference)
    ax.set_xlabel("Circumference (mm)", fontsize=12)
    ax.set_ylabel("Distance from Proximal End (mm)", fontsize=12)
    ax.set_title(f"UNROLLED GRAFT TEMPLATE\n{diameter}mm × {length}mm | Scale: 1:1", 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    
    # Scale bar (top left)
    ax.plot([10, 20], [length-10, length-10], 'k-', linewidth=4)
    ax.text(15, length-15, "10mm", ha='center', fontsize=10, fontweight='bold')
    
    st.pyplot(fig)
else:
    st.info("Add fenestrations to see live preview")

# --- PDF GENERATOR (EXACT SCALE) ---
st.header("4. Generate Template - CRITICAL: Print at EXACT Scale")
st.caption("📏 **The printed width must equal {:.1f}mm (circumference)**".format(circumference))

if st.button("🖨️ Create PDF Template", type="primary"):
    width_mm = circumference
    height_mm = length
    
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    
    # Position with margins
    x_offset = 50
    y_offset = 50
    
    # Graft rectangle (exact mm dimensions)
    c.rect(x_offset, y_offset, width_mm, height_mm, stroke=1, fill=0)
    
    # Stent rings + distance labels
    for i in range(0, length, 15):
        c.line(x_offset, y_offset + i,
