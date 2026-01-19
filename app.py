import streamlit as st
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Versionskonfiguration
VERSION = "1.3.4"
AUTHOR = "Kilian Betz"

st.set_page_config(page_title=f"Winkel-Trainer v{VERSION}", layout="wide")

# Apple-Style CSS
st.markdown(f"""
    <style>
    .main {{ background-color: #F2F2F7; }}
    .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; transition: 0.2s; }}
    .stButton>button:first-child {{ background-color: #007AFF; color: white; border: none; }}
    .stButton>button:hover {{ opacity: 0.8; }}
    .given-box {{
        background-color: #E5E5EA;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-size: 1.5em;
        font-weight: bold;
        color: #007AFF;
        margin-bottom: 15px;
        border: 1px solid #D1D1D6;
    }}
    .footer {{ text-align: center; color: #8E8E93; margin-top: 50px; font-size: 0.8em; }}
    </style>
    """, unsafe_allow_html=True)

# --- Mapping der Symbole ---
# Unicode für UI (Eingabefelder, Texte)
UI_SYMBOLS = {
    'a1': 'α', 'b1': 'β', 'c1': 'γ', 'd1': 'δ',
    'a2': 'ε', 'b2': 'ζ', 'c2': 'η', 'd2': 'θ'
}
# LaTeX für den Plot (schönere Darstellung im Graphen)
PLOT_SYMBOLS = {
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
    base_angle = random.randint(35, 75)
    keys = list(UI_SYMBOLS.keys())
    given_pos = random.choice(keys)
    target_pos = random.choice([k for k in keys if k != given_pos])
    
    def calc_value(pos, base):
        return base if pos[0] in ['a', 'c'] else 180 - base

    st.session_state.current_task = {
        'given_pos': given_pos,
        'target_pos': target_pos,
        'given_val': calc_value(given_pos, base_angle),
        'correct_answer': calc_value(target_pos, base_angle),
        'given_ui': UI_SYMBOLS[given_pos],
        'target_ui': UI_SYMBOLS[target_pos],
        'given_plot': PLOT_SYMBOLS[given_pos],
        'target_plot': PLOT_SYMBOLS[target_pos]
    }
    st.session_state.feedback = None

if st.session_state.current_task is None:
    generate_task()

# --- Grafik-Erstellung ---
def create_plot(task, width):
    # Die Höhe passt sich proportional zur Breite an (Goldener Schnitt/Ästhetik)
    fig, ax = plt.subplots(figsize=(width, width * 0.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # Parallele Geraden g und h
    ax.axhline(y=5, color='black', linewidth=2.5)
    ax.axhline(y=2, color='black', linewidth=2.5)
    ax.text(9.5, 5.2, 'g', fontsize=16, fontstyle='italic')
    ax.text(9.5, 2.2, 'h', fontsize=16, fontstyle='italic')

    # Schneidende Gerade t
    x = np.linspace(1, 9, 100)
    y = 1.2 * (x - 5) + 3.5 
    ax.plot(x, y, color='#FF3B30', linewidth=2.5)
    ax.text(8.5, 8, 't', color='#FF3B30', fontsize=16, fontstyle='italic')

    c1 = (6.25, 5) 
    c2 = (3.75, 2) 
    phi = np.degrees(np.arctan(1.2))
    
    def draw_angle_mark(pos, is_target=False):
        center = c1 if pos.endswith('1') else c2
        color = '#FF3B30' if is_target else '#007AFF'
        alpha = 0.15 if is_target else 0.3
        
        angles = {
            'a': (0, phi), 'b': (phi, 180), 
            'c': (180, 180+phi), 'd': (180+phi, 360)
        }
        start, end = angles[pos[0]]
        
        wedge = patches.Wedge(center, 0.9, start, end, color=color, alpha=alpha)
        ax.add_patch(wedge)
        
        label = task['target_plot'] if is_target else task['given_plot']
        mid_angle = np.radians((start + end) / 2)
        dist = 1.4
        lx = center[0] + dist * np.cos(mid_angle)
        ly = center[1] + dist * np.sin(mid_angle)
        ax.text(lx, ly, label, fontsize=22, color=color, fontweight='bold', ha='center', va='center')

    draw_angle_mark(task['given_pos'], is_target=False)
    draw_angle_mark(task['target_pos'], is_target=True)
    return fig

# --- UI Aufbau ---
st.title("📐 Winkel-Trainer")

# Sidebar für Einstellungen
with st.sidebar:
    st.header("⚙️ Einstellungen")
    # Regler für die Bildbreite
    img_width = st.slider("Bildbreite verändern", min_value=4.0, max_value=14.0, value=8.0, step=0.5)
    st.caption("Nutze diesen Regler, um die Darstellung an deinen Bildschirm anzupassen.")

col1, col2 = st.columns([1.6, 1], gap="large")

with col1:
    # Graphik anzeigen
    fig = create_plot(st.session_state.current_task, img_width)
    st.pyplot(fig)
    st.info("Info: g || h (Die Geraden g und h sind parallel).")

with col2:
    t = st.session_state.current_task
    st.markdown(f"### Score: `{st.session_state.score} / 10`")
    
    # Gegebener Winkel Box (Jetzt mit Unicode-Symbol)
    st.markdown(f"""
        <div class="given-box">
            Gegeben: {t['given_ui']} = {t['given_val']}°
        </div>
    """, unsafe_allow_html=True)
    
    # Eingabeformular
    with st.form("input_form_v4"):
        # Unicode-Symbol in der Beschriftung
        user_val = st.number_input(f"Berechne das Maß für {t['target_ui']}:", 
                                   min_value=0, max_value=180, step=1)
        
        if st.form_submit_button("Überprüfen"):
            if user_val == t['correct_answer']:
                st.session_state.feedback = "correct"
            else:
                st.session_state.feedback = "wrong"

    if st.session_state.feedback == "correct":
        st.success(f"✅ Richtig! {t['target_ui']} = {t['correct_answer']}°")
        if st.button("Nächste Aufgabe ➔"):
            st.session_state.score += 1
            generate_task()
            st.rerun()
    elif st.session_state.feedback == "wrong":
        st.error(f"❌ Nicht ganz. Überlege: Wie hängen {t['given_ui']} und {t['target_ui']} zusammen?")

    if st.session_state.score >= 10:
        st.balloons()
        st.success("🎉 Hervorragend! Du hast die 10 Aufgaben gemeistert!")

# Signatur
st.markdown(f'<div class="footer">{AUTHOR} - Version {VERSION}</div>', unsafe_allow_html=True)
