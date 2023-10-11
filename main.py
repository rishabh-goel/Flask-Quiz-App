import uuid

from flask import Flask, redirect, render_template, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, DateTime, Time
from datetime import datetime, timedelta, time

app = Flask(__name__)
app.secret_key = 'qwerty'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(100))


class TestQues(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    category = db.Column(db.String(100))
    ques = db.Column(db.String(500))
    option1 = db.Column(db.String(200))
    option2 = db.Column(db.String(200))
    option3 = db.Column(db.String(200))
    option4 = db.Column(db.String(200))
    correctAns = db.Column(db.String(200))


class TestResults(db.Model):
    id = db.Column(db.String(100), primary_key=True, default=str(uuid.uuid4()), unique=True)
    testDate = db.Column(DateTime)
    category = db.Column(db.String(100))
    time = db.Column(Time)
    score = db.Column(db.String(200))


def add_data_to_question_database(id, category, ques, op1, op2, op3, op4, correct):
    try:
        # Create an instance of the model and populate its attributes
        new_data = TestQues(id=id, category=category, ques=ques, option1=op1, option2=op2, option3=op3, option4=op4,
                            correctAns=correct)
        # Add the instance to the database session
        db.session.add(new_data)
        # Commit the changes to the database
        db.session.commit()
        return "Data added successfully."
    except Exception as e:
        # Handle any errors, such as a database integrity error or validation error
        db.session.rollback()
        return "An error occurred while adding data: " + str(e)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        pwd = request.form.get('pwd')
        confirm_pwd = request.form.get('confirm_pwd')

        if fname == "" or lname == "" or email == "" or pwd == "" or confirm_pwd == "":
            # TODO: throw an error that fields are empty
            return render_template('register.html')

        if pwd != confirm_pwd:
            # TODO: throw an error that passwords don't match
            return render_template('register.html')

        new_user = User(first_name=fname, last_name=lname, email=email, password=pwd)
        db.session.add(new_user)
        db.session.commit()
        flash('Thanks for registering! Your account has been created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('pwd')

        user = User.query.filter_by(email=email).first()

        if user is None:
            flash('User not found', 'failure')
        else:
            if pwd == user.password:
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password', 'failure')
    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')


@app.route('/results', methods=['GET', 'POST'])
def results():
    return render_template('results.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return redirect(url_for('index'))


@app.route('/get-test', methods=['POST'])
def get_test():
    category = request.form.get('category')
    ques_list = TestQues.query.filter_by(category=category).all()
    return render_template('questions.html', questions=ques_list)


@app.route('/check-answers', methods=['POST'])
def check_answers():
    answers = request.get_json()
    count = 0

    category = answers[0]['questionId'].split('-')[0]
    total = db.session.query(func.count(TestQues.id)).filter(TestQues.category == category).scalar()

    for answer in answers:
        question_id = answer['questionId']
        user_answer = answer['selectedAnswer']
        entry = TestQues.query.filter_by(id=question_id).first()

        if user_answer == entry.correctAns:
            count += 1

    result = {'score': f'{count}/{total}', 'category': category}
    return jsonify(result)


@app.route('/store-results', methods=['POST'])
def store_results():
    result = request.json
    seconds = result.get('time')
    time_object = timedelta(seconds=seconds)
    formatted_time = time(time_object.seconds // 3600, (time_object.seconds // 60) % 60, time_object.seconds % 60)
    new_result = TestResults(testDate=datetime.now(), category=result.get('category'), time=formatted_time,
                             score=result.get('score'))
    db.session.add(new_result)
    db.session.commit()
    return jsonify({"message": "Results stored successfully"})


@app.route('/get-test-results', methods=['GET'])
def get_test_results():
    # Fetch test results from the database (you might want to filter, sort, etc.)
    test_results = TestResults.query.all()

    # Create a list of dictionaries for the results
    results_list = []
    for result in test_results:
        results_list.append({
            'testDate': result.testDate.strftime('%Y-%m-%d %H:%M:%S'),  # Format the date
            'category': result.category,  # Replace with your actual column name
            'time': result.time.strftime('%H:%M:%S'),  # Format the time
            'score': result.score,  # Replace with your actual column name
        })

    return jsonify(testResults=results_list)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if db.session.query(TestQues).first() is None:
            add_data_to_question_database('mcq-1', 'mcq', 'ques1', 'op1', 'op2', 'op3', 'op4', 'op1')
            add_data_to_question_database('mcq-2', 'mcq', 'ques2', 'op1', 'op2', 'op3', 'op4', 'op1')
            add_data_to_question_database('mcq-3', 'mcq', 'ques3', 'op1', 'op2', 'op3', 'op4', 'op1')
            add_data_to_question_database('mcq-4', 'mcq', 'ques4', 'op1', 'op2', 'op3', 'op4', 'op1')
            add_data_to_question_database('mcq-5', 'mcq', 'ques5', 'op1', 'op2', 'op3', 'op4', 'op1')

            add_data_to_question_database('synonym-1', 'synonym', 'ques1', 'op1', 'op2', 'op3', 'op4', 'op1')
            add_data_to_question_database('synonym-2', 'synonym', 'ques2', 'op1', 'op2', 'op3', 'op4', 'op1')
            add_data_to_question_database('synonym-3', 'synonym', 'ques3', 'op1', 'op2', 'op3', 'op4', 'op1')
            add_data_to_question_database('synonym-4', 'synonym', 'ques4', 'op1', 'op2', 'op3', 'op4', 'op1')
            add_data_to_question_database('synonym-5', 'synonym', 'ques5', 'op1', 'op2', 'op3', 'op4', 'op1')

            add_data_to_question_database('test_completion-1', 'test_completion', 'ques1', 'op1', 'op2', 'op3', 'op4', 'op1')
            add_data_to_question_database('test_completion-2', 'test_completion', 'ques2', 'op1', 'op2', 'op3', 'op4', 'op1')
            add_data_to_question_database('test_completion-3', 'test_completion', 'ques3', 'op1', 'op2', 'op3', 'op4', 'op1')
            add_data_to_question_database('test_completion-4', 'test_completion', 'ques4', 'op1', 'op2', 'op3', 'op4', 'op1')
            add_data_to_question_database('test_completion-5', 'test_completion', 'ques5', 'op1', 'op2', 'op3', 'op4', 'op1')

    app.run(debug=False, port=3000)

