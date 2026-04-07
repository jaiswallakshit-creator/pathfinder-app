import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="PathFinder Pro", page_icon="🧭", layout="centered")

# ---------- PREMIUM UI ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
.title {
    font-size: 3rem;
    text-align: center;
    font-weight: bold;
    background: linear-gradient(90deg,#00f260,#0575e6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.card {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(15px);
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------- DATA ----------
QUESTIONS = [
("I enjoy building or fixing things", "Realistic"),
("I like solving problems", "Investigative"),
("I love creativity and art", "Artistic"),
("I enjoy helping people", "Social"),
("I like leading and business", "Enterprising"),
("I like organizing data", "Conventional")
]

CAREERS = {
"Realistic":["Engineer","Pilot"],
"Investigative":["Scientist","Doctor"],
"Artistic":["Designer","Writer"],
"Social":["Teacher","Psychologist"],
"Enterprising":["Business","Manager"],
"Conventional":["Accountant","Banker"]
}

# ---------- STATE ----------
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.answers = {}

# ---------- HOME ----------
if st.session_state.step == 0:
    st.markdown('<div class="title">🚀 PathFinder Pro</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    name = st.text_input("Enter your name")

    if st.button("Start Quiz"):
        if name:
            st.session_state.name = name
            st.session_state.step = 1
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- QUIZ ----------
elif st.session_state.step == 1:
    i = len(st.session_state.answers)

    if i < len(QUESTIONS):
        q, trait = QUESTIONS[i]

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f"### Question {i+1}")
        st.write(q)

        val = st.radio("Select:", [1,2,3,4,5], key=f"q{i}")

        if st.button("Next"):
            st.session_state.answers[i] = (trait, val)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.session_state.step = 2
        st.rerun()

# ---------- RESULT ----------
elif st.session_state.step == 2:

    scores = {}
    for t in CAREERS.keys():
        scores[t] = 0

    for _, (trait, val) in st.session_state.answers.items():
        scores[trait] += val

    top = max(scores, key=scores.get)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(f"## 🎯 {st.session_state.name}, You are **{top}**")

    df = pd.DataFrame(scores, index=["Score"]).T
    st.bar_chart(df)

    st.markdown("### 💼 Recommended Careers")
    for c in CAREERS[top]:
        st.write("👉", c)

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Restart"):
        st.session_state.step = 0
        st.session_state.answers = {}
        st.rerun()
