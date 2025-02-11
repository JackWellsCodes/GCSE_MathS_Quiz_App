from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session tracking

# Sample questions stored in a list of dictionaries
questions = [
    {"question": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "answer": "4"},
    {"question": "What is the capital of France?", "options": ["Berlin", "Madrid", "Paris", "Lisbon"], "answer": "Paris"},
    {"question": "What is 5 * 3?", "options": ["15", "20", "25", "30"], "answer": "15"}
]

@app.route('/')
def home():
    session.clear()  # Reset the quiz progress
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'score' not in session:
        session['score'] = 0
        session['question_index'] = 0

    if session['question_index'] >= len(questions):
        return redirect(url_for('result'))

    if request.method == 'POST':
        selected_option = request.form.get('answer')
        correct_answer = questions[session['question_index']]['answer']

        if selected_option == correct_answer:
            session['score'] += 1

        session['question_index'] += 1  # Move to the next question
        return redirect(url_for('quiz'))  # Reload quiz page

    return render_template('quiz.html', 
                           question=questions[session['question_index']], 
                           score=session['score'], 
                           question_num=session['question_index'] + 1)

@app.route('/result')
def result():
    return render_template('result.html', score=session['score'], total=len(questions))

if __name__ == '__main__':
    app.run(debug=True)

