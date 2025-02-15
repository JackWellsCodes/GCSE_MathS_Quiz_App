from flask import Flask, render_template, request, redirect, url_for, session
import json
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session tracking

# Function to load questions from the JSON file
def load_questions():
    with open("questions.json", "r") as file:
        return json.load(file)

@app.route('/')
def home():
    session.clear()  # Reset the quiz progress
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # Load the full list of questions from the JSON file
    all_questions = load_questions()

    # If the session does not have a set of quiz questions yet, select 5 at random
    if 'quiz_questions' not in session:
        session['quiz_questions'] = random.sample(all_questions, 5)
        session['question_index'] = 0
        session['score'] = 0

    # Retrieve the current set of quiz questions from the session
    quiz_questions = session['quiz_questions']
    index = session['question_index']

    # If all quiz questions have been answered, go to result page
    if index >= len(quiz_questions):
        return redirect(url_for('result'))

    current_question = quiz_questions[index]

    if request.method == 'POST':
        user_answer = request.form.get('answer', '').strip()

        # Get the list of correct answers
        correct_answers = current_question["answer"]

        # Normalize the user answer and correct answers (remove extra spaces and ignore case)
        normalized_user_answer = user_answer.lower().replace(" ", "")
        normalized_correct_answers = [ans.lower().replace(" ", "") for ans in correct_answers]

        if normalized_user_answer in normalized_correct_answers:
            session['score'] += 1

        session['question_index'] += 1  # Move to the next question
        return redirect(url_for('quiz'))

    return render_template(
        'quiz.html',
        question=current_question,
        score=session['score'],
        question_num=index + 1,
        total=len(quiz_questions)
    )

@app.route('/result')
def result():
    return render_template('result.html', score=session.get('score', 0), total=5)

if __name__ == '__main__':
    app.run(debug=True)

