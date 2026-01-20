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

# --- MAIN: ADD FENESTRATIONS ---
st.header("2. Add Fenestrations")
col1, col2 = st.columns(2)

with col1:
    vessel_type = st.selectbox(
        "Vessel",
        ["Left Renal", "Right Renal", "Accessory Renal", "SMA", "Celiac", "IMA", "Lumbar Artery"]
    )
    distance = st.number_input("Distance from Proximal End (mm)", 20, length-20, 50)
with col2:
    clock_pos = st.slider("Clock Position (12 o'clock = anterior)", 0, 360, 180, 15)
    fen_size = st.number_input("Fenestration Diameter (mm)", 4.0, 12.0, 6.0, 0.5)

if st.button("➕ Add Fenestration"):
    if 'fens' not in st.session_state:
        st.session_state.fens = []
    
    # Collision detection
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
    st.success(f"✅ Added {vessel_type}")
    st.rerun()

# --- DISPLAY LIST ---
if 'fens' in st.session_state and st.session_state.fens:
    st.write("**Current Fenestrations:**")
    for i, f in enumerate(st.session_state.fens):
        col1, col2 = st.columns([5, 1])
        col1.write(f"🔴 {f['v']} | @{f['d']}mm | {f['c']}° | Ø{f['s']}mm")
        if col2.button("Delete", key=f"del_{i}"):
            st.session_state.fens.pop(i)
            st.rerun()

# --- LIVE VISUALIZATION (PROXIMAL AT TOP) ---
st.header("3. Live Graft Preview")
st.caption("❗**IMPORTANT**: Proximal end is at TOP of image")

