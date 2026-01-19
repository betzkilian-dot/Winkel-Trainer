import streamlit as st
import random
import math

# Versionskonfiguration
VERSION = "1.2.1"
AUTHOR = "Kilian Betz"

# Seite konfigurieren
st.set_page_config(page_title=f"Winkel-Trainer v{VERSION}", layout="wide")

# Apple-Style CSS für ein sauberes Interface
st.markdown("""
    <style>
    .main { background-color: #F2F2F7; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; transition: 0.2s; border: none; }
    .stButton>button:first-child { background-color: #007AFF; color: white; }
    .stButton>button:hover { opacity: 0.8; }
    div[data-testid="column"] { 
        background-color: white; 
        padding: 25px; 
        border-radius: 20px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
    }
    .footer { text-align: center; color: #8E8E93; margin-top: 50px; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- Mathematische Logik & Mapping ---
GRIECHISCHE_WINKEL = {
    'a1': 'α', 'b1': 'β', 'c1': 'γ', 'd1': 'δ',
    'a2': 'ε', 'b2': 'ζ', 'c2': 'η', 'd2': 'θ'
}

if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_task' not in st.session_state:
    st.session_state.current_task = None
if 'feedback' not in st.session_state:
    st.session_state.feedback = None

def generate_task():
    # Basis-Winkel (spitz)
    base_angle = random.randint(35, 75)
    
    keys = list(GRIECHISCHE_WINKEL.keys())
    given_pos = random.choice(keys)
    target_pos = random.choice([k for k in keys if k != given_pos])
    
    def calc_value(pos, base):
        # a und c sind Scheitelwinkel (gleich base)
        # b und d sind Nebenwinkel (180 - base)
        if pos[0] in ['a', 'c']: return base
        else: return 180 - base

    st.session_state.current_task = {
        'given_pos': given_pos,
        'target_pos': target_pos,
        'given_val': calc_value(given_pos, base_angle),
        'correct_answer': calc_value(target_pos, base_angle),
        'given_letter': GRIECHISCHE_WINKEL[given_pos],
        'target_letter': GRIECHISCHE_WINKEL[target_pos]
    }
    st.session_state.feedback = None

if st.session_state.current_task is None:
    generate_task()

# --- SVG Zeichnung mit griechischen Buchstaben ---
def draw_winkel_svg(task):
    phi = 48 # Fester Neigungswinkel für die Optik
    c1 = (327, 150) # Kreuzung oben
    c2 = (191, 300) # Kreuzung unten
    r = 40 # Radius Winkelbogen

    def get_arc_path(pos, center):
        cx, cy = center
        # Start- und Endwinkel je Quadrant
        quadrant = pos[0]
        if quadrant == 'a': start_deg, end_deg = -phi, 0
        elif quadrant == 'b': start_deg, end_deg = 180-phi, 180
        elif quadrant == 'c': start_deg, end_deg = 180, 180+phi
        else: start_deg, end_deg = 360-phi, 360
        
        def polar_to_cartesian(angle_deg):
            angle_rad = math.radians(angle_deg)
            return cx + r * math.cos(angle_rad), cy + r * math.sin(angle_rad)

        x1, y1 = polar_to_cartesian(start_deg)
        x2, y2 = polar_to_cartesian(end_deg)
        return f"M {cx} {cy} L {x1} {y1} A {r} {r} 0 0 1 {x2} {y2} Z"

    # Positionierung der Buchstaben
    offsets = {'a': (45, -25), 'b': (-65, -25), 'c': (-65, 45), 'd': (45, 45)}
    
    given_p = c1 if task['given_pos'].endswith('1') else c2
    target_p = c1 if task['target_pos'].endswith('1') else c2
    given_off = offsets[task['given_pos'][0]]
    target_off = offsets[task['target_pos'][0]]

    svg = f"""
    <svg width="100%" height="400" viewBox="0 0 500 450" xmlns="http://www.w3.org/2000/svg">
        <line x1="50" y1="150" x2="450" y2="150" stroke="#1C1C1E" stroke-width="3" />
        <line x1="50" y1="300" x2="450" y2="300" stroke="#1C1C1E" stroke-width="3" />
        <text x="465" y="155" font-style="italic" font-family="serif" font-size="20">g</text>
        <text x="465" y="305" font-style="italic" font-family="serif" font-size="20">h</text>
        <line x1="100" y1="400" x2="400" y2="70" stroke="#FF3B30" stroke-width="3" />
        <text x="410" y="60" fill="#FF3B30" font-style="italic" font-size="20">t</text>
        
        <path d="{get_arc_path(task['given_pos'], given_p)}" fill="rgba(0, 122, 255, 0.2)" stroke="#007AFF" stroke-width="2" />
        <text x="{given_p[0] + given_off[0]}" y="{given_p[1] + given_off[1]}" fill="#007AFF" font-weight="bold" font-size="24">{task['given_letter']}</text>
        
        <path d="{get_arc_path(task['target_pos'], target_p)}" fill="rgba(255, 59, 48, 0.1)" stroke="#FF3B30" stroke-width="2" stroke-dasharray="4" />
        <text x="{target_p[0] + target_off[0]}" y="{target_p[1] + target_off[1]}" fill="#FF3B30" font-weight="bold" font-size="24">{task['target_letter']}</text>
    </svg>
    """
    return svg

# --- UI ---
st.title("📐 Winkel-Trainer")
st.markdown(f"**Thema:** Winkelzusammenhänge an parallelen Geraden ($g \parallel h$)")

if st.session_state.score >= 10:
    st.balloons()
    st.success("🎉 Hervorragend! Du hast 10 Aufgaben richtig gelöst.")
    if st.button("Training zurücksetzen"):
        st.session_state.score = 0
        generate_task()
        st.rerun()
else:
    col1, col2 = st.columns([1.5, 1], gap="large")

    with col1:
        st.markdown(draw_winkel_svg(st.session_state.current_task), unsafe_allow_html=True)
        t = st.session_state.current_task
        st.info(f"Gegeben ist der Winkel **{t['given_letter']} = {t['given_val']}°**. Berechne den Winkel **{t['target_letter']}**.")

    with col2:
        st.markdown(f"### Score: `{st.session_state.score} / 10`")
        
        with st.form("math_form"):
            user_val = st.number_input(f"Wert für {t['target_letter']} in Grad:", min_value=0, max_value=180, step=1)
            submit = st.form_submit_button("Überprüfen")
            
            if submit:
                if user_val == t['correct_answer']:
                    st.session_state.feedback = "correct"
                    st.session_state.score += 1
                else:
                    st.session_state.feedback = "wrong"

        if st.session_state.feedback == "correct":
            st.success("✅ Richtig!")
            if st.button("Nächste Aufgabe ➔"):
                generate_task()
                st.rerun()
        elif st.session_state.feedback == "wrong":
            st.error("❌ Das ist leider falsch. Denke an Scheitel-, Neben-, Stufen- und Wechselwinkel!")

# Footer
st.markdown(f"""
    <div class="footer">
        {AUTHOR} - Version {VERSION} | Entwickelt für den Einsatz an bayerischen Gymnasien
    </div>
    """, unsafe_allow_html=True)
