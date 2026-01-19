import streamlit as st
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Versionskonfiguration
VERSION = "1.5.2"
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
        font-size: 1.3em; font-weight: bold; color: #007AFF; margin-bottom: 15px; border: 1px solid #D1D1D6;
    }}
    .footer {{ text-align: center; color: #8E8E93; margin-top: 50px; font-size: 0.8em; }}
    </style>
    """, unsafe_allow_html=True)

# --- Symbole Mapping ---
UI_SYMBOLS = {'a1':'α','b1':'β','c1':'γ','d1':'δ','a2':'ε','b2':'ζ','c2':'η','d2':'θ','a3':'ι','b3':'κ','c3':'λ','d3':'μ','top':'φ'}
PLOT_SYMBOLS = {'a1':r'$\alpha$','b1':r'$\beta$','c1':r'$\gamma$','d1':r'$\delta$','a2':r'$\epsilon$','b2':r'$\zeta$','c2':r'$\eta$','d2':r'$\theta$','a3':r'$\iota$','b3':r'$\kappa$','c3':r'$\lambda$','d3':r'$\mu$','top':r'$\varphi$'}

if 'score' not in st.session_state: st.session_state.score = 0
if 'mode' not in st.session_state: st.session_state.mode = "Normal"
if 'current_task' not in st.session_state: st.session_state.current_task = None
if 'feedback' not in st.session_state: st.session_state.feedback = None

def generate_task():
    mode = st.session_state.mode
    
    if mode == "Innenwinkelsumme":
        # Dreiecks-Modus: t und s müssen unterschiedliche Winkel haben
        t_angle = random.randint(35, 65)
        s_angle = random.randint(115, 145)
        
        # Gegebene Winkel an der unteren Parallele h
        val1 = t_angle
        val2 = 180 - s_angle
        # Ziel: Innenwinkelsumme 180 - (t_angle + (180-s_angle))
        correct = 180 - (val1 + val2)
        
        st.session_state.current_task = {
            'p_angle': 0, 't_angle': t_angle, 's_angle': s_angle,
            'mode': "triangle",
            'given1_pos': 'a2', 'given1_val': val1, 'given1_ui': UI_SYMBOLS['a2'], 'given1_plot': PLOT_SYMBOLS['a2'],
            'given2_pos': 'b4', 'given2_val': val2, 'given2_ui': UI_SYMBOLS['b2'], 'given2_plot': PLOT_SYMBOLS['b2'],
            'target_pos': 'top', 'target_ui': UI_SYMBOLS['top'], 'target_plot': PLOT_SYMBOLS['top'],
            'correct_answer': int(correct)
        }
    else:
        # Normaler Modus
        t_ang = random.randint(35, 145)
        given_pos = random.choice(['a1','b1','c1','d1'])
        target_pos = random.choice(['a2','b2','c2','d2'])
        inter = t_ang if t_ang <= 90 else 180 - t_ang
        
        def calc_v(p, base): return base if p[0] in ['a','c'] else 180-base
        
        st.session_state.current_task = {
            'p_angle': 0, 't_angle': t_ang, 's_angle': t_ang,
            'mode': "normal",
            'given1_pos': given_pos, 'given1_val': calc_v(given_pos, inter), 'given1_ui': UI_SYMBOLS[given_pos], 'given1_plot': PLOT_SYMBOLS[given_pos],
            'given2_pos': None,
            'target_pos': target_pos, 'target_ui': UI_SYMBOLS[target_pos], 'target_plot': PLOT_SYMBOLS[target_pos],
            'correct_answer': int(calc_v(target_pos, inter))
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

    def draw_l(ang, dist, col='black', lbl=''):
        r = np.radians(ang)
        dx, dy = np.cos(r), np.sin(r)
        nx, ny = -np.sin(r), np.cos(r)
        cx, cy = nx * dist, ny * dist
        ax.plot([cx-10*dx, cx+10*dx], [cy-10*dy, cy+10*dy], color=col, lw=2.5)
        if lbl: ax.text(cx+4.2*dx, cy+4.2*dy+0.2, lbl, fontsize=14, fontstyle='italic', color=col)

    def intersect_safe(a1, d1, a2, d2):
        # Sicherheitscheck gegen Division durch Null (parallele Linien)
        if abs(a1 % 180 - a2 % 180) < 0.1: return np.array([0,0])
        r1, r2 = np.radians(a1), np.radians(a2)
        A = np.array([[-np.sin(r1), np.cos(r1)], [-np.sin(r2), np.cos(r2)]])
        b = np.array([d1, d2])
        return np.linalg.solve(A, b)

    # Zeichnen
    draw_l(0, 1.5, lbl='g')
    draw_l(0, -1.5, lbl='h')
    draw_l(task['t_angle'], 0, col='#FF3B30', lbl='t')
    
    if task['mode'] == "triangle":
        draw_l(task['s_angle'], -0.5, col='orange', lbl='s')

    # Punkte berechnen
    pts = {
        '1': intersect_safe(0, 1.5, task['t_angle'], 0),
        '2': intersect_safe(0, -1.5, task['t_angle'], 0)
    }
    if task['mode'] == "triangle":
        pts['3'] = intersect_safe(0, 1.5, task['s_angle'], -0.5)
        pts['4'] = intersect_safe(0, -1.5, task['s_angle'], -0.5)
        pts['top'] = intersect_safe(task['t_angle'], 0, task['s_angle'], -0.5)

    def draw_wedge(pos, val_plot, is_target):
        if pos == 'top': center = pts['top']
        else: center = pts[pos[1:]]
        
        color = '#FF3B30' if is_target else '#007AFF'
        
        if pos == 'top':
            s, e = task['s_angle'], task['t_angle'] + 180
        else:
            line_a, trans_a = 0, (task['t_angle'] if pos[1] in ['1','2'] else task['s_angle'])
            angles = sorted([line_a, trans_a % 180])
            q = pos[0]
            if q == 'a': s, e = angles[0], angles[1]
            elif q == 'b': s, e = angles[1], angles[0] + 180
            elif q == 'c': s, e = angles[0] + 180, angles[1] + 180
            else: s, e = angles[1] + 180, angles[0] + 360

        ax.add_patch(patches.Wedge(center, 0.7, s, e, color=color, alpha=0.2))
        m = np.radians((s+e)/2)
        ax.text(center[0]+1.2*np.cos(m), center[1]+1.2*np.sin(m), val_plot, 
                fontsize=18, color=color, fontweight='bold', ha='center', va='center')

    # Markierungen einzeichnen
    draw_wedge(task['given1_pos'], task['given1_plot'], False)
    if task['given2_pos']:
        draw_wedge(task['given2_pos'], task['given2_plot'], False)
    draw_wedge(task['target_pos'], task['target_plot'], True)
    
    return fig

# --- UI ---
st.title("📐 Winkel-Trainer Profi")

with st.sidebar:
    st.header("Modus")
    mode_selection = st.radio("Aufgabentyp:", ["Normal", "Innenwinkelsumme"])
    if mode_selection != st.session_state.mode:
        st.session_state.mode = mode_selection
        generate_task(); st.rerun()
    img_w = st.slider("Bildbreite", 4.0, 14.0, 8.0)
    if st.button("Neu würfeln"): generate_task(); st.rerun()

col1, col2 = st.columns([1.6, 1], gap="large")

with col1:
    st.pyplot(create_plot(st.session_state.current_task, img_w))
    if st.session_state.mode == "Innenwinkelsumme":
        st.info("💡 Nutze Stufenwinkel an g || h und dann die Innenwinkelsumme im Dreieck ($180^\\circ$).")

with col2:
    t = st.session_state.current_task
    st.markdown(f"### Score: `{st.session_state.score}`")
    
    txt = f"Gegeben: {t['given1_ui']} = {t['given1_val']}°"
    if t['given2_pos']:
        txt += f"  und  {t['given2_ui']} = {t['given2_val']}°"
    
    st.markdown(f'<div class="given-box">{txt}</div>', unsafe_allow_html=True)
    
    with st.form("input_form"):
        u_val = st.number_input(f"Berechne {t['target_ui']}:", min_value=0, max_value=180, step=1)
        if st.form_submit_button("Überprüfen"):
            if u_val == t['correct_answer']: st.session_state.feedback = "correct"
            else: st.session_state.feedback = "wrong"

    if st.session_state.feedback == "correct":
        st.success("✅ Richtig!")
        if st.button("Nächste Aufgabe ➔"):
            st.session_state.score += 1
            generate_task(); st.rerun()
    elif st.session_state.feedback == "wrong":
        st.error(f"❌ Falsch. (Tipp: Ergebnis ist {t['correct_answer']}°)")

st.markdown(f'<div class="footer">{AUTHOR} - Version {VERSION}</div>', unsafe_allow_html=True)
