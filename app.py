import streamlit as st
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Versionskonfiguration
VERSION = "1.4.0"
AUTHOR = "Kilian Betz"

st.set_page_config(page_title=f"Winkel-Trainer v{VERSION}", layout="wide")

# CSS für Apple-Design
st.markdown(f"""
    <style>
    .main {{ background-color: #F2F2F7; }}
    .stButton>button {{ width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; transition: 0.2s; }}
    .stButton>button:first-child {{ background-color: #007AFF; color: white; border: none; }}
    .given-box {{
        background-color: #E5E5EA; padding: 15px; border-radius: 12px; text-align: center;
        font-size: 1.5em; font-weight: bold; color: #007AFF; margin-bottom: 15px; border: 1px solid #D1D1D6;
    }}
    .footer {{ text-align: center; color: #8E8E93; margin-top: 50px; font-size: 0.8em; }}
    </style>
    """, unsafe_allow_html=True)

# --- Symbole ---
UI_SYMBOLS = {'a1':'α','b1':'β','c1':'γ','d1':'δ','a2':'ε','b2':'ζ','c2':'η','d2':'θ','a3':'ι','b3':'κ','c3':'λ','d3':'μ'}
PLOT_SYMBOLS = {'a1':r'$\alpha$','b1':r'$\beta$','c1':r'$\gamma$','d1':r'$\delta$','a2':r'$\epsilon$','b2':r'$\zeta$','c2':r'$\eta$','d2':r'$\theta$','a3':r'$\iota$','b3':r'$\kappa$','c3':r'$\lambda$','d3':r'$\mu$'}

# --- Session State ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'difficult_mode' not in st.session_state: st.session_state.difficult_mode = False
if 'current_task' not in st.session_state: st.session_state.current_task = None
if 'feedback' not in st.session_state: st.session_state.feedback = None

