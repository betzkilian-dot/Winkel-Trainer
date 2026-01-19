import streamlit as st
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Versionskonfiguration
VERSION = "1.5.0"
AUTHOR = "Kilian Betz"

st.set_page_config(page_title=f"Winkel-Trainer v{VERSION}", layout="wide")

# Apple-Style CSS
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

# --- Symbole Mapping ---
UI_SYMBOLS = {'a1':'α','b1':'β','c1':'γ','d1':'δ','a2':'ε','b2':'ζ','c2':'η','d2':'θ','a3':'ι','b3':'κ','c3':'λ','d3':'μ','a4':'ν','b4':'ξ','c4':'ο','d4':'π'}
PLOT_SYMBOLS = {'a1':r'$\alpha$','b1':r'$\beta$','c1':r'$\gamma$','d1':r'$\delta$','a2':r'$\epsilon$','b2':r'$\zeta$','c2':r'$\eta$','d2':r'$\theta$','a3':r'$\iota$','b3':r'$\kappa$','c3':r'$\lambda$','d3':r'$\mu$','a4':r'$\nu$','b4':r'$\xi$','c4':r'$o$','d4':r'$\pi$'}

if 'score' not in st.session_state: st.session_state.score = 0
if 'diff_mode' not in st.session_state: st.session_state.diff_mode = False
if 'tri_mode' not in st.session_state: st.session_state.tri_mode = False
if 'current_task' not in st.session_state: st.session_state.current_task = None
if 'feedback' not in st.session_state: st.session_state.feedback = None

def generate_task():
    # Basis-Geometrie
    p_angle = random.randint(0, 179)
    t_angle = (p_angle + random.randint(40, 140)) % 180
    
    # Spezialmodus: Innenwinkelsumme
    if st.session_state.tri_mode:
        # Erzeugt ein Dreieck durch eine zweite Schneidende s
        s_angle = (t_angle + random.randint(40, 80)) % 180
        mode = "triangle"
    elif st.session_state.diff_mode:
        s_angle = (t_angle + 30) % 180
        mode = "hard"
    else:
        s_angle = t_angle
        mode = "normal"

    # Bestimmung der Kreuzungspunkte (1,2 für t | 3,4 für s)
    if mode == "triangle":
        # Im Dreiecksmodus beziehen wir uns auf t, s und die Parallele g
        # Wir fragen nach einem Winkel im Dreieck
        active_set = ('1', '3') 
        # Berechne den Winkel an der Spitze des Dreiecks (Schnittpunkt t und s)
        tri_top_angle = abs(t_angle - s_angle) % 180
        if tri_top_angle > 90: tri_top_angle = 180 - tri_top_angle
    else:
        active_set = ('1', '2')

    # Geometrie-Werte berechnen
    inter_t = abs(p_angle - t_angle) % 180
    if inter_t > 90: inter_t = 180 - inter_t
    
    inter_s = abs(p_angle - s_angle) % 180
    if inter_s > 90: inter_s = 180 - inter_s

    given_pos = random.choice(['a', 'b', 'c', 'd']) + active_set[0]
    target_pos = random.choice(['a', 'b', 'c', 'd']) + active_set[1]

    def get_val(pos, base_t, base_s):
        base = base_t if pos[1] in ['1', '2'] else base_s
        return base if pos[0] in ['a', 'c'] else 180 - base

    st.session_state.current_task = {
        'p_angle': p_angle, 't_angle': t_angle, 's_angle': s_angle,
        'mode': mode, 'given_pos': given_pos, 'target_pos': target_pos,
        'given_val': get_val(given_pos, inter_t, inter_s),
        'correct_answer': get_val(target_pos, inter_t, inter_s),
        'given_ui': UI_SYMBOLS[given_pos], 'target_ui': UI_SYMBOLS[target_pos],
        'given_plot': PLOT_SYMBOLS[given_pos], 'target_plot': PLOT_SYMBOLS[target_pos]
    }
    st.session_state.feedback = None

if st.session_state.current_task is None:
    generate_task()

