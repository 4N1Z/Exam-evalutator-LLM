import os
import streamlit as st
from dotenv import load_dotenv

from src.question_generator import QuestionGenerator
from src.answer_evaluator import AnswerEvaluator
from src.ui_components import (
    load_css, 
    initialize_session_state, 
    display_question,
    display_score
)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set page configuration
st.set_page_config(
    page_title="Smart Learning Quiz",
    page_icon="📚",
    layout="wide"
)

def main():
    load_css()
    st.title("📚 Smart Learning Quiz")
    st.markdown("### Welcome to your interactive learning journey! 🌟")
    initialize_session_state()
    
    question_generator = QuestionGenerator(OPENAI_API_KEY)
    answer_evaluator = AnswerEvaluator(OPENAI_API_KEY)

    # Topic Selection and Question Generation
    if not st.session_state.questions:
        st.markdown("""
        #### 🎯 Let's get started!
        Choose a subject you'd like to practice from class 10th syllabus.
        """)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            topic = st.text_input("What would you like to learn about today?", 
                                placeholder="For example: Trigonometry, Chemical Reactions, World War II...")
        with col2:
            if st.button("Start Quiz! 🚀"):
                with st.spinner("Creating your personalized quiz... 🎯"):
                    questions = question_generator.generate_mcq(topic)
                    if questions:
                        st.session_state.questions = questions
                        st.session_state.total_questions = len(questions)
                        st.balloons()
                    else:
                        st.error("Oops! Something went wrong. Let's try again! 😅")
                    st.rerun()

    # Question Display and Answer Collection
    if hasattr(st.session_state, 'questions') and st.session_state.questions:
        progress = st.session_state.current_question / st.session_state.total_questions
        st.progress(progress)
        st.markdown(f"Question {st.session_state.current_question + 1} of {st.session_state.total_questions}")

        if st.session_state.current_question < len(st.session_state.questions):
            current_q = st.session_state.questions[st.session_state.current_question]
            
            with st.container():
                st.markdown("---")
                display_question(current_q, st.session_state.current_question + 1)
                
                answer = st.radio(
                    "Choose your answer:",
                    ["A", "B", "C", "D"],
                    format_func=lambda x: f"{x}) {current_q['options'][ord(x)-ord('A')][3:]}",
                    key=f"q_{st.session_state.current_question}"
                )
                
                col1, col2, col3 = st.columns([1,1,1])
                with col2:
                    if st.button("Submit Answer ✨"):
                        st.session_state.answers[st.session_state.current_question] = answer
                        st.session_state.current_question += 1
                        st.rerun()

        # Evaluation Button
        elif not st.session_state.evaluation_complete and len(st.session_state.answers) == len(st.session_state.questions):
            st.markdown("### 🎉 You've completed all questions!")
            col1, col2, col3 = st.columns([1,1,1])
            with col2:
                if st.button("Evaluate My Answers! 🎯"):
                    st.session_state.evaluation_complete = True
                    st.rerun()

        # Display Results
        if st.session_state.evaluation_complete:
            st.header("📊 Your Quiz Results")
            correct_count = 0
            
            for i, (question, answer) in enumerate(st.session_state.answers.items()):
                question_data = st.session_state.questions[question]
                evaluation = answer_evaluator.evaluate_answer(question_data, answer)
                
                if evaluation["is_correct"]:
                    correct_count += 1
                
                with st.expander(f"Question {i + 1} - {'✅ Correct!' if evaluation['is_correct'] else '❌ Let\'s Review'}"):
                    st.markdown(f"**Question:** {question_data['question']}")
                    st.markdown(f"**Your Answer:** Option {answer}")
                    st.markdown(f"**Correct Answer:** Option {question_data['correct_answer']}")
                    st.markdown("**Feedback:**")
                    st.markdown(evaluation["feedback"])
                    st.markdown("---")
                    if not evaluation["is_correct"]:
                        st.markdown("**💡 Keep Learning:**")
                        st.markdown(question_data["explanation"])
            
            score_percentage = (correct_count / len(st.session_state.questions)) * 100
            display_score(score_percentage)
            
            # Option to start new quiz
            col1, col2, col3 = st.columns([1,1,1])
            with col2:
                if st.button("Start a New Quiz! 🚀"):
                    st.session_state.clear()
                    st.rerun()

if __name__ == "__main__":
    main()