def generate_task():
    # Schwierigkeitsgrad prüfen
    mode = "hard" if st.session_state.difficult_mode else "normal"
    
    # Rotation basierend auf Score (alle 5 Aufgaben ein neuer Winkel)
    # 0=Horizontal, 1=Vertikal, 2=Diagonal, 3=Gedreht
    layout_type = (st.session_state.score // 5) % 4
    
    base_angle = random.randint(35, 75)
    
    # Positionen festlegen
    if mode == "normal":
        keys = ['a1','b1','c1','d1','a2','b2','c2','d2']
    else:
        keys = ['a1','b1','c1','d1','a2','b2','c2','d2', 'a3','b3','c3','d3']
    
    given_pos = random.choice(keys)
    target_pos = random.choice([k for k in keys if k != given_pos])
    
    # Berechnungslogik (Parallelität g||h)
    def calc_val(pos, base):
        return base if pos[0] in ['a', 'c'] else 180 - base

    st.session_state.current_task = {
        'mode': mode,
        'layout': layout_type,
        'given_pos': given_pos,
        'target_pos': target_pos,
        'given_val': calc_val(given_pos, base_angle),
        'correct_answer': calc_val(target_pos, base_angle),
        'given_ui': UI_SYMBOLS[given_pos],
        'target_ui': UI_SYMBOLS[target_pos],
        'given_plot': PLOT_SYMBOLS[given_pos],
        'target_plot': PLOT_SYMBOLS[target_pos],
        'base_angle': base_angle
    }
    st.session_state.feedback = None

if st.session_state.current_task is None:
    generate_task()

# --- Grafik-Funktion ---
def create_plot(task, width):
    fig, ax = plt.subplots(figsize=(width, width * 0.7))
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    ax.set_aspect('equal'); ax.axis('off')
    fig.patch.set_facecolor('white')

    # Rotationsmatrix definieren
    rot_angle = task['layout'] * 45 # 0, 45, 90, 135 Grad
    rad = np.radians(rot_angle)
    rot_mat = np.array([[np.cos(rad), -np.sin(rad)], [np.sin(rad), np.cos(rad)]])

    def draw_line(p1, p2, color='black', label='', label_pos=(0,0)):
        pts = np.dot(rot_mat, np.array([p1, p2]).T).T
        ax.plot(pts[:,0], pts[:,1], color=color, linewidth=2.5)
        if label:
            lp = np.dot(rot_mat, np.array(label_pos))
            ax.text(lp[0], lp[1], label, fontsize=14, fontstyle='italic', color=color)

    # Geraden zeichnen
    # Parallele g und h
    draw_line([-5, 1.5], [5, 1.5], label='g', label_pos=(4.7, 1.8))
    draw_line([-5, -1.5], [5, -1.5], label='h', label_pos=(4.7, -1.2))

    # Schneidende Gerade(n)
    t_angle = 60 # Winkel der Schneidenden t zur Horizontalen
    t_rad = np.radians(t_angle)
    
    # Kreuzungspunkte (vor Rotation)
    # t: y = tan(60) * x -> x = y / tan(60)
    c1 = np.array([1.5 / np.tan(t_rad), 1.5])
    c2 = np.array([-1.5 / np.tan(t_rad), -1.5])
    
    # Gerade t zeichnen
    draw_line([-3, -4.5], [3, 4.5], color='#FF3B30', label='t', label_pos=(2.5, 4.5))

    if task['mode'] == "hard":
        # Eine vierte Gerade s, die NICHT parallel zu t ist
        draw_line([3, -4.5], [-1, 4.5], color='green', label='s', label_pos=(-1.5, 4.5))
        c3 = np.array([0.5, 1.5]) # Grober Schnittpunkt s mit g für Symbole

    # Winkelbögen zeichnen
    def draw_angle(pos, is_target):
        # Bestimme Zentrum
        if pos.endswith('1'): center_raw = c1
        elif pos.endswith('2'): center_raw = c2
        else: center_raw = c3
        
        center = np.dot(rot_mat, center_raw)
        color = '#FF3B30' if is_target else '#007AFF'
        alpha = 0.15 if is_target else 0.3
        
        # Quadranten-Logik (relativ zur Geraden t und Rotation)
        # a=oben-rechts, b=oben-links, c=unten-links, d=unten-rechts
        q = pos[0]
        base_rot = rot_angle + t_angle
        if q == 'a': s, e = base_rot - t_angle, base_rot
        elif q == 'b': s, e = base_rot, base_rot + (180-t_angle)
        elif q == 'c': s, e = base_rot + (180-t_angle), base_rot + 180
        else: s, e = base_rot + 180, base_rot + 360 - t_angle

        wedge = patches.Wedge(center, 0.7, s, e, color=color, alpha=alpha)
        ax.add_patch(wedge)
        
        # Label
        lbl = task['target_plot'] if is_target else task['given_plot']
        m_rad = np.radians((s + e) / 2)
        lx, ly = center[0] + 1.1 * np.cos(m_rad), center[1] + 1.1 * np.sin(m_rad)
        ax.text(lx, ly, lbl, fontsize=18, color=color, fontweight='bold', ha='center', va='center')

    draw_angle(task['given_pos'], False)
    draw_angle(task['target_pos'], True)
    
    return fig

# --- UI ---
st.title("📐 Winkel-Trainer Profi")

with st.sidebar:
    st.header("Einstellungen")
    st.session_state.difficult_mode = st.toggle("Schwere Aufgaben (4 Geraden)", value=st.session_state.difficult_mode)
    img_width = st.slider("Bildbreite", 5.0, 15.0, 8.0)
    if st.button("Neue Aufgabe generieren"): generate_task(); st.rerun()

col1, col2 = st.columns([1.6, 1], gap="large")

with col1:
    st.pyplot(create_plot(st.session_state.current_task, img_width))
    st.info("Hinweis: Geraden g und h sind immer parallel ($g \parallel h$).")

with col2:
    t = st.session_state.current_task
    st.markdown(f"### Score: `{st.session_state.score}`")
    
    st.markdown(f'<div class="given-box">Gegeben: {t["given_ui"]} = {t["given_val"]}°</div>', unsafe_allow_html=True)
    
    with st.form("input_form"):
        user_val = st.number_input(f"Wie groß ist {t['target_ui']}?", min_value=0, max_value=180, step=1)
        if st.form_submit_button("Überprüfen"):
            if user_val == t['correct_answer']: st.session_state.feedback = "correct"
            else: st.session_state.feedback = "wrong"

    if st.session_state.feedback == "correct":
        st.success("✅ Richtig!")
        if st.button("Nächste Aufgabe ➔"):
            st.session_state.score += 1
            generate_task(); st.rerun()
    elif st.session_state.feedback == "wrong":
        st.error("❌ Falsch. Prüfe die Parallelität!")

st.markdown(f'<div class="footer">{AUTHOR} - Version {VERSION}</div>', unsafe_allow_html=True)
