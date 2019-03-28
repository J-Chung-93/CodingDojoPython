from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import connectToMySQL
import re
from flask_bcrypt import Bcrypt
app = Flask(__name__)
app.secret_key = "into the spiderverse"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.+_-]+\.[a-zA_Z]+$')
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login')
def login_register():
    return render_template('login_register.html')

@app.route('/login/register', methods=['POST'])
def register():
    mysql = connectToMySQL('login_registration_mysql')
    is_valid = True
    query = 'SELECT email FROM users WHERE email = %(email)s;'
    data = {'email': request.form['email']}
    existing_user = mysql.query_db(query, data)
    print(existing_user)
    if len(request.form['first_name']) < 1:
        is_valid = False
        flash('Please enter a first name')
    if len(request.form['last_name']) < 1:
        is_valid = False
        flash('Please enter a last name')
    if existing_user:
        is_valid = False
        flash('Email already used to register')
    if not EMAIL_REGEX.match(request.form['email']):
        flash('Invalid email address')
    if len(request.form['password']) < 8:
        flash('Password must be at least 8 characters')
    if request.form['password'] != request.form['confirm_password']:
        is_valid = False
        flash('Passwords do not match')
        return redirect('/login')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    if is_valid:
        mysql = connectToMySQL('login_registration_mysql')
        query = 'INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password_hash)s, NOW(), NOW());'
        data = {"first_name": request.form["first_name"], "last_name": request.form["last_name"], "email": request.form["email"], "password_hash": pw_hash}
        new_user_id = mysql.query_db(query, data)
    if is_valid == False:
        return redirect('/login')
    return redirect('/login/register_success')

@app.route('/login/register_success')
def register_success():
    return render_template('register_success.html')

@app.route('/login/attempt', methods=['POST'])
def login_attempt():
    mysql = connectToMySQL('login_registration_mysql')
    query = 'SELECT * FROM users WHERE email = %(email)s;'
    data = {'email': request.form['email']}
    result = mysql.query_db(query, data)
    if result:
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
            session['userid'] = result[0]['id']
            return redirect('/login/success')
    flash('You could not be logged in')
    return redirect('/')

@app.route('/login/success')
def login_success():
    if 'userid' not in session:
        return redirect('/')
    return render_template('login_success.html')

@app.route('/logout')
def logout():
    if 'userid' in session:
        session.pop('userid')
    print("session cleared")
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)