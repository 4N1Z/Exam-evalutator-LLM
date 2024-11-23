from openai import OpenAI
import json

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
        
        response_data = json.loads(response.choices[0].message.content)
        return response_data.get("questions", []) 