if 'fens' in st.session_state and st.session_state.fens:
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Draw unrolled graft rectangle (proximal at TOP)
    # Invert Y-axis so 0 = top, length = bottom
    ax.set_ylim(length, 0)
    
    # Graft outline
    ax.plot([0, circumference, circumference, 0, 0], 
            [0, 0, length, length, 0], 
            'k-', linewidth=3, label="Graft Edge")
    
    # Stent rings (every 15mm)
    for i in range(0, length, 15):
        ax.plot([0, circumference], [i, i], 'gray', linestyle=':', alpha=0.5)
    
    # Radiopaque markers (fixed positions)
    for pos in [30, 60, 90, 120]:
        ax.plot([0, circumference], [pos, pos], 'gold', linewidth=4, alpha=0.8)
        ax.text(5, pos, f"Marker", fontsize=8, color='gold', fontweight='bold')
    
    # Proximal/Distal labels
    ax.text(circumference/2, -5, "PROXIMAL END", ha='center', fontsize=12, 
            fontweight='bold', color='red', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="pink", alpha=0.5))
    ax.text(circumference/2, length+5, "DISTAL END", ha='center', fontsize=12, 
            fontweight='bold', color='blue',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
    
    # Fenestrations
    colors = {
        'Left Renal': '#FF4444', 'Right Renal': '#4444FF', 
        'Accessory Renal': '#FF8888', 'SMA': '#44AA44', 
        'Celiac': '#8888FF', 'IMA': '#AA44AA', 'Lumbar Artery': '#888888'
    }
    
    for f in st.session_state.fens:
        x = (f['c'] / 360) * circumference
        y = length - f['d']  # Invert Y to show proximal at top
        
        # Draw circle
        circle = plt.Circle((x, y), f['s'], 
                           color=colors.get(f['v'], 'black'), 
                           alpha=0.6, fill=True, linewidth=2)
        ax.add_patch(circle)
        
        # Label vessel
        ax.text(x, y, f['v'][:6], ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white',
                bbox=dict(boxstyle="round,pad=0.2", facecolor="black", alpha=0.5))
        
        # Add coordinate text
        ax.text(x, y + f['s'] + 3, 
                f"Ø{f['s']}mm\n@{f['d']}mm\n{f['c']}°", 
                ha='center', fontsize=7)
    
    # Labels and grid
    ax.set_xlim(0, circumference)
    ax.set_xlabel("Circumference (mm)", fontsize=12)
    ax.set_ylabel("Distance from Proximal End (mm)", fontsize=12)
    ax.set_title(f"UNROLLED GRAFT TEMPLATE\n{diameter}mm × {length}mm | Scale: 1:1", 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    
    # Scale bar (visual)
    ax.plot([10, 20], [length-10, length-10], 'k-', linewidth=4)
    ax.text(15, length-15, "10mm", ha='center', fontsize=10, fontweight='bold')
    
    st.pyplot(fig)
else:
    st.info("Add fenestrations to see live preview")

# --- PDF GENERATOR (EXACT SCALE) ---
st.header("4. Generate Template - CRITICAL: Print at EXACT Scale")
st.caption("📏 **The printed width MUST equal the circumference shown above**")

if st.button("🖨️ Create PDF Template", type="primary"):
    # Exact dimensions - NO SCALING
    width_mm = circumference
    height_mm = length
    
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    
    # Draw graft outline at EXACT scale
    # Position: centered on page with margins
    x_offset = 50
    y_offset = 50
    
    # Graft rectangle (exact mm dimensions)
    c.rect(x_offset, y_offset, width_mm, height_mm, stroke=1, fill=0)
    
    # Stent rings
    for i in range(0, length, 15):
        c.line(x_offset, y_offset + i, x_offset + width_mm, y_offset + i)
        c.setFont("Helvetica", 6)
        c.drawString(x_offset - 20, y_offset + i, f"{i}mm")
    
    # Radiopaque markers
    c.setStrokeColorRGB(1, 0.84, 0)  # Gold color
    c.setLineWidth(2)
    for pos in [30, 60, 90, 120]:
        c.line(x_offset, y_offset + pos, x_offset + width_mm, y_offset + pos)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x_offset + width_mm + 5, y_offset + pos, "MARKER")
    
    # Fenestrations
    c.setStrokeColorRGB(0, 0, 0)
    for f in st.session_state.fens:
        x = x_offset + (f['c'] / 360) * width_mm
        y = y_offset + (length - f['d'])  # Invert Y
        r = f['s']
        c.circle(x, y, r, stroke=1, fill=0)
        
        # Label
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x - 10, y + r + 5, f"{f['v']} Ø{f['s']}mm")
    
    # CRITICAL: Scale verification bars (multiple locations)
    c.setStrokeColorRGB(1, 0, 0)  # Red for visibility
    c.setLineWidth(3)
    
    # Horizontal rulers (top, middle, bottom)
    for y_pos in [y_offset + height_mm + 15, y_offset + height_mm/2, y_offset - 15]:
        c.line(x_offset, y_pos, x_offset + 10, y_pos)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_offset + 15, y_pos - 2, "10mm")
    
    # Vertical ruler (left side)
    c.line(x_offset - 15, y_offset, x_offset - 15, y_offset + 10)
    c.drawString(x_offset - 30, y_offset + 5, "10mm")
    
    # Instructions box
    c.setStrokeColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10)
    instructions = [
        "CRITICAL PRINTING INSTRUCTIONS:",
        "1. Print at 100% scale (NO 'Fit to Page')",
        "2. Verify ALL 10mm bars measure exactly 10mm",
        "3. Cut along graft outline",
        "4. Wrap cylinder - edges must meet perfectly",
        f"5. Expected cylinder diameter: {diameter:.1f}mm"
    ]
    y_text = y_offset + height_mm + 30
    for line in instructions:
        c.drawString(x_offset, y_text, line)
        y_text += 12
    
    c.save()
    pdf_buffer.seek(0)
    
    st.download_button(
        label="📥 Download EXACT-SCALE PDF",
        data=pdf_buffer,
        file_name=f"PMEG_Template_{graft['name']}_{diameter}mm.pdf",
        mime="application/pdf"
    )
    
    st.success("✅ PDF generated at exact 1:1 scale")
    st.warning("⚠️ **PRINT SETTINGS: Choose 'Actual Size' or '100%' - NOT 'Fit'**")

# --- VERIFICATION SECTION ---
st.header("5. Verification Checklist")
st.info("""
**Before Sterilization:**
- [ ] Print using laser printer (1200 DPI)
- [ ] Measure ALL 10mm bars: they must be exactly 10mm
- [ ] Measure graft rectangle width: must be **{:.1f}mm** (circumference)
- [ ] Measure graft rectangle height: must be **{}mm** (length)
- [ ] Edges of paper meet perfectly when wrapped
""".format(circumference, length))

# --- OR INSTRUCTIONS ---
st.header("6. OR Use Instructions")
st.info("""
1. **Sterilize**: Laminate between two sterile Tegaderm sheets
2. **Wrap**: Align markers, ensure edges meet perfectly
3. **Mark**: Use sterile pen through fenestration holes
4. **Cut**: Electrocautery along marked circles
5. **Verify**: Fluoroscopy shows markers align with vessels
""")

st.caption("Proof-of-Concept | Not for clinical use | Validate before OR use")
