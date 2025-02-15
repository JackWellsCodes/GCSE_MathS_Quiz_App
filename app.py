from flask import Flask, render_template, request, redirect, url_for, session
import json
import random
from flask_session import Session
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Configure session
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "your_secret_key"
Session(app)

# Load questions from JSON file
def load_questions():
    with open("questions.json", "r") as file:
        return json.load(file)

# Randomly select 5 questions from the full list
def get_random_questions():
    all_questions = load_questions()
    return random.sample(all_questions, 5)

# Home route - Login page
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        username = request.form.get("username").strip()
        if username:
            session.clear()  # Reset session for a fresh quiz
            session["username"] = username
            session["score"] = 0
            session["question_index"] = 0
            session["questions"] = get_random_questions()
            session["topic_scores"] = {}  # Initialize topic tracking
            return redirect(url_for("quiz"))
    return render_template("index.html")

# Quiz route
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "username" not in session:
        return redirect(url_for("home"))

    questions = session.get("questions", [])
    question_index = session.get("question_index", 0)

    if question_index >= len(questions):
        return redirect(url_for("result"))

    current_question = questions[question_index]

    if request.method == "POST":
        user_answer = request.form.get("answer", "").strip().lower()
        correct_answers = [ans.strip().lower() for ans in current_question["answer"]]

        # Check multiple possible answers (including different orderings)
        if user_answer in correct_answers or any(
            sorted(user_answer) == sorted(ans) for ans in correct_answers
        ):
            session["score"] += 1

            # Track performance by topic
            topic = current_question.get("topic", "Unknown Topic")
            session["topic_scores"][topic] = session["topic_scores"].get(topic, 0) + 1

        session["question_index"] += 1
        return redirect(url_for("quiz"))

    return render_template(
        "quiz.html",
        question=current_question,
        question_num=question_index + 1,
        total=len(questions),
        score=session["score"],
    )

# Generate results with a bar chart
@app.route("/result")
def result():
    username = session.get("username", "User")
    score = session.get("score", 0)
    total = len(session.get("questions", []))
    topic_scores = session.get("topic_scores", {})

    # Generate a performance bar chart
    chart_path = "static/performance_chart.png"
    if topic_scores:
        topics = list(topic_scores.keys())
        scores = list(topic_scores.values())

        plt.figure(figsize=(8, 5))
        plt.bar(topics, scores, color="skyblue")
        plt.xlabel("Topics")
        plt.ylabel("Correct Answers")
        plt.title(f"Performance of {username}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
    else:
        if os.path.exists(chart_path):
            os.remove(chart_path)

    return render_template(
        "result.html",
        score=score,
        total=total,
        username=username,
        topics=topic_scores,
        chart_path=chart_path,
    )

if __name__ == "__main__":
    app.run(debug=True)

