#!/usr/bin/env python3.5

from flask import Flask, render_template, request, session, g, redirect, url_for, abort, flash


# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
EMAIL_ADDRESS = 'tutao1818@gmail.com'
PASSWORD = '123'

app = Flask(__name__)
app.config.from_object(__name__)

app.debug = True

@app.route("/")
def template_test():
    return render_template('template.html', my_string="Wheeeee!", my_list=["L1","L2"], title="Tao")


@app.route("/about")
def about():
    return render_template('laundromat.html',priceList=[10,20,30,40,50,60])

@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route("/order")
def order():
    return render_template('order.html')

#@app.route("/login")
#def login():
#    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['email'] != app.config['EMAIL_ADDRESS']:
            error = 'Invalid username'
    
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'

        else:
            #session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('about'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
