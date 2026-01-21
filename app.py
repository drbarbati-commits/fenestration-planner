import streamlit as st
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import matplotlib.pyplot as plt

# --- PAGE TITLE ---
st.set_page_config(page_title="PMEG Template Generator", layout="wide")
st.title("🎯 PMEG Template Generator")
st.subheader("Physician-Modified Endograft Planning Tool")

# --- SIDEBAR: GRAFT SELECTION ---
st.sidebar.header("1. Select Graft Template")
graft_type = st.sidebar.selectbox("Graft Template", ["Device A (24mm × 145mm)", "Device B (28mm × 150mm)", "Device C (32mm × 155mm)"])

graft_specs = {
    "Device A (24mm × 145mm)": {"diameter": 24, "length": 145, "name": "A"},
    "Device B (28mm × 150mm)": {"diameter": 28, "length": 150, "name": "B"},
    "Device C (32mm × 155mm)": {"diameter": 32, "length": 155, "name": "C"}
}

graft = graft_specs[graft_type]
diameter = graft["diameter"]
length = graft["length"]
circumference = math.pi * diameter

st.sidebar.info(f"Diameter: {diameter}mm\nCircumference: {circumference:.1f}mm\nLength: {length}mm")

# --- VESSEL ORDERING ---
VESSEL_OPTIONS = ["Celiac trunk", "SMA", "Right renal artery", "Left renal artery", "Accessory renal artery 1", "Accessory renal artery 2", "IMA"]
VESSEL_SHORT = {"Celiac trunk": "CELIAC", "SMA": "SMA", "Right renal artery": "R-REN", "Left renal artery": "L-REN", "Accessory renal artery 1": "ACC-1", "Accessory renal artery 2": "ACC-2", "IMA": "IMA"}

# --- ADD FENESTRATIONS ---
st.header("2. Add Fenestrations")
col1, col2 = st.columns(2)

with col1:
    vessel_type = st.selectbox("Vessel (anatomical order)", VESSEL_OPTIONS)
    distance = st.slider("Distance from Proximal End (mm)", 0, length, 50, 5, help=f"0 = TOP (proximal), {length} = BOTTOM (distal)")
    st.caption(f"📍 {distance}mm from TOP")

with col2:
    # CLOCK: 6 = anterior = 0°
    hour = st.selectbox("Clock Position (6 = anterior)", [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], index=6)
    # CONVERSION: 6 o'clock = 0°, 12 o'clock = 180°
    clock_pos = ((hour - 6) % 12) * 30  # 6=0°, 12=180°, 3=90°, 9=270°
    st.success(f"Angle: {clock_pos}°")
    
    # Visual clock showing 6 as anterior
    fig_clock, ax_clock = plt.subplots(figsize=(1.5, 1.5))
    circle = plt.Circle((0, 0), 1, color='lightgray', fill=False)
    ax_clock.add_patch(circle)
    ax_clock.plot([0, 0], [-0.8, -1], 'r-', linewidth=3)
    ax_clock.text(0, -1.1, '6\nANT', ha='center', va='center', color='red', fontweight='bold', fontsize=8)
    ax_clock.set_xlim(-1.2, 1.2)
    ax_clock.set_ylim(-1.2, 1.2)
    ax_clock.axis('off')
    st.pyplot(fig_clock)
    
    fen_size = st.number_input("Fenestration Diameter (mm)", 4.0, 12.0, 6.0, 0.5)

if st.button("➕ Add Fenestration"):
    if 'fens' not in st.session_state:
        st.session_state.fens = []
    for f in st.session_state.fens:
        if abs(f['d'] - distance) < 4:
            st.error("Too close to existing fenestration!")
            st.stop()
    st.session_state.fens.append({"v": vessel_type, "d": distance, "c": clock_pos, "s": fen_size})
    st.success(f"Added {VESSEL_SHORT[vessel_type]}")
    st.rerun()

# --- DISPLAY LIST ---
if 'fens' in st.session_state and st.session_state.fens:
    st.write("Current Fenestrations:")
    for i, f in enumerate(st.session_state.fens):
        hour_display = "6" if f['c'] == 0 else str(int(((f['c']/30) + 6) % 12))
        col1, col2 = st.columns([5, 1])
        col1.write(f"🔴 {VESSEL_SHORT[f['v']]} | @{f['d']}mm | {hour_display} o'clock | Ø{f['s']}mm")
        if col2.button("Delete", key=f"del_{i}"):
            st.session_state.fens.pop(i)
            st.rerun()

# --- LIVE VISUALIZATION ---
st.header("3. Live Graft Preview")

