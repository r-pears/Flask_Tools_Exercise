from flask import Flask, session, request, render_template, redirect, make_response, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

CURRENT_SURVEY = 'current_survey'
RESPONSES = 'responses'

app = Flask(__name__)
app.config['SECRET_KEY'] = "my-secret-password"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route("/")
def surveys_home():
    """Choose a survey"""

    return render_template("survey_home.html", surveys=surveys)


@app.route("/", methods=["POST"])
def pick_survey():
    """Chosen survey, checks if it has been taken before or not."""

    survey_id = request.form['survey_code']

    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("completed.html")

    survey = surveys[survey_id]
    session[CURRENT_SURVEY] = survey_id

    return render_template("survey_start.html", survey=survey)


@app.route("/start", methods=["POST"])
def start_survey():
    """Start the survey and clear the session."""

    session[RESPONSES] = []

    return redirect("/questions/0")


@app.route("/questions/<int:qid>")
def show_question(qid):
    """Show the current question."""

    responses = session.get(RESPONSES)
    survey_code = session[CURRENT_SURVEY]
    survey = surveys[survey_code]

    if (responses is None):
        return redirect("/")

    if (len(responses) == len(survey.questions)):
        return redirect("/finish")

    if (len(responses) != qid):
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]

    return render_template(
        "question.html", question_num=qid, question=question)


@app.route("/answer", methods=["POST"])
def handle_answer():
    """Records the answer and then moves along to the next question."""

    choice = request.form['answer']
    text = request.form.get("text", "")

    responses = session[RESPONSES]
    responses.append({"choice": choice, "text": text})

    session[RESPONSES] = responses
    survey_code = session[CURRENT_SURVEY]
    survey = surveys[survey_code]

    if (len(responses) == len(survey.questions)):
        return redirect("/finish")

    else:
        return redirect(f"/questions/{len(responses)}")


@app.route("/finish")
def finish_survey():
    """Survey finished! Show a thank you for participating message."""

    survey_id = session[CURRENT_SURVEY]
    survey = surveys[survey_id]
    responses = session[RESPONSES]

    html = render_template("finish.html", survey=survey, responses=responses)

    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response
