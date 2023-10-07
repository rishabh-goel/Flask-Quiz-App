from flask import Flask, redirect, render_template, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key= 'qwerty'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

key = Fernet.generate_key()
cipher_suite = Fernet(key)


class User(db.Model):
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.LargeBinary(200))


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

        new_user = User(first_name=fname, last_name=lname, email=email,
                        password=cipher_suite.encrypt(bytes(pwd, 'utf-8')))
        db.session.add(new_user)
        db.session.commit()
        flash('Thanks for registering! Your account has been created', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=False)
    # pwd = "Hello"
    # encrypt = cipher_suite.encrypt(bytes(pwd, 'utf-8'))
    # decrypt = str(cipher_suite.decrypt(encrypt), encoding='utf-8')
