from openai import OpenAI

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