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
    return render_template('home.html')

@app.route('/submit', methods=['POST'])
def register():
    mysql = connectToMySQL('email_validation')
    is_valid = True
    query = 'SELECT email FROM users WHERE email = %(em)s;'
    data = {'em': request.form['email']}
    existing_user = mysql.query_db(query, data)
    if existing_user:
        is_valid = False
        flash('Email already used to register')
    if not EMAIL_REGEX.match(request.form['email']):
        flash('Invalid email address')
    if is_valid == False:
        return redirect('/')
    if is_valid:
        mysql = connectToMySQL('email_validation')
        query = 'INSERT INTO users (email, created_at, updated_at) VALUES (%(email)s, NOW(), NOW());'
        data = {"email": request.form["email"]}
        new_user_id = mysql.query_db(query, data)
    return redirect('/success')

@app.route('/success')
def success():
    mysql = connectToMySQL('email_validation')
    query = 'SELECT * FROM users'
    all_user = mysql.query_db(query)
    flash('You have successfully registered!')
    return render_template('success.html', user = all_user)

if __name__=='__main__':
    app.run(debug=True)