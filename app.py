# --- LIVE VISUALIZATION (12 CENTERED) ---
st.header("3. Live Graft Preview")
st.caption("❗12 o'clock (anterior) is at CENTER of graft")

if 'fens' in st.session_state and st.session_state.fens:
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Draw unrolled graft rectangle
    ax.set_xlim(0, circumference)
    ax.set_ylim(length, 0)  # Invert Y: proximal at top
    
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
    
    # Labels
    ax.text(circumference/2, -8, "PROXIMAL END (0mm)", ha='center', fontsize=12, fontweight='bold', color='red')
    ax.text(circumference/2, length+8, f"DISTAL END ({length}mm)", ha='center', fontsize=12, fontweight='bold', color='blue')
    
    # Fenestrations with 12-centered mapping: ((angle + 180) % 360) / 360
    colors = {"Celiac trunk": '#FF6B6B', "SMA": '#4ECDC4', "Right renal artery": '#45B7D1', "Left renal artery": '#96CEB4', "Accessory renal artery 1": '#FFEAA7', "Accessory renal artery 2": '#DDA0DD', "IMA": '#FFB347'}
    for f in st.session_state.fens:
        x = ((f['c'] + 180) % 360) / 360 * circumference
        y = length - f['d']  # Invert Y for proximal at top
        circle = plt.Circle((x, y), f['s'], color=colors.get(f['v'], 'black'), alpha=0.6, fill=True)
        ax.add_patch(circle)
        
        hour_disp = "12" if f['c'] == 0 else str(int(f['c'] / 30))
        ax.text(x, y, VESSEL_SHORT[f['v']], ha='center', va='center', fontsize=9, fontweight='bold', 
                color='white', bbox=dict(boxstyle="round,pad=0.2", facecolor="black", alpha=0.5))
        ax.text(x, y + f['s'] + 3, f"Ø{f['s']}mm @{f['d']}mm\n{hour_disp} o'clock", ha='center', fontsize=7)
    
    ax.set_xlabel("Circumference (mm)", fontsize=12)
    ax.set_ylabel("Distance from Proximal End (mm)", fontsize=12)
    ax.set_title(f"UNROLLED GRAFT\n{diameter}mm × {length}mm | Scale 1:1", fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
else:
    st.info("Add fenestrations to see live preview")
