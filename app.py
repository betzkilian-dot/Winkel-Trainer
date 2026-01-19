import streamlit as st
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Versionskonfiguration
VERSION = "1.3.1"
AUTHOR = "Kilian Betz"

st.set_page_config(page_title=f"Winkel-Trainer v{VERSION}", layout="wide")

# Apple-Style CSS
st.markdown(f"""
    <style>
    .main {{ background-color: #F2F2F7; }}
    .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; }}
    .stButton>button:first-child {{ background-color: #007AFF; color: white; border: none; }}
    .footer {{ text-align: center; color: #8E8E93; margin-top: 50px; font-size: 0.8em; }}
    </style>
    """, unsafe_allow_html=True)

# --- Logik ---
GRIECHISCHE_WINKEL = {
    'a1': r'$\alpha$', 'b1': r'$\beta$', 'c1': r'$\gamma$', 'd1': r'$\delta$',
    'a2': r'$\epsilon$', 'b2': r'$\zeta$', 'c2': r'$\eta$', 'd2': r'$\theta$'
}

if 'score' not in st.session_state:
    st.session_state.score = 0
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'current_task' not in st.session_state:
    st.session_state.current_task = None

def generate_task():
    base_angle = random.randint(35, 70)
    keys = list(GRIECHISCHE_WINKEL.keys())
    given_pos = random.choice(keys)
    target_pos = random.choice([k for k in keys if k != given_pos])
    
    def calc_value(pos, base):
        return base if pos[0] in ['a', 'c'] else 180 - base

    st.session_state.current_task = {
        'given_pos': given_pos,
        'target_pos': target_pos,
        'given_val': calc_value(given_pos, base_angle),
        'correct_answer': calc_value(target_pos, base_angle),
        'given_letter': GRIECHISCHE_WINKEL[given_pos],
        'target_letter': GRIECHISCHE_WINKEL[target_pos],
        'base': base_angle
    }
    st.session_state.feedback = None

if st.session_state.current_task is None:
    generate_task()

# --- Grafik-Erstellung mit Matplotlib ---
def create_plot(task):
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # Parallele Geraden g und h
    ax.axhline(y=5, color='black', linewidth=2)
    ax.axhline(y=2, color='black', linewidth=2)
    ax.text(9.5, 5.2, 'g', fontsize=14, fontstyle='italic')
    ax.text(9.5, 2.2, 'h', fontsize=14, fontstyle='italic')

    # Schneidende Gerade t
    x = np.linspace(1, 9, 100)
    y = 1.2 * (x - 5) + 3.5 
    ax.plot(x, y, color='red', linewidth=2)
    ax.text(8.5, 8, 't', color='red', fontsize=14, fontstyle='italic')

    # Schnittpunkte berechnen
    c1 = (6.25, 5)
    c2 = (3.75, 2)
    
    phi = np.degrees(np.arctan(1.2))
    
    def draw_angle_mark(pos, is_target=False):
        center = c1 if pos.endswith('1') else c2
        color = 'red' if is_target else 'blue'
        alpha = 0.2 if is_target else 0.4
        
        # Quadranten-Logik (a=oben-rechts, b=oben-links, c=unten-links, d=unten-rechts)
        angles = {
            'a': (0, phi), 'b': (phi, 180), 
            'c': (180, 180+phi), 'd': (180+phi, 360)
        }
        start, end = angles[pos[0]]
        
        # Winkelbogen einzeichnen
        wedge = patches.Wedge(center, 0.8, start, end, color=color, alpha=alpha)
        ax.add_patch(wedge)
        
        # Beschriftung (Griechische Buchstaben)
        label = task['target_letter'] if is_target else task['given_letter']
        mid_angle = np.radians((start + end) / 2)
        dist = 1.3
        lx = center[0] + dist * np.cos(mid_angle)
        ly = center[1] + dist * np.sin(mid_angle)
        ax.text(lx, ly, label, fontsize=18, color=color, fontweight='bold', ha='center', va='center')

    draw_angle_mark(task['given_pos'], is_target=False)
    draw_angle_mark(task['target_pos'], is_target=True)

    return fig

# --- UI Aufbau ---
st.title("📐 Winkel-Trainer")
st.caption("Mathe Gymnasium Bayern | 7. Klasse")

col1, col2 = st.columns([1.5, 1], gap="large")

with col1:
    # Plot anzeigen
    st.pyplot(create_plot(st.session_state.current_task))
    t = st.session_state.current_task
    st.info(f"Gegeben ist der Winkel **{t['given_letter']} = {t['given_val']}°**. Berechne das Maß von **{t['target_letter']}**.")

with col2:
    st.markdown(f"### Score: `{st.session_state.score} / 10`")
    
    with st.form("input_form", clear_on_submit=False):
        user_val = st.number_input(f"Ergebnis für {t['target_letter']}:", min_value=0, max_value=180, step=1)
        if st.form_submit_button("Überprüfen"):
            if user_val == t['correct_answer']:
                st.session_state.feedback = "correct"
            else:
                st.session_state.feedback = "wrong"

    if st.session_state.feedback == "correct":
        st.success("✅ Richtig!")
        if st.button("Nächste Aufgabe ➔"):
            st.session_state.score += 1
            generate_task()
            st.rerun()
    elif st.session_state.feedback == "wrong":
        st.error("❌ Leider falsch. Probiere es noch einmal oder prüfe die Winkelart!")

    if st.session_state.score >= 10:
        st.balloons()
        st.success("🎉 Ziel erreicht! Du bist ein echter Winkel-Profi.")

st.markdown(f'<div class="footer">{AUTHOR} - Version {VERSION}</div>', unsafe_allow_html=True)