# --- Grafik ---
def create_plot(task, width):
    fig, ax = plt.subplots(figsize=(width, width * 0.7))
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    ax.set_aspect('equal'); ax.axis('off')
    fig.patch.set_facecolor('white')

    def draw_line(angle_deg, dist, color='black', label='', style='-'):
        rad = np.radians(angle_deg)
        dx, dy = np.cos(rad), np.sin(rad)
        nx, ny = -np.sin(rad), np.cos(rad)
        cx, cy = nx * dist, ny * dist
        ax.plot([cx - 10*dx, cx + 10*dx], [cy - 10*dy, cy + 10*dy], color=color, linewidth=2.5, linestyle=style)
        if label:
            ax.text(cx + 4.2*dx, cy + 4.2*dy + 0.2, label, fontsize=14, fontstyle='italic', color=color)

    # Parallele Geraden
    draw_line(task['p_angle'], 1.5, label='g')
    draw_line(task['p_angle'], -1.5, label='h')
    
    # Schneidende t
    draw_line(task['t_angle'], 0, color='#FF3B30', label='t')
    
    # Zweite Schneidende s
    if task['mode'] in ["hard", "triangle"]:
        s_color = "green" if task['mode'] == "hard" else "orange"
        # Im Dreiecksmodus muss s so liegen, dass es t schneidet
        s_dist = 1.0 if task['mode'] == "hard" else -0.5
        draw_line(task['s_angle'], s_dist, color=s_color, label='s')

    def intersect(a1, d1, a2, d2):
        r1, r2 = np.radians(a1), np.radians(a2)
        A = np.array([[-np.sin(r1), np.cos(r1)], [-np.sin(r2), np.cos(r2)]])
        b = np.array([d1, d2])
        return np.linalg.solve(A, b)

    pts = {
        '1': intersect(task['p_angle'], 1.5, task['t_angle'], 0),
        '2': intersect(task['p_angle'], -1.5, task['t_angle'], 0),
        '3': intersect(task['p_angle'], 1.5, task['s_angle'], -0.5 if task['mode']=="triangle" else 1.0),
        '4': intersect(task['p_angle'], -1.5, task['s_angle'], -0.5 if task['mode']=="triangle" else 1.0)
    }

    def draw_wedge(pos, is_target):
        center = pts[pos[1]]
        color = '#FF3B30' if is_target else '#007AFF'
        a1 = task['p_angle'] % 180
        a2 = (task['t_angle'] if pos[1] in ['1','2'] else task['s_angle']) % 180
        angles = sorted([a1, a2])
        q = pos[0]
        if q == 'a': s, e = angles[0], angles[1]
        elif q == 'b': s, e = angles[1], angles[0] + 180
        elif q == 'c': s, e = angles[0] + 180, angles[1] + 180
        else: s, e = angles[1] + 180, angles[0] + 360
        
        ax.add_patch(patches.Wedge(center, 0.8, s, e, color=color, alpha=0.2))
        lbl = task['target_plot'] if is_target else task['given_plot']
        m = np.radians((s + e) / 2)
        ax.text(center[0]+1.3*np.cos(m), center[1]+1.3*np.sin(m), lbl, 
                fontsize=20, color=color, fontweight='bold', ha='center', va='center')

    draw_wedge(task['given_pos'], False)
    draw_wedge(task['target_pos'], True)
    return fig

# --- UI ---
st.title("📐 Winkel-Trainer Profi")

with st.sidebar:
    st.header("Modus wählen")
    # Toggles für die Modi
    if st.toggle("Schwere Aufgaben (4 Geraden)", value=st.session_state.diff_mode):
        st.session_state.diff_mode = True
        st.session_state.tri_mode = False
    else:
        st.session_state.diff_mode = False
        
    if st.toggle("Innenwinkelsumme (Dreieck)", value=st.session_state.tri_mode):
        st.session_state.tri_mode = True
        st.session_state.diff_mode = False
    else:
        st.session_state.tri_mode = False

    st.divider()
    img_w = st.slider("Bildbreite", 4.0, 14.0, 8.0)
    if st.button("Manuell neu würfeln"): generate_task(); st.rerun()

col1, col2 = st.columns([1.6, 1], gap="large")

with col1:
    st.pyplot(create_plot(st.session_state.current_task, img_w))
    if st.session_state.tri_mode:
        st.warning("💡 Tipp: Nutze die Innenwinkelsumme im Dreieck ($180^\\circ$) und die Stufen-/Wechselwinkel.")
    else:
        st.info("Information: Die Geraden g und h sind parallel.")

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
        st.error("❌ Das ist leider falsch.")

st.markdown(f'<div class="footer">{AUTHOR} - Version {VERSION}</div>', unsafe_allow_html=True)
