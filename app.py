import streamlit as st
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Versionskonfiguration
VERSION = "1.4.1"
AUTHOR = "Kilian Betz"

st.set_page_config(page_title=f"Winkel-Trainer v{VERSION}", layout="wide")

# CSS für Apple-Look
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
UI_SYMBOLS = {'a1':'α','b1':'β','c1':'γ','d1':'δ','a2':'ε','b2':'ζ','c2':'η','d2':'θ','a3':'ι','b3':'κ','c3':'λ','d3':'μ','a4':'ν','b4':'ξ','c4':'ο','d4':'π'}
PLOT_SYMBOLS = {'a1':r'$\alpha$','b1':r'$\beta$','c1':r'$\gamma$','d1':r'$\delta$','a2':r'$\epsilon$','b2':r'$\zeta$','c2':r'$\eta$','d2':r'$\theta$','a3':r'$\iota$','b3':r'$\kappa$','c3':r'$\lambda$','d3':r'$\mu$','a4':r'$\nu$','b4':r'$\xi$','c4':r'$o$','d4':r'$\pi$'}

# --- Logik & Session State ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'diff_mode' not in st.session_state: st.session_state.diff_mode = False
if 'current_task' not in st.session_state: st.session_state.current_task = None

def generate_task():
    # Neue Geometrie-Parameter
    p_angle = random.randint(0, 170) # Winkel der parallelen Geraden
    t_angle = (p_angle + random.randint(40, 140)) % 180 # Winkel der Schneidenden
    
    # Sicherstellen, dass sie nicht fast parallel sind
    while abs(p_angle - t_angle) < 20:
        t_angle = (t_angle + 30) % 180

    mode = "hard" if st.session_state.diff_mode else "normal"
    
    # Sets von Kreuzungen bestimmen (Winkelsätze gelten nur innerhalb eines Sets)
    if mode == "normal":
        sets = [('1', '2')] # Kreuzungen an Gerade t
    else:
        sets = [('1', '2'), ('3', '4')] # t oder s
    
    active_set = random.choice(sets)
    given_pos = random.choice(['a', 'b', 'c', 'd']) + active_set[0]
    target_pos = random.choice(['a', 'b', 'c', 'd']) + active_set[1]
    
    # Basiswinkel für die Berechnung (Schnittwinkel p_angle und t_angle)
    # Kleinerer Schnittwinkel
    inter_angle = abs(p_angle - t_angle) % 180
    if inter_angle > 90: inter_angle = 180 - inter_angle
    
    def calc_val(pos, base):
        return base if pos[0] in ['a', 'c'] else 180 - base

    st.session_state.current_task = {
        'p_angle': p_angle,
        't_angle': t_angle,
        's_angle': (t_angle + 40) % 180, # Zweite Schneidende für Hard Mode
        'mode': mode,
        'given_pos': given_pos,
        'target_pos': target_pos,
        'given_val': calc_val(given_pos, inter_angle),
        'correct_answer': calc_val(target_pos, inter_angle),
        'given_ui': UI_SYMBOLS[given_pos],
        'target_ui': UI_SYMBOLS[target_pos],
        'given_plot': PLOT_SYMBOLS[given_pos],
        'target_plot': PLOT_SYMBOLS[target_pos]
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

    def draw_line(angle_deg, offset, color='black', label=''):
        angle_rad = np.radians(angle_deg)
        # Normalenvektor für den Offset
        nx, ny = -np.sin(angle_rad), np.cos(angle_rad)
        cx, cy = nx * offset, ny * offset
        
        # Richtungsvektor
        dx, dy = np.cos(angle_rad), np.sin(angle_rad)
        ax.plot([cx - 10*dx, cx + 10*dx], [cy - 10*dy, cy + 10*dy], color=color, linewidth=2)
        if label:
            ax.text(cx + 4.5*dx, cy + 4.5*dy + 0.3, label, fontsize=14, fontstyle='italic', color=color)

    # Parallele g und h
    draw_line(task['p_angle'], 1.5, label='g')
    draw_line(task['p_angle'], -1.5, label='h')

    # Schneidende t
    draw_line(task['t_angle'], 0, color='red', label='t')
    
    if task['mode'] == "hard":
        # Schneidende s (nicht parallel zu t)
        draw_line(task['s_angle'], 1.5, color='green', label='s')

    # Schnittpunkte berechnen für Winkelmarkierungen
    def get_intersect(a1, d1, a2, d2):
        # Lineare Gleichungssystem-Lösung für zwei Geraden
        r1, r2 = np.radians(a1), np.radians(a2)
        A = np.array([[-np.sin(r1), np.cos(r1)], [-np.sin(r2), np.cos(r2)]])
        b = np.array([d1, d2])
        try: return np.linalg.solve(A, b)
        except: return np.array([0, 0])

    # Kreuzungspunkte
    pts = {
        '1': get_intersect(task['p_angle'], 1.5, task['t_angle'], 0),
        '2': get_intersect(task['p_angle'], -1.5, task['t_angle'], 0),
        '3': get_intersect(task['p_angle'], 1.5, task['s_angle'], 1.5),
        '4': get_intersect(task['p_angle'], -1.5, task['s_angle'], 1.5)
    }

    def draw_wedge(pos, is_target):
        center = pts[pos[1]]
        color = '#FF3B30' if is_target else '#007AFF'
        
        # Winkel der beiden Geraden an dieser Kreuzung
        a1 = task['p_angle']
        a2 = task['t_angle'] if pos[1] in ['1', '2'] else task['s_angle']
        
        # Sortieren für Wedge
        angles = sorted([a1 % 180, a2 % 180])
        q = pos[0]
        if q == 'a': s, e = angles[0], angles[1]
        elif q == 'b': s, e = angles[1], angles[0] + 180
        elif q == 'c': s, e = angles[0] + 180, angles[1] + 180
        else: s, e = angles[1] + 180, angles[0] + 360
        
        wedge = patches.Wedge(center, 0.7, s, e, color=color, alpha=0.2)
        ax.add_patch(wedge)
        
        # Label
        lbl = task['target_plot'] if is_target else task['given_plot']
        m = np.radians((s + e) / 2)
        ax.text(center[0]+1.1*np.cos(m), center[1]+1.1*np.sin(m), lbl, 
                fontsize=18, color=color, fontweight='bold', ha='center', va='center')

    draw_wedge(task['given_pos'], False)
    draw_wedge(task['target_pos'], True)
    return fig

# --- UI ---
st.title("📐 Winkel-Trainer Profi")

with st.sidebar:
    st.header("Einstellungen")
    new_mode = st.toggle("Schwere Aufgaben", value=st.session_state.diff_mode)
    if new_mode != st.session_state.diff_mode:
        st.session_state.diff_mode = new_mode
        generate_task(); st.rerun()
    
    img_w = st.slider("Bildbreite", 5.0, 15.0, 8.0)
    if st.button("Bild manuell neu drehen"): generate_task(); st.rerun()

col1, col2 = st.columns([1.6, 1], gap="large")

with col1:
    st.pyplot(create_plot(st.session_state.current_task, img_w))
    st.info("Hinweis: g || h (Die schwarzen Geraden sind immer parallel).")

with col2:
    t = st.session_state.current_task
    st.markdown(f"### Score: `{st.session_state.score}`")
    st.markdown(f'<div class="given-box">Gegeben: {t["given_ui"]} = {t["given_val"]}°</div>', unsafe_allow_html=True)
    
    with st.form("input_form"):
        val = st.number_input(f"Wie groß ist {t['target_ui']}?", min_value=0, max_value=180, step=1)
        if st.form_submit_button("Überprüfen"):
            if val == t['correct_answer']: st.session_state.feedback = "correct"
            else: st.session_state.feedback = "wrong"

    if st.session_state.feedback == "correct":
        st.success("✅ Richtig!")
        if st.button("Nächste Aufgabe ➔"):
            st.session_state.score += 1
            # Bild alle 5 Aufgaben oder bei Klick neu generieren
            generate_task(); st.rerun()
    elif st.session_state.feedback == "wrong":
        st.error("❌ Falsch. Überprüfe die Winkelbeziehung!")

st.markdown(f'<div class="footer">{AUTHOR} - Version {VERSION}</div>', unsafe_allow_html=True)
