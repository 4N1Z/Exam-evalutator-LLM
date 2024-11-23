import streamlit as st

def load_css():
    with open("styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def initialize_session_state():
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "evaluation_complete" not in st.session_state:
        st.session_state.evaluation_complete = False
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0

def display_question(current_q, question_number):
    difficulty_colors = {
        "easy": "green",
        "medium": "orange",
        "hard": "red"
    }
    difficulty = current_q['difficulty'].lower()
    
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3>Question {question_number} 📝</h3>
            <span style="background-color: {difficulty_colors[difficulty]}; 
                       color: white; 
                       padding: 5px 10px; 
                       border-radius: 15px; 
                       font-size: 0.8em;">
                {difficulty.upper()}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"**{current_q['question']}**")
    if 'topic_area' in current_q:
        st.markdown(f"*Topic Area: {current_q['topic_area']}*")

def display_score(score_percentage):
    st.markdown("### Your Score:")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.metric("", f"{score_percentage:.1f}%")
        
    if score_percentage == 100:
        st.markdown("### 🌟 Perfect Score! You're Amazing! 🌟")
    elif score_percentage >= 80:
        st.markdown("### 🎉 Great Job! You're doing excellent! 🌟")
    elif score_percentage >= 60:
        st.markdown("### 👍 Good effort! Keep practicing! 💪")
    else:
        st.markdown("### 💪 Keep learning! You'll do better next time! 📚") 