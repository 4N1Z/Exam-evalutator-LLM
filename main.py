import os
from openai import OpenAI
import streamlit as st
import json

# Move API key to .env file for security
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set page configuration
st.set_page_config(
    page_title="Smart Learning Quiz",
    page_icon="📚",
    layout="wide"
)

# Custom CSS to improve the look and feel
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-size: 16px;
    }
    .question-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success-text {
        color: #28a745;
    }
    .error-text {
        color: #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

class QuestionGenerator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        
    def generate_mcq(self, topic, num_questions=10):
        prompt = f"""Generate {num_questions} multiple choice questions about {topic}.
        Create an equal distribution of questions across three difficulty levels:
        - Easy (basic concept understanding)
        - Medium (application of concepts)
        - Hard (analysis and advanced understanding)

        The questions should be ordered from Easy → Medium → Hard.
        
        Return the response in the following JSON format:
        {{
            "questions": [
                {{
                    "question": "The question text",
                    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
                    "correct_answer": "The correct option letter (A/B/C/D)",
                    "explanation": "Brief explanation of the correct answer",
                    "difficulty": "easy/medium/hard",
                    "topic_area": "specific subtopic within {topic}"
                }}
            ]
        }}

        Guidelines for each difficulty:
        - Easy: Direct concept questions, straightforward application
        - Medium: Questions requiring understanding of relationships between concepts
        - Hard: Questions requiring analysis, evaluation, or multiple concept integration

        Ensure each question:
        1. Is clear and age-appropriate for 10th grade
        2. Has one definitively correct answer
        3. Has plausible distractors
        4. Includes a helpful explanation
        """

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response and extract the questions array
        response_data = json.loads(response.choices[0].message.content)
        return response_data.get("questions", [])

class AnswerEvaluator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
    
    def evaluate_answer(self, question_data, student_answer):
        is_correct = student_answer.upper() == question_data["correct_answer"]
        
        prompt = f"""
        Question: {question_data['question']}
        Student's answer: {student_answer}
        Correct answer: {question_data['correct_answer']}
        
        Provide a detailed evaluation including:
        1. Whether the answer is correct
        2. Explanation of why it's correct/incorrect
        3. Key concepts the student should review if needed
        4. Suggestions for improvement
        """
        
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o-mini"
        )
        
        return {
            "is_correct": is_correct,
            "feedback": response.choices[0].message.content
        }

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

def main():
    st.title("📚 Smart Learning Quiz")
    st.markdown("### Welcome to your interactive learning journey! 🌟")
    initialize_session_state()
    
    question_generator = QuestionGenerator(OPENAI_API_KEY)
    answer_evaluator = AnswerEvaluator(OPENAI_API_KEY)

    # Topic Selection and Question Generation
    if not st.session_state.questions:
        st.markdown("""
        #### 🎯 Let's get started!
        Choose a subject you'd like to practice. It can be anything from Math to Science to History!
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
        # Progress bar
        progress = st.session_state.current_question / st.session_state.total_questions
        st.progress(progress)
        st.markdown(f"Question {st.session_state.current_question + 1} of {st.session_state.total_questions}")

        if st.session_state.current_question < len(st.session_state.questions):
            current_q = st.session_state.questions[st.session_state.current_question]
            
            # Display question in a nice box with difficulty badge
            with st.container():
                st.markdown("---")
                # Add difficulty badge with appropriate color
                difficulty_colors = {
                    "easy": "green",
                    "medium": "orange",
                    "hard": "red"
                }
                difficulty = current_q['difficulty'].lower()
                st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>Question {st.session_state.current_question + 1} 📝</h3>
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
                
                # Display options in a cleaner format
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

        # Evaluation
        elif not st.session_state.evaluation_complete and len(st.session_state.answers) == len(st.session_state.questions):
            st.markdown("### 🎉 You've completed all questions!")
            if st.button("See How You Did! 🌟"):
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
            
            # Display score with encouraging message
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
            
            # Option to start new quiz
            if st.button("Start a New Quiz! 🚀"):
                st.session_state.clear()
                st.rerun()

if __name__ == "__main__":
    main()
