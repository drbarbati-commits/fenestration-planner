import streamlit as st
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import matplotlib.pyplot as plt

# --- PAGE TITLE ---
st.set_page_config(page_title="Fenestration Planner", layout="wide")
st.title("🎯 PMEG Template Generator")
st.subheader("Proof-of-Concept Demo")

# --- SIDEBAR: GRAFT SELECTION ---
st.sidebar.header("1. Select Graft Template")
graft_type = st.sidebar.selectbox(
    "Graft Type",
    ["Device A (24mm diameter)", "Device B (28mm diameter)", "Device C (32mm diameter)"]
)

graft_specs = {
    "Device A (24mm diameter)": {"diameter": 24, "length": 145, "name": "A"},
    "Device B (28mm diameter)": {"diameter": 28, "length": 150, "name": "B"},
    "Device C (32mm diameter)": {"diameter": 32, "length": 155, "name": "C"}
}

graft = graft_specs[graft_type]
diameter = graft["diameter"]
length = graft["length"]

st.sidebar.info(f"**Diameter:** {diameter}mm | **Length:** {length}mm")

# --- MAIN: ADD FENESTRATIONS ---
st.header("2. Add Fenestrations")
col1, col2 = st.columns(2)

with col1:
    vessel_type = st.selectbox("Vessel", ["Left Renal", "Right Renal", "SMA", "Celiac"])
    distance = st.number_input("Distance from Proximal (mm)", 20, 130, 50)
with col2:
    clock_pos = st.slider("Clock Position (12=anterior)", 0, 360, 180)
    fen_size = st.number_input("Fenestration Diameter (mm)", 5.0, 12.0, 6.0, 0.5)

if st.button("➕ Add Fenestration"):
    if 'fens' not in st.session_state:
        st.session_state.fens = []
    
    # Collision detection (simple)
    for f in st.session_state.fens:
        if abs(f['d'] - distance) < 5:
            st.error("⚠️ Too close to existing fenestration!")
            st.stop()
    
    st.session_state.fens.append({
        "v": vessel_type,
        "d": distance,
        "c": clock_pos,
        "s": fen_size
    })
    st.success(f"✅ Added {vessel_type}")
    st.rerun()

# --- SHOW LIST ---
if 'fens' in st.session_state and st.session_state.fens:
    st.write("**Current Fenestrations:**")
    for i, f in enumerate(st.session_state.fens):
        col1, col2 = st.columns([5, 1])
        col1.write(f"🔴 {f['v']} | @{f['d']}mm | {f['c']}° | Size {f['s']}mm")
        if col2.button("❌", key=f"del_{i}"):
            st.session_state.fens.pop(i)
            st.rerun()

# --- LIVE VISUALIZATION ---
st.header("3. Live Graft Preview")
st.caption("Watch the template update in real-time as you add fenestrations")

if 'fens' in st.session_state and st.session_state.fens:
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Draw unrolled graft rectangle
    width = math.pi * diameter
    height = length
    
    # Graft outline
    ax.plot([0, width, width, 0, 0], [0, 0, height, height, 0], 
            'k-', linewidth=3, label="Graft Edge")
    
    # Stent rings (every 15mm)
    for i in range(0, length, 15):
        ax.plot([0, width], [i, i], 'gray', linestyle=':', alpha=0.5)
    
    # Radiopaque markers
    for pos in [30, 60, 90]:
        ax.plot([0, width], [pos, pos], 'gold', linewidth=4, alpha=0.8)
    
    # Fenestrations
    colors = {'Left Renal': 'red', 'Right Renal': 'blue', 'SMA': 'green', 'Celiac': 'purple'}
    for f in st.session_state.fens:
        x = (f['c'] / 360) * width
        y = f['d']
        # Draw circle
        circle = plt.Circle((x, y), f['s'], 
                           color=colors.get(f['v'], 'black'), 
                           alpha=0.4, fill=True, linewidth=2)
        ax.add_patch(circle)
        # Label
        ax.text(x, y, f['v'][:3], ha='center', va='center', 
                fontsize=10, fontweight='bold', color='white')
    
    # Labels
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_xlabel("Circumference (mm)", fontsize=12)
    ax.set_ylabel("Length from Proximal End (mm)", fontsize=12)
    ax.set_title(f"Unrolled Graft Template: {diameter}mm × {length}mm", 
                 fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    ax.legend(loc='upper right')
    
    st.pyplot(fig)
else:
    st.info("Add a fenestration to see live preview")

# --- PDF GENERATOR ---
st.header("4. Generate Printable Template")
if st.button("🖨️ Create PDF", type="primary"):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    
    # Unrolled dimensions
    unrolled_width = math.pi * diameter
    unrolled_height = length
    
    # Draw graft outline
    c.rect(50, 100, unrolled_width * 2, unrolled_height * 2)
    
    # Draw fenestrations
    for f in st.session_state.get('fens', []):
        x = 50 + (f['c'] / 360) * unrolled_width * 2
        y = 100 + (f['d'] / length) * unrolled_height * 2
        r = f['s']
        c.circle(x, y, r)
        c.drawString(x - 10, y + r + 5, f['v'])
    
    # Calibration ruler
    c.line(50, 80, 60, 80)
    c.drawString(55, 70, "10mm (verify this measures exactly 10mm)")
    
    c.save()
    pdf_buffer.seek(0)
    
    st.download_button(
        label="📥 Download PDF",
        data=pdf_buffer,
        file_name=f"graft_template_{graft['name']}.pdf",
        mime="application/pdf"
    )

# --- INSTRUCTIONS ---
st.header("5. OR Usage Instructions")
st.info("""
1. **Print** at 100% scale (disable "Fit to page")
2. **Verify** the 10mm calibration line
3. **Sterilize** by laminating between two Tegaderm sheets
4. **Wrap** around unsheathed graft & align to markers
5. **Mark** fenestrations through the holes
""")

st.caption("Proof-of-Concept | Not for clinical use")
