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
    return redirect('/home')

@app.route('/home')
def login_register():
    return render_template('home.html')

@app.route('/home/register', methods=['POST'])
def register():
    mysql = connectToMySQL('private_wall_mysql')
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
        return redirect('/home')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    if is_valid:
        mysql = connectToMySQL('private_wall_mysql')
        query = 'INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password_hash)s, NOW(), NOW());'
        data = {"first_name": request.form["first_name"], "last_name": request.form["last_name"], "email": request.form["email"], "password_hash": pw_hash}
        new_user_id = mysql.query_db(query, data)
    if is_valid == False:
        return redirect('/home')
    return redirect('/home/register_success')

@app.route('/home/register_success')
def register_success():
    flash('You have successfully registered')
    return redirect('/home')

@app.route('/home/login', methods=['POST'])
def login_attempt():
    mysql = connectToMySQL('private_wall_mysql')
    query = 'SELECT * FROM users WHERE email = %(email)s;'
    data = {'email': request.form['email']}
    result = mysql.query_db(query, data)
    if result:
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
            session['userid'] = result[0]['user_id']
            return redirect('/wall')
    flash('You could not be logged in')
    return redirect('/')

@app.route('/wall')
def login_success():
    mysql = connectToMySQL('private_wall_mysql')
    query = 'SELECT * FROM users WHERE users.user_id = '+ str(session['userid'])+';'
    user = mysql.query_db(query)
    mysql = connectToMySQL('private_wall_mysql')
    query = 'SELECT * FROM users'
    friend = mysql.query_db(query)
    mysql = connectToMySQL('private_wall_mysql')
    query = 'SELECT messages.message_id, messages.message, messages.sender_id, messages.receiver_id, users.first_name as sender FROM messages JOIN users ON users.user_id = messages.sender_id AND messages.receiver_id = %(id)s WHERE messages.receiver_id = %(id)s;'
    data = {'id': session['userid']}
    message = mysql.query_db(query, data)
    print(message)
    if 'userid' not in session:
        return redirect('/')
    return render_template('wall.html', user = user, friend = friend, message = message)

@app.route('/wall/send', methods=['POST'])
def send():
    mysql = connectToMySQL('private_wall_mysql')
    query = 'INSERT INTO messages (message, sender_id, receiver_id, created_at, updated_at) VALUES (%(mess)s, %(sender)s, %(receiver)s, NOW(), NOW());'
    data = {"mess": request.form["textbox"], "sender": session['userid'], "receiver": request.form["friend"]}
    new_message_id = mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/wall/destroy/<id>')
def delete(id):
    mysql = connectToMySQL('private_wall_mysql')
    query = 'DELETE FROM messages WHERE message_id = %(id)s;'
    data = {'id': id}
    delete_message = mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/logout')
def logout():
    if 'userid' in session:
        session.pop('userid')
    print("session cleared")
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)