import streamlit as st
import random
import math

# Versionskonfiguration
VERSION = "1.2.2"
AUTHOR = "Kilian Betz"

# Seite konfigurieren
st.set_page_config(page_title=f"Winkel-Trainer v{VERSION}", layout="wide")

# CSS für Apple-Look und weißen Graphen-Hintergrund
st.markdown(f"""
    <style>
    .main {{ background-color: #F2F2F7; }}
    .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; }}
    .stButton>button:first-child {{ background-color: #007AFF; color: white; border: none; }}
    .graph-container {{ 
        background-color: white; 
        border-radius: 20px; 
        padding: 10px; 
        border: 1px solid #D1D1D6;
        display: flex;
        justify-content: center;
    }}
    .control-container {{
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #D1D1D6;
    }}
    .footer {{ text-align: center; color: #8E8E93; margin-top: 50px; font-size: 0.8em; }}
    </style>
    """, unsafe_allow_html=True)

# --- State Management ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'answer_correct' not in st.session_state:
    st.session_state.answer_correct = False

GRIECHISCHE_WINKEL = {
    'a1': 'α', 'b1': 'β', 'c1': 'γ', 'd1': 'δ',
    'a2': 'ε', 'b2': 'ζ', 'c2': 'η', 'd2': 'θ'
}

def generate_task():
    base_angle = random.randint(40, 70)
    keys = list(GRIECHISCHE_WINKEL.keys())
    given_pos = random.choice(keys)
    target_pos = random.choice([k for k in keys if k != given_pos])
    
    def calc_value(pos, base):
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
    st.session_state.answer_correct = False

if 'current_task' not in st.session_state or st.session_state.current_task is None:
    generate_task()

# --- SVG Zeichnung ---
def draw_winkel_svg(task):
    # Mathematische Konstanten für die Zeichnung
    phi = 45  # Winkel der schneidenden Geraden
    c1 = (320, 150) # Kreuzungspunkt oben (g)
    c2 = (170, 300) # Kreuzungspunkt unten (h)
    r = 45 # Radius der Winkelbögen

    def get_arc_path(pos, center):
        cx, cy = center
        # Winkelbereiche für die 4 Quadranten
        if pos[0] == 'a': s, e = -phi, 0
        elif pos[0] == 'b': s, e = 180-phi, 180
        elif pos[0] == 'c': s, e = 180, 180+phi
        else: s, e = 360-phi, 360
        
        # Umrechnung in Bogenmaß für Endpunkte
        x1 = cx + r * math.cos(math.radians(s))
        y1 = cy + r * math.sin(math.radians(s))
        x2 = cx + r * math.cos(math.radians(e))
        y2 = cy + r * math.sin(math.radians(e))
        
        return f"M {cx} {cy} L {x1} {y1} A {r} {r} 0 0 1 {x2} {y2} Z"

    # Buchstaben-Offsets
    offs = {'a': (35, -15), 'b': (-55, -15), 'c': (-55, 35), 'd': (35, 35)}
    
    p_given = c1 if task['given_pos'].endswith('1') else c2
    p_target = c1 if task['target_pos'].endswith('1') else c2
    o_given = offs[task['given_pos'][0]]
    o_target = offs[task['target_pos'][0]]

    svg = f"""
    <svg width="100%" height="400" viewBox="0 0 500 450" xmlns="http://www.w3.org/2000/svg">
        <!-- Weißer Hintergrund -->
        <rect width="100%" height="100%" fill="white" rx="20"/>
        
        <!-- Parallele Geraden -->
        <line x1="50" y1="150" x2="450" y2="150" stroke="#1C1C1E" stroke-width="3" />
        <line x1="50" y1="300" x2="450" y2="300" stroke="#1C1C1E" stroke-width="3" />
        <text x="460" y="155" font-style="italic" font-family="serif" font-size="20">g</text>
        <text x="460" y="305" font-style="italic" font-family="serif" font-size="20">h</text>
        
        <!-- Schneidende Gerade -->
        <line x1="100" y1="370" x2="400" y2="70" stroke="#FF3B30" stroke-width="3" />
        <text x="410" y="60" fill="#FF3B30" font-style="italic" font-size="20">t</text>
        
        <!-- Winkelbogen Gegeben -->
        <path d="{get_arc_path(task['given_pos'], p_given)}" fill="rgba(0, 122, 255, 0.2)" stroke="#007AFF" stroke-width="2" />
        <text x="{p_given[0]+o_given[0]}" y="{p_given[1]+o_given[1]}" fill="#007AFF" font-weight="bold" font-size="22">{task['given_letter']}</text>
        
        <!-- Winkelbogen Gesucht -->
        <path d="{get_arc_path(task['target_pos'], p_target)}" fill="rgba(255, 59, 48, 0.1)" stroke="#FF3B30" stroke-width="2" stroke-dasharray="4" />
        <text x="{p_target[0]+o_target[0]}" y="{p_target[1]+o_target[1]}" fill="#FF3B30" font-weight="bold" font-size="26">{task['target_letter']}</text>
    </svg>
    """
    return svg

# --- UI Aufbau ---
st.title("📐 Winkel-Trainer")
st.markdown(f"**Mathe 7. Klasse** – Winkel an parallelen Geraden")

if st.session_state.score >= 10:
    st.balloons()
    st.success("🎉 Ziel erreicht! Du hast 10 Aufgaben richtig gelöst.")
    if st.button("Training neustarten"):
        st.session_state.score = 0
        generate_task()
        st.rerun()
else:
    col1, col2 = st.columns([1.5, 1], gap="medium")

    with col1:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.markdown(draw_winkel_svg(st.session_state.current_task), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        curr = st.session_state.current_task
        st.info(f"Gegeben: **{curr['given_letter']} = {curr['given_val']}°**. Berechne das Maß von **{curr['target_letter']}**.")

    with col2:
        st.markdown('<div class="control-container">', unsafe_allow_html=True)
        st.markdown(f"### Score: `{st.session_state.score} / 10`")
        
        # Eingabeformular
        with st.form("calc_form", clear_on_submit=False):
            user_input = st.number_input(f"Ergebnis für {curr['target_letter']}:", min_value=0, max_value=180, step=1)
            btn_submit = st.form_submit_button("Überprüfe")
            
            if btn_submit:
                if user_input == curr['correct_answer']:
                    st.session_state.feedback = "correct"
                    st.session_state.score += 1
                    st.session_state.answer_correct = True
                else:
                    st.session_state.feedback = "wrong"
                    st.session_state.answer_correct = False

        if st.session_state.feedback == "correct":
            st.success("✅ Richtig!")
        elif st.session_state.feedback == "wrong":
            st.error("❌ Das ist leider falsch. Probiere es nochmal!")

        # Nächste Aufgabe Button (außerhalb des Forms)
        if st.session_state.answer_correct:
            if st.button("Nächste Aufgabe ➔"):
                generate_task()
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown(f"""
    <div class="footer">
        {AUTHOR} - Version {VERSION} | Entwickelt für bayerische Gymnasien
    </div>
    """, unsafe_allow_html=True)