if 'fens' in st.session_state and st.session_state.fens:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, circumference)
    ax.set_ylim(0, length)
    
    # Graft outline
    ax.plot([0, circumference, circumference, 0, 0], [0, 0, length, length, 0], 'k-', linewidth=3)
    
    # Stent rings
    for i in range(0, length, 15):
        ax.plot([0, circumference], [i, i], 'gray', linestyle=':', alpha=0.5)
        ax.text(-8, i, f"{i}", ha='right', va='center', fontsize=8)
    
    # Radiopaque markers
    for pos in [30, 60, 90, 120]:
        ax.plot([0, circumference], [pos, pos], 'gold', linewidth=4, alpha=0.8)
        ax.text(circumference + 5, pos, "MARKER", fontsize=8, color='gold', fontweight='bold')
    
    # Title in upper-left
    ax.text(5, length - 10, f"UNROLLED GRAFT\n{diameter}mm × {length}mm", fontsize=12, fontweight='bold', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    # Proximal label in upper-right
    ax.text(circumference - 10, length - 10, "PROXIMAL END\n(0mm)", ha='right', fontsize=11, fontweight='bold', 
            color='red', bbox=dict(boxstyle="round,pad=0.3", facecolor="pink", alpha=0.7))
    
    # Distal label in lower-right
    ax.text(circumference - 10, 10, "DISTAL END\n({}mm)".format(length), ha='right', fontsize=11, fontweight='bold', 
            color='blue', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
    
    # Fenestrations (smaller distance = higher position)
    colors = {"Celiac trunk": '#FF6B6B', "SMA": '#4ECDC4', "Right renal artery": '#45B7D1', "Left renal artery": '#96CEB4', "Accessory renal artery 1": '#FFEAA7', "Accessory renal artery 2": '#DDA0DD', "IMA": '#FFB347'}
    for f in st.session_state.fens:
        x = (f['c'] / 360) * circumference
        y = f['d']
        circle = plt.Circle((x, y), f['s'], color=colors.get(f['v'], 'black'), alpha=0.6, fill=True)
        ax.add_patch(circle)
        
        hour_display = "6" if f['c'] == 0 else str(int(((f['c']/30) + 6) % 12))
        # SIMPLIFIED: Remove bbox parameters
        ax.text(x, y, VESSEL_SHORT[f['v']], ha='center', va='center', fontsize=9, fontweight='bold', color='black')
        ax.text(x, y + f['s'] + 3, f"Ø{f['s']}mm @{f['d']}mm\n{hour_display} o'clock", ha='center', fontsize=7)
    
    ax.invert_yaxis()  # Flip AFTER adding elements
    
    ax.set_xlabel("Circumference (mm)", fontsize=12)
    ax.set_ylabel("Distance from Proximal End (mm)", fontsize=12)
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
else:
    st.info("Add fenestrations to see live preview")

# --- PDF GENERATOR ---
st.header("4. Generate Template")
st.caption(f"Print width must be {circumference:.1f}mm")

if st.button("🖨️ Create PDF", type="primary"):
    width_mm = circumference
    height_mm = length
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    x_offset = 50
    y_offset = 50
    
    c.rect(x_offset, y_offset, width_mm, height_mm, stroke=1, fill=0)
    
    for i in range(0, length, 15):
        c.line(x_offset, y_offset + i, x_offset + width_mm, y_offset + i)
        c.setFont("Helvetica", 6)
        c.drawString(x_offset - 15, y_offset + i - 1, f"{i}")
    
    c.setStrokeColorRGB(1, 0.84, 0)
    c.setLineWidth(2)
    for pos in [30, 60, 90, 120]:
        c.line(x_offset, y_offset + pos, x_offset + width_mm, y_offset + pos)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x_offset + width_mm + 5, y_offset + pos - 2, "MARKER")
    
    c.setStrokeColorRGB(0, 0, 0)
    for f in st.session_state.fens:
        x = x_offset + ((f['c'] + 180) % 360) / 360 * width_mm
        y = y_offset + (height_mm - f['d'])
        r = f['s']
        c.circle(x, y, r, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x - 15, y + r + 3, f"{VESSEL_SHORT[f['v']]} Ø{f['s']}mm @{f['d']}mm")
    
    c.setStrokeColorRGB(1, 0, 0)
    c.setLineWidth(3)
    for y_pos in [y_offset + height_mm + 10, y_offset + height_mm/2, y_offset - 10]:
        c.line(x_offset, y_pos, x_offset + 10, y_pos)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_offset + 12, y_pos - 2, "10mm")
    
    c.line(x_offset - 10, y_offset, x_offset - 10, y_offset + 10)
    c.drawString(x_offset - 25, y_offset + 5, "10mm")
    
    c.setStrokeColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10)
    instr = ["CRITICAL PRINTING INSTRUCTIONS:", "1. Print at 100% scale (NO 'Fit to Page')", "2. Verify ALL 10mm bars measure exactly 10mm", "3. Cut along black rectangle outline", "4. Wrap into cylinder - edges must meet", f"5. Expected cylinder diameter: {diameter:.1f}mm"]
    y_text = y_offset + height_mm + 25
    for line in instr:
        c.drawString(x_offset, y_text, line)
        y_text += 12
    
    c.save()
    pdf_buffer.seek(0)
    
    st.download_button(label="📥 Download PDF", data=pdf_buffer, file_name=f"PMEG_Template_{graft['name']}_{diameter}mm.pdf", mime="application/pdf")
    st.success("✅ PDF generated")
    st.warning("⚠️ PRINT: 'Actual Size' or '100%'")

# --- VERIFICATION ---
st.header("5. Verification")
st.info(f"Print width = {circumference:.1f}mm\nPrint height = {length}mm\nCylinder diameter = {diameter}mm")

st.caption("Proof-of-Concept | Validate before use")
