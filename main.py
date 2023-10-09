from flask import Flask, redirect, render_template, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy

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


# TODO: Create method to insert data to table
class TestQues(db.Model):
    category = db.Column(db.String(100), primary_key=True)
    ques = db.Column(db.String(500), primary_key=True)
    option1 = db.Column(db.String(200), primary_key=True)
    option2 = db.Column(db.String(200), primary_key=True)
    option3 = db.Column(db.String(200), primary_key=True)
    option4 = db.Column(db.String(200), primary_key=True)
    correctAns = db.Column(db.String(200), primary_key=True)


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


# TODO: This is not working as POST
@app.route('/get_test', methods=['POST'])
def get_test():
    category = request.form.get('category')
    if request.method == 'POST':
        ques_list = TestQues.query.filter_by(category=category)
        return render_template('questions.html', questions=ques_list)
    return render_template('questions.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=False)
