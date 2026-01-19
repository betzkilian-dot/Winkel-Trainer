import streamlit as st
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Versionskonfiguration
VERSION = "1.4.2"
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

# --- Session State Initialisierung ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'diff_mode' not in st.session_state: st.session_state.diff_mode = False
if 'current_task' not in st.session_state: st.session_state.current_task = None
if 'feedback' not in st.session_state: st.session_state.feedback = None

def generate_task():
    """Generiert eine komplett neue geometrische Situation."""
    # 1. Winkel der parallelen Geraden g und h (0 bis 180 Grad)
    p_angle = random.randint(0, 179)
    
    # 2. Winkel der Schneidenden t (Sicherstellen, dass der Schnittwinkel gut sichtbar ist)
    t_angle = (p_angle + random.randint(35, 145)) % 180
    while abs(p_angle - t_angle) < 25 or abs(p_angle - t_angle) > 155:
        t_angle = (t_angle + 10) % 180

    mode = "hard" if st.session_state.diff_mode else "normal"
    
    # 3. Schneidende s für den schweren Modus (nicht parallel zu t)
    s_angle = (t_angle + random.randint(30, 60)) % 180
    
    # 4. Auswahl der Kreuzungen (Sets von zusammengehörigen Winkeln)
    if mode == "normal":
        active_set = ('1', '2') # Beides an Schneidende t
    else:
        active_set = random.choice([('1', '2'), ('3', '4')]) # Entweder t oder s
    
    given_pos = random.choice(['a', 'b', 'c', 'd']) + active_set[0]
    target_pos = random.choice(['a', 'b', 'c', 'd']) + active_set[1]
    
    # 5. Berechnung des Basis-Schnittwinkels
    inter_angle = abs(p_angle - (t_angle if active_set[0] in ['1','2'] else s_angle)) % 180
    if inter_angle > 90: inter_angle = 180 - inter_angle
    
    def calc_val(pos, base):
        # a, c sind spitz/stumpf gleich; b, d sind Nebenwinkel
        return base if pos[0] in ['a', 'c'] else 180 - base

    st.session_state.current_task = {
        'p_angle': p_angle,
        't_angle': t_angle,
        's_angle': s_angle,
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

# --- Grafik-Funktion (Matplotlib) ---
def create_plot(task, width):
    fig, ax = plt.subplots(figsize=(width, width * 0.7))
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    ax.set_aspect('equal'); ax.axis('off')
    fig.patch.set_facecolor('white')

    def draw_line(angle_deg, dist, color='black', label=''):
        rad = np.radians(angle_deg)
        # Richtungsvektor der Geraden
        dx, dy = np.cos(rad), np.sin(rad)
        # Normalenvektor für den Abstand vom Zentrum
        nx, ny = -np.sin(rad), np.cos(rad)
        cx, cy = nx * dist, ny * dist
        # Zeichnen
        ax.plot([cx - 10*dx, cx + 10*dx], [cy - 10*dy, cy + 10*dy], color=color, linewidth=2.5)
        if label:
            ax.text(cx + 4.2*dx, cy + 4.2*dy + 0.2, label, fontsize=14, fontstyle='italic', color=color)

    # 1. Parallele Geraden g und h zeichnen
    draw_line(task['p_angle'], 1.5, label='g')
    draw_line(task['p_angle'], -1.5, label='h')

    # 2. Schneidende t (Rot) zeichnen
    draw_line(task['t_angle'], 0, color='#FF3B30', label='t')
    
    # 3. Schneidende s (Grün) zeichnen im Hard Mode
    if task['mode'] == "hard":
        draw_line(task['s_angle'], 1.0, color='green', label='s')

    # 4. Hilfsfunktion für Schnittpunkte
    def intersect(a1, d1, a2, d2):
        r1, r2 = np.radians(a1), np.radians(a2)
        A = np.array([[-np.sin(r1), np.cos(r1)], [-np.sin(r2), np.cos(r2)]])
        b = np.array([d1, d2])
        try: return np.linalg.solve(A, b)
        except: return np.array([0,0])

    # Schnittpunkte berechnen
    pts = {
        '1': intersect(task['p_angle'], 1.5, task['t_angle'], 0), # g x t
        '2': intersect(task['p_angle'], -1.5, task['t_angle'], 0), # h x t
        '3': intersect(task['p_angle'], 1.5, task['s_angle'], 1.0), # g x s
        '4': intersect(task['p_angle'], -1.5, task['s_angle'], 1.0) # h x s
    }

    # 5. Winkel und Beschriftung einzeichnen
    def draw_wedge(pos, is_target):
        center = pts[pos[1]]
        color = '#FF3B30' if is_target else '#007AFF'
        
        # Basis-Winkel der Geraden an dieser Kreuzung
        line_angle = task['p_angle'] % 180
        trans_angle = (task['t_angle'] if pos[1] in ['1','2'] else task['s_angle']) % 180
        
        angles = sorted([line_angle, trans_angle])
        q = pos[0] # Quadrant a, b, c, d
        if q == 'a': s, e = angles[0], angles[1]
        elif q == 'b': s, e = angles[1], angles[0] + 180
        elif q == 'c': s, e = angles[0] + 180, angles[1] + 180
        else: s, e = angles[1] + 180, angles[0] + 360
        
        # Wedge zeichnen
        wedge = patches.Wedge(center, 0.8, s, e, color=color, alpha=0.2)
        ax.add_patch(wedge)
        
        # Label platzieren
        lbl = task['target_plot'] if is_target else task['given_plot']
        m_rad = np.radians((s + e) / 2)
        ax.text(center[0]+1.2*np.cos(m_rad), center[1]+1.2*np.sin(m_rad), lbl, 
                fontsize=18, color=color, fontweight='bold', ha='center', va='center')

    draw_wedge(task['given_pos'], False)
    draw_wedge(task['target_pos'], True)
    return fig

# --- UI Aufbau ---
st.title("📐 Winkel-Trainer")
st.caption("Jede Aufgabe eine neue Konstruktion | g || h")

with st.sidebar:
    st.header("Einstellungen")
    diff = st.toggle("Schwere Aufgaben (4 Geraden)", value=st.session_state.diff_mode)
    if diff != st.session_state.diff_mode:
        st.session_state.diff_mode = diff
        generate_task(); st.rerun()
    
    img_w = st.slider("Bildbreite anpassen", 5.0, 15.0, 8.0, step=0.5)
    if st.button("Manuell neu würfeln"): generate_task(); st.rerun()

col1, col2 = st.columns([1.6, 1], gap="large")

with col1:
    st.pyplot(create_plot(st.session_state.current_task, img_w))
    st.info("Die schwarzen Geraden g und h sind immer parallel zueinander.")

with col2:
    t = st.session_state.current_task
    st.markdown(f"### Score: `{st.session_state.score}`")
    
    st.markdown(f'<div class="given-box">Gegeben: {t["given_ui"]} = {t["given_val"]}°</div>', unsafe_allow_html=True)
    
    with st.form("math_form"):
        user_input = st.number_input(f"Berechne das Maß für {t['target_ui']}:", min_value=0, max_value=180, step=1)
        if st.form_submit_button("Überprüfen"):
            if user_input == t['correct_answer']:
                st.session_state.feedback = "correct"
            else:
                st.session_state.feedback = "wrong"

    if st.session_state.feedback == "correct":
        st.success(f"✅ Richtig! {t['target_ui']} ist {t['correct_answer']}°.")
        if st.button("Nächste Aufgabe ➔"):
            st.session_state.score += 1
            generate_task(); st.rerun()
    elif st.session_state.feedback == "wrong":
        st.error("❌ Das ist leider falsch. Prüfe, ob es sich um Stufen-, Wechsel-, Scheitel- oder Nebenwinkel handelt.")

    if st.session_state.score >= 10:
        st.balloons()
        st.success("🎉 Hervorragend! Du hast 10 Aufgaben gemeistert.")

st.markdown(f'<div class="footer">{AUTHOR} - Version {VERSION}</div>', unsafe_allow_html=True)
