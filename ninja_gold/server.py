from flask import Flask, render_template, request, redirect, session
import random
app=Flask(__name__)
app.secret_key='spiderman'

@app.route('/')
def index():
    if 'gold' not in session:
        session['gold'] = 0
    if 'log' not in session:
        session['log'] = []
    if 'counter' not in session:
        session['counter'] = 0
    if 'game_over' not in session:
        session['game_over'] = 'False'
    if session['counter'] > 14:
        session['game_over'] = 'True'
    print(session['game_over'])
    return render_template('index.html', earning=session['gold'], log=session['log'], turn=session['counter'], game_over=session['game_over'])

@app.route('/process', methods=['POST'])
def process():
    print(request.form)
    earned = 0
    if request.form['form'] == 'Farm':
        earned=random.randint(10,20)
        session['gold'] += earned
    if request.form['form'] == 'Cave':
        earned=random.randint(5,10)
        session['gold'] += earned
    if request.form['form'] == 'House':
        earned=random.randint(2,5)
        session['gold'] += earned
    if request.form['form'] == 'Casino':
        earned=random.randint(-50,50)
        session['gold'] += earned
    if earned < 0:
            session['log'].append ('Lost ' + str(abs(earned)) + ' in the ' + request.form['form'])
    else:
        session['log'].append ('Earned ' + str(earned) + ' in the ' + request.form['form'])
    session['counter'] += 1
    return redirect('/')

@app.route('/reset')
def reset():
    session.clear()
    return redirect('/')









if __name__=='__main__':
    app.run(debug=True)