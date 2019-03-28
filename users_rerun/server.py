from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import connectToMySQL
import re
from flask_bcrypt import Bcrypt
app = Flask(__name__)
app.secret_key = 'into the spiderverse'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.+_-]+\.[a-zA_Z]+$')
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/home/register', methods=['POST'])
def register():
    mysql = connectToMySQL('users_rerun')
    is_valid = True
    query = 'SELECT email FROM users WHERE email = %(em)s;'
    data = {'em': request.form['user_email']}
    existing_user = mysql.query_db(query, data)
    if len(request.form['fname']) < 1:
        is_valid = False
        flash('Please enter a first name')
    if len(request.form['lname']) < 1:
        is_valid = False
        flash('Please enter a last name')
    if existing_user:
        is_valid = False
        flash('Email already used to register')
    if not EMAIL_REGEX.match(request.form['user_email']):
        flash('Invalid email address')
    if len(request.form['pw']) < 8:
        flash('Password must be at least 8 characters')
    if request.form['pw'] != request.form['confirm_pw']:
        is_valid = False
        flash('Passwords do not match')
        return redirect('/home')
    pw_hash = bcrypt.generate_password_hash(request.form['pw'])
    if is_valid:
        mysql = connectToMySQL('users_rerun')
        query = 'INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(password_hash)s, NOW(), NOW());'
        data = {'fn': request.form['fname'], 'ln': request.form['lname'], 'em': request.form['user_email'], 'password_hash': pw_hash}
        new_user_id = mysql.query_db(query, data)
    if is_valid == False:
        return redirect('/home')
    return redirect('/home/register_success')

@app.route('/home/register_success')
def register_success():
    flash('You have successfully registered')
    return redirect('/home')

@app.route('/home/login', methods=['POST'])
def login():
    mysql = connectToMySQL('users_rerun')
    query = 'SELECT * FROM users WHERE email = %(em)s;'
    data = {'em': request.form['user_email']}
    result = mysql.query_db(query, data)
    if result:
        if bcrypt.check_password_hash(result[0]['password'], request.form['pw']):
            session['user_id'] = result[0]['id']
            return redirect('/wall')
    flash('You could not be logged in')
    return redirect('/home')

@app.route('/wall')
def wall():
    mysql = connectToMySQL('users_rerun')
    query = 'SELECT * FROM users WHERE users.id = '+ str(session['user_id'])+';'
    user = mysql.query_db(query)
    mysql = connectToMySQL('users_rerun')
    query = 'SELECT * FROM users'
    friend = mysql.query_db(query)
    mysql = connectToMySQL('users_rerun')
    query = 'SELECT messages.id, messages.message, messages.sender_id, messages.receiver_id, users.first_name as sender FROM messages JOIN users ON users.id = messages.sender_id AND messages.receiver_id = %(id)s WHERE messages.receiver_id = %(id)s;'
    data = {'id': session['user_id']}
    message = mysql.query_db(query, data)
    if 'user_id' not in session:
        return redirect('/')
    return render_template('wall.html', user = user, friend = friend, message = message)

@app.route('/wall/send', methods=['POST'])
def send():
    mysql = connectToMySQL('users_rerun')
    query = 'INSERT INTO messages (message, sender_id, receiver_id, created_at, updated_at) VALUES (%(mess)s, %(sender)s, %(receiver)s, NOW(), NOW());'
    data = {'mess': request.form['message_box'], 'sender': session['user_id'], 'receiver': request.form['friend']}
    new_message_id = mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/wall/destroy/<id>')
def delete(id):
    mysql = connectToMySQL('users_rerun')
    query = 'DELETE FROM messages WHERE id = %(id)s;'
    data = {'id': id}
    delete_message = mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    return redirect('/')

if __name__=='__main__':
    app.run(debug=True)