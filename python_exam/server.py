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
    mysql = connectToMySQL('python_exam')
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
        is_valid = False
        flash('Invalid email address')
    if len(request.form['pw']) < 8:
        is_valid = False
        flash('Password must be at least 8 characters')
    if request.form['pw'] != request.form['confirm_pw']:
        is_valid = False
        flash('Passwords do not match')
        return redirect('/home')
    if is_valid == False:
        return redirect('/home')
    pw_hash = bcrypt.generate_password_hash(request.form['pw'])
    if is_valid:
        mysql = connectToMySQL('python_exam')
        query = 'INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(password_hash)s, NOW(), NOW());'
        data = {'fn': request.form['fname'], 'ln': request.form['lname'], 'em': request.form['user_email'], 'password_hash': pw_hash}
        new_user_id = mysql.query_db(query, data)
    return redirect('/home/register_success')

@app.route('/home/register_success')
def register_success():
    flash('You have successfully registered')
    return redirect('/home')

@app.route('/home/login', methods=['POST'])
def login():
    mysql = connectToMySQL('python_exam')
    query = 'SELECT * FROM users WHERE email = %(em)s;'
    data = {'em': request.form['user_email']}
    result = mysql.query_db(query, data)
    if result:
        if bcrypt.check_password_hash(result[0]['password'], request.form['pw']):
            session['user_id'] = result[0]['id']
            return redirect('/wishes')
    flash('You could not be logged in')
    return redirect('/home')

@app.route('/wishes')
def wish():
    mysql = connectToMySQL('python_exam')
    query = 'SELECT wishes.id, wishes.wish, wishes.description, wishes.created_at, wishes.updated_at, wishes.granted, users.first_name as wisher FROM wishes JOIN users ON users.id = wishes.users_id WHERE granted = %(bool)s;'
    data = {'bool': 1}
    all_user = mysql.query_db(query, data)
    mysql = connectToMySQL('python_exam')
    query = 'SELECT * FROM users WHERE users.id = '+ str(session['user_id'])+';'
    user = mysql.query_db(query)
    mysql = connectToMySQL('python_exam')
    query = 'SELECT * FROM wishes JOIN users ON users.id = wishes.users_id WHERE users.id = %(id)s;'
    data = {'id': session['user_id']}
    wish = mysql.query_db(query, data)
    if 'user_id' not in session:
        return redirect('/')
    print(all_user)
    return render_template('wishes.html', user = user, all_wishes = wish, all_users = all_user)

@app.route('/wishes/<id>/granted')
def granted_wish(id):
    mysql = connectToMySQL('python_exam')
    query = 'UPDATE wishes SET updated_at = NOW(), granted = %(bool)s WHERE id = %(id)s;'
    data = {'id': id, 'bool': 1}
    grant = mysql.query_db(query, data)
    print(grant)
    return redirect('/wishes')

@app.route('/wishes/<id>/edit')
def edit_wishes(id):
    mysql = connectToMySQL('python_exam')
    query = 'SELECT * FROM users WHERE users.id = '+ str(session['user_id'])+';'
    user = mysql.query_db(query)
    mysql = connectToMySQL('python_exam')
    query = 'SELECT * FROM wishes WHERE id = %(id)s;'
    data = {'id': id}
    wish = mysql.query_db(query, data)
    return render_template('edit.html', user = user, all_wishes = wish)

@app.route('/wishes/<id>/edit/success', methods=['POST'])
def success_edit(id):
    is_valid = True
    if len(request.form['updated_item']) < 3:
        is_valid = False
        flash('A wish must consist of at least 3 characters!')
    if len(request.form['updated_message_box']) < 1:
        is_valid = False
        flash('A description must be provided!')
    if is_valid:
        mysql = connectToMySQL('python_exam')
        query = 'UPDATE wishes SET wish = %(wish)s, description = %(desc)s, updated_at = NOW() WHERE wishes.id = %(id)s;'
        data = {'id': id, 'wish': request.form['updated_item'], 'desc': request.form['updated_message_box']}
        updated_wish_id = mysql.query_db(query, data)
    if is_valid == False:
        return redirect('/wishes/<id>/edit')
    return redirect('/wishes/success')

@app.route('/wishes/new')
def new_wish():
    mysql = connectToMySQL('python_exam')
    query = 'SELECT * FROM users WHERE users.id = '+ str(session['user_id'])+';'
    user = mysql.query_db(query)
    return render_template('new_wish.html', user = user)

@app.route('/wishes/create', methods=['POST'])
def create_wish():
    is_valid = True
    if len(request.form['item']) < 3:
        is_valid = False
        flash('A wish must consist of at least 3 characters!')
    if len(request.form['message_box']) < 1:
        is_valid = False
        flash('A description must be provided!')
    if is_valid:
        mysql = connectToMySQL('python_exam')
        query = 'INSERT INTO wishes (wish, description, created_at, updated_at, users_id, granted) VALUES (%(wish)s, %(desc)s, NOW(), NOW(), %(id)s, %(bool)s);'
        data = {'wish': request.form['item'], 'desc': request.form['message_box'], 'id': session['user_id'], 'bool': 0}
        new_wish_id = mysql.query_db(query, data)
    if is_valid == False:
        return redirect('/wishes/new')
    return redirect('/wishes/success')

@app.route('/wishes/success')
def wish_success():
    flash('Wish updated!')
    return redirect('/wishes')

@app.route('/wishes/<id>/destroy')
def destroy_wishes(id):
    mysql = connectToMySQL('python_exam')
    query = 'DELETE FROM wishes WHERE id = %(id)s;'
    data = {"id": id}
    delete_wish = mysql.query_db(query, data)
    return redirect('/wishes')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    return redirect('/')

if __name__=='__main__':
    app.run(debug=True)