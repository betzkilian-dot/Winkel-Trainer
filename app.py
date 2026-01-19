import streamlit as st
import random

# Konfiguration der Seite für Apple-Geräte (responsive)
st.set_page_config(page_title="Winkel-Trainer", layout="wide")

# CSS für Apple-Look und Layout
st.markdown("""
    <style>
    .main { background-color: #F2F2F7; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    div[data-testid="column"] { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #D1D1D6; }
    </style>
    """, unsafe_allow_html=True)

# --- Logik & Session State ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'task_ready' not in st.session_state:
    st.session_state.task_ready = False
if 'current_task' not in st.session_state:
    st.session_state.current_task = None

def generate_new_task():
    base_angle = random.randint(35, 145)
    if base_angle == 90: base_angle = 82
    
    keys = ['a1', 'b1', 'c1', 'd1', 'a2', 'b2', 'c2', 'd2']
    given_pos = random.choice(keys)
    target_pos = random.choice([k for k in keys if k != given_pos])
    
    def get_val(pos, base):
        return base if pos in ['a1', 'c1', 'a2', 'c2'] else 180 - base

    st.session_state.current_task = {
        'given_pos': given_pos,
        'target_pos': target_pos,
        'given_val': get_val(given_pos, base_angle),
        'correct_answer': get_val(target_pos, base_angle)
    }
    st.session_state.feedback = None
    st.session_state.task_ready = True

if st.session_state.current_task is None:
    generate_new_task()

# --- SVG Zeichnung ---
def get_svg(task):
    # Koordinaten-Mapping
    pos_map = {
        'a1': (335, 125), 'b1': (270, 125), 'c1': (265, 175), 'd1': (330, 175),
        'a2': (210, 275), 'b2': (145, 275), 'c2': (140, 325), 'd2': (205, 325)
    }
    g_val = task['given_val']
    g_pos = pos_map[task['given_pos']]
    t_pos = pos_map[task['target_pos']]

    svg = f"""
    <svg width="100%" height="400" viewBox="0 0 500 400" xmlns="http://www.w3.org/2000/svg">
        <line x1="50" y1="150" x2="450" y2="150" stroke="black" stroke-width="3" />
        <line x1="50" y1="300" x2="450" y2="300" stroke="black" stroke-width="3" />
        <text x="465" y="155" font-style="italic" font-family="Arial">g</text>
        <text x="465" y="305" font-style="italic" font-family="Arial">h</text>
        <line x1="100" y1="380" x2="400" y2="70" stroke="#FF3B30" stroke-width="3" />
        <text x="410" y="60" fill="#FF3B30" font-style="italic" font-family="Arial">t</text>
        
        <text x="{g_pos[0]}" y="{g_pos[1]}" fill="#007AFF" font-weight="bold" font-family="Arial" font-size="16">{g_val}°</text>
        <circle cx="{t_pos[0]}" cy="{t_pos[1]-5}" r="15" fill="none" stroke="#FF3B30" stroke-width="2" />
        <text x="{t_pos[0]-5}" y="{t_pos[1]}" fill="#FF3B30" font-weight="bold" font-family="Arial" font-size="20">?</text>
    </svg>
    """
    return svg

# --- UI Layout ---
st.title("📐 Winkel-Trainer")
st.subheader("Gymnasium Bayern | Klasse 7 | g || h")

if st.session_state.score >= 10:
    st.balloons()
    st.success("🎉 Glückwunsch! Du hast 10 Aufgaben richtig gelöst!")
    if st.button("Training neustarten"):
        st.session_state.score = 0
        generate_new_task()
        st.rerun()
else:
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.markdown(get_svg(st.session_state.current_task), unsafe_allow_html=True)
        st.info("Bestimme das Maß des rot markierten Winkels. Die Geraden g und h sind parallel.")

    with col2:
        st.write(f"### Dein Fortschritt: {st.session_state.score} / 10")
        
        with st.form("check_form", clear_on_submit=False):
            user_input = st.number_input("Winkel in Grad (°):", min_value=0, max_value=360, step=1, key="answer_input")
            submit = st.form_submit_button("Überprüfe")
            
            if submit:
                if user_input == st.session_state.current_task['correct_answer']:
                    st.session_state.feedback = ("success", "Richtig! Sehr gut.")
                    st.session_state.score += 1
                else:
                    st.session_state.feedback = ("error", f"Leider falsch. Schau dir die Winkelbeziehung noch einmal an.")

        if st.session_state.feedback:
            if st.session_state.feedback[0] == "success":
                st.success(st.session_state.feedback[1])
            else:
                st.error(st.session_state.feedback[1])

        if st.button("Nächste Aufgabe ➔"):
            generate_new_task()
            st.rerun()

st.caption("ByLKI Winkel-Trainer für bayerische Gymnasien. Hinweis: Informationen bitte stets verifizieren.")