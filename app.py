import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="PathFinder", page_icon="🧭")

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
if st.session_state.step == 0:
    st.title("🧭 PathFinder")
    name = st.text_input("Enter your name")

    if st.button("Start"):
        if name:
            st.session_state.name = name
            st.session_state.step = 1
            st.rerun()

# QUIZ
elif st.session_state.step == 1:
    df = load_questions()
    i = len(st.session_state.answers)

    if i < len(df):
        row = df.iloc[i]

        st.progress((i + 1) / len(df))
        st.write(f"Q{i+1}: {row['Text']}")

        val = st.radio("Rate:", [1, 2, 3, 4, 5], key=f"q{i}")

        if st.button("Next"):
            st.session_state.answers[row["Question_ID"]] = val
            st.rerun()
    else:
        st.session_state.step = 2
        st.rerun()

# RESULT
elif st.session_state.step == 2:
    df = load_questions()
    scores = calculate_scores(st.session_state.answers, df)
    top = get_top(scores)

    st.success(f"{st.session_state.name}, you are {top}")

    st.bar_chart(pd.DataFrame(scores, index=[0]).T)

    if st.button("Restart"):
        st.session_state.step = 0
        st.session_state.answers = {}
        st.rerun()
