import re
from sys import path
from flask import Flask, render_template, redirect, url_for, request, abort, flash, send_file, session, jsonify
from werkzeug.utils import send_from_directory
from wtforms import StringField, SubmitField, PasswordField, validators
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_manager, login_user, login_required, logout_user, current_user
from wtforms.validators import EqualTo, InputRequired, Email, Length, ValidationError, DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import subprocess
from subprocess import Popen, PIPE, check_output
import os

app = Flask(__name__)
app.secret_key = 'mykey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
# redirect to login page if not logged in.
login_manager.login_view = 'login'

# Database table for users
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

#User Loader
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

#Forms
class RegisterForm(FlaskForm):
    username = StringField('Username:', validators=[InputRequired(), Length(max=20)])
    email = StringField('Email Address:', validators=[InputRequired(), Length(max=40)])
    password = PasswordField('Password:', validators=[InputRequired()])
    confirm_password = PasswordField("Password Confirmation:", validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email Address:', validators=[InputRequired(), Length(max=40)])
    password = PasswordField('Password:', validators=[InputRequired()])
    submit = SubmitField('Login')

class SettingsForm(FlaskForm):
    old_password = PasswordField('Old Password:', validators=[InputRequired()])
    new_password = PasswordField('New Password:', validators=[InputRequired()])
    confirm_password = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo('new_password')])
    submit = SubmitField('Save Changes')

#Generate Client csr and key files. Get csr file signed by CA to get client.crt
def clientCertGen():
    command = "/home/server/client-configs/autoFillSign.sh; mv /home/server/client-configs/keys/client.key /home/server/client-configs/keys/" + current_user.username + ".key; mv /home/server/client-configs/keys/client.crt /home/server/client-configs/keys/"  + current_user.username + ".crt"
    process = subprocess.run(command, stdout=PIPE, stderr=None, shell=True)
    output = process.stdout.decode()
    return output

#Generate .ovpn file with make_config
def vpnFileGen():
    command = "/home/server/client-configs/make_config.sh " + current_user.username + "; rm -f /home/server/client-configs/client.csr"
    process = subprocess.run(command, stdout=PIPE, stderr=None, shell=True)
    output = process.stdout.decode()
    return output

#Remove files when client deletes their account
def removeFiles():
    command = "rm -f /home/server/client-configs/keys/" + current_user.username + ".key /home/server/client-configs/keys/" + current_user.username + ".crt; rm -f /home/server/client-configs/files/" + current_user.username + ".ovpn"
    process = subprocess.run(command, stdout=PIPE, stderr=None, shell=True)
    output = process.stdout.decode()
    return output

#Home page
@app.route('/')
def index():
    return render_template('index.html')

#About page explaining Openvpn and benefits
@app.route('/about')
def about():
    return render_template('about.html')

#Let users register their account
@app.route('/register', methods = ['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        exist_user = User.query.filter_by(username=username).first()
        exist_email = User.query.filter_by(email=email).first()
        if exist_user:
            flash('This username is already taken.')
            return redirect(url_for('register'))
        elif exist_email:
            flash('This Email is already in use.')
            return redirect(url_for('register'))
        elif form.password.data != form.confirm_password.data:
            flash("Password confirmation does not match. Please try again.")
            return redirect(url_for('register'))
        elif len(password) < 8 or len(password) > 20:
            flash("Password should be between 8 and 20 characters.")
            return redirect(url_for('register'))
        elif form.password.data != form.confirm_password.data:
            flash("Password confirmation does not match. Please try again.")
            return redirect(url_for('account'))
        else:
            hashed_password = generate_password_hash(password, method='sha256')
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('New account confirmed. Please Login.')
            return redirect(url_for('login'))
    return render_template('signup.html', form=form)

#Let users login
@app.route('/login', methods = ['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Password is invalid.')
                return redirect(url_for('login'))
        else:
            flash('Invalid Email.')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

#Let users logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#Function to create .ovpn file with shell scripts
@app.route('/createVPN', methods = ['POST', 'GET'])
@login_required
def createVPN():
    clientCertGen()
    vpnFileGen()
    flash(current_user.username + "'s Public key and Private key have been generated. OpenVPN file is ready to download.")
    #messages = "Hello world"
    return redirect(url_for('index'))

#Let clients download .ovpn file
@app.route('/downloadFile', methods = ['POST', 'GET'])
def downloadFile():
    try:
        path = "/home/server/client-configs/files/" + current_user.username + ".ovpn"
        if request.method == "GET":
            return send_file(path, as_attachment=True)
    except:
        flash('Download is not available. Please Generate keys first.')
        return redirect(url_for('index'))

#Page that explains how to configure .ovpn on client side
@app.route('/setup')
@login_required
def setup():
    return render_template('setup.html')

#User account settings
@app.route('/account', methods = ['POST', 'GET'])
@login_required
def account():
    form = SettingsForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if check_password_hash(user.password, form.old_password.data):
            password = form.new_password.data
            hashed_password = generate_password_hash(password, method='sha256')
            if len(password) > 8 and len(password) < 20:
                User.query.filter(User.id==current_user.id).update({'password':hashed_password},synchronize_session=False)
                db.session.commit()
                flash("Password successfully changed.")
                return redirect(url_for('index'))
            elif len(form.new_password.data) < 8 or len(form.new_password.data) > 20:
                flash("Password must be between 8 and 20 characters.")
                return redirect(url_for('account'))
            else:
                flash("Password confirmation does not match. Please try again.")
                return redirect(url_for('account'))
        else:
            flash("Old Password invalid.")
            return redirect(url_for('account'))
    return render_template("account.html", form=form)

#Delete user account
@app.route("/deleteAccount", methods = ["POST", "GET"])
@login_required
def deleteAccount():
    removeFiles()
    User.query.filter_by(id=current_user.id).delete()
    db.session.commit()
    flash("Account has been deleted.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
    #app.run(host="10.110.207.139", port=80, debug=True)