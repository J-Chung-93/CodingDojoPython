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
    return render_template('home.html')

@app.route('/survey', methods=['POST'])
def survey():
    is_valid = True
    if len(request.form['user_name']) < 1:
        is_valid = False
        flash('Please enter a name')
    if is_valid == False:
        return redirect('/')
    if is_valid:
        session['survey'] = None
        mysql = connectToMySQL('dojo_survey')
        query = 'INSERT INTO users (name, location, language, comment, created_at, updated_at) VALUES (%(name)s, %(dojo)s, %(lang)s, %(comment)s, NOW(), NOW());'
        data = {"name": request.form["user_name"], "dojo": request.form["dojo_location"], "lang": request.form["fav_lang"], "comment": request.form["comment"]}
        new_user_id = mysql.query_db(query, data)
        session['survey'] = new_user_id
    return redirect('/result')

@app.route('/result')
def result():
    mysql = connectToMySQL('dojo_survey')
    query = 'SELECT * FROM users WHERE id = '+ str(session['survey'])+';'
    survey_result = mysql.query_db(query)
    return render_template('result.html', survey = survey_result)


if __name__=='__main__':
    app.run(debug=True)