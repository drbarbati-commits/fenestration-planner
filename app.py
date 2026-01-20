import streamlit as st
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

st.title("🎯 PMEG Template Generator")

# --- GRAFT SELECTION ---
graft_type = st.sidebar.selectbox("Graft Type", ["Device A (24mm)", "Device B (28mm)"])
graft_specs = {
    "Device A (24mm)": {"diameter": 24, "length": 145},
    "Device B (28mm)": {"diameter": 28, "length": 150}
}
graft = graft_specs[graft_type]
diameter = graft["diameter"]
length = graft["length"]

st.sidebar.info(f"**Diameter:** {diameter}mm | **Length:** {length}mm")

# --- ADD FENESTRATIONS ---
st.write("Add fenestrations:")
col1, col2 = st.columns(2)
with col1:
    vessel = st.selectbox("Vessel", ["Left Renal", "Right Renal", "SMA"])
    distance = st.number_input("Distance (mm)", 20, 130, 50)
with col2:
    clock = st.slider("Clock Position", 0, 360, 180)
    size = st.number_input("Diameter (mm)", 5.0, 12.0, 6.0)

if st.button("Add Fenestration"):
    if 'fens' not in st.session_state:
        st.session_state.fens = []
    st.session_state.fens.append({"v": vessel, "d": distance, "c": clock, "s": size})
    st.success(f"Added {vessel}")

# --- SHOW LIST ---
if 'fens' in st.session_state:
    st.write("Current fenestrations:")
    for f in st.session_state.fens:
        st.write(f"- {f['v']} @ {f['d']}mm, {f['c']}°, size {f['s']}mm")

# --- GENERATE PDF ---
if st.button("🖨️ Create PDF Template"):
    width = math.pi * diameter
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.rect(50, 50, width*2, length*2)
    
    for f in st.session_state.get('fens', []):
        x = 50 + (f['c']/360) * width * 2
        y = 50 + (f['d']/length) * length * 2
        c.circle(x, y, f['s'])
    
    c.line(50, 40, 60, 40)
    c.save()
    buffer.seek(0)
    
    st.download_button("📥 Download PDF", buffer, "template.pdf", "application/pdf")

st.info("Print at 100% scale. Verify the 10mm line measures exactly 10mm.")