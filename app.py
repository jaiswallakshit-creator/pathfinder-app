import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="PathFinder", page_icon="🧭")
st.markdown("""
<style>
/* Background */
.stApp {
    background: linear-gradient(135deg, #141e30, #243b55);
}

/* Title */
.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #00f260, #0575e6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

/* Card */
.card {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(15px);
    margin-bottom: 15px;
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(90deg, #00f260, #0575e6);
    color: white;
    border-radius: 10px;
    font-weight: bold;
    padding: 10px;
}

/* Inputs */
input {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

QUESTIONS_CSV = """Question_ID|Text|Trait
Q01|I enjoy building or fixing mechanical things (machines, electronics, etc.)|Realistic
Q02|I like working outdoors with tools or physical materials|Realistic
Q03|I love solving complex puzzles or mathematical problems|Investigative
Q04|I enjoy conducting experiments or research to understand how things work|Investigative
Q05|I often express myself through art, music, writing, or drama|Artistic
Q06|I prefer tasks that let me use my imagination and creativity|Artistic
Q07|I enjoy helping others with their personal problems or challenges|Social
Q08|I feel energized when teaching or training other people|Social
Q09|I like persuading others and taking on leadership roles|Enterprising
Q10|I enjoy starting new projects and taking calculated risks|Enterprising
Q11|I prefer tasks that follow clear rules, procedures, and deadlines|Conventional
Q12|I like organizing data, keeping records, and maintaining accuracy|Conventional
"""

def load_questions():
    return pd.read_csv(io.StringIO(QUESTIONS_CSV), sep="|")

def calculate_scores(ans, df):
    scores = {t: 0 for t in ["Realistic","Investigative","Artistic","Social","Enterprising","Conventional"]}
    for _, row in df.iterrows():
        scores[row["Trait"]] += ans.get(row["Question_ID"], 0)
    return scores

def get_top(scores):
    return max(scores, key=scores.get)

# SESSION
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.answers = {}

# HOME
st.markdown('<div class="hero-title">🚀 PathFinder Pro</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)

name = st.text_input("👤 Enter your name")

if st.button("Start Your Journey 🚀"):
    if name:
        st.session_state.name = name
        st.session_state.step = 1
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# QUIZ
st.markdown('<div class="card">', unsafe_allow_html=True)

st.progress((i + 1) / len(df))
st.write(f"### 🧠 Question {i+1}")
st.write(row['Text'])

val = st.radio("Select your answer:", [1,2,3,4,5], key=f"q{i}")

st.markdown('</div>', unsafe_allow_html=True)

# RESULT
st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown(f"## 🎯 {st.session_state.name}, You are **{top}**")

st.bar_chart(pd.DataFrame(scores, index=[0]).T)

st.markdown("### 💼 Recommended Careers")

career_map = {
    "Realistic": ["Engineer", "Pilot"],
    "Investigative": ["Doctor", "Scientist"],
    "Artistic": ["Designer", "Writer"],
    "Social": ["Teacher", "Psychologist"],
    "Enterprising": ["Business", "Manager"],
    "Conventional": ["Accountant", "Banker"],
}

for c in career_map[top]:
    st.write("👉", c)

st.markdown('</div>', unsafe_allow_html=True)
