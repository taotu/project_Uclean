#!/usr/bin/env python3.5

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, render_template, request, session, g, redirect, url_for, abort, flash, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

# configuration
DATABASEURI = 'postgresql://postgres:zes8lami2LH@localhost/laundryapp'
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
EMAIL_ADDRESS = 'tutao1818@gmail.com'
PASSWORD = '123'


engine = create_engine(DATABASEURI)



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass




@app.route("/")
def template_test():
  #cursor = g.conn.execute("SELECT name FROM laundromat")
  cursor = g.conn.execute("select l.lid, l.name, a.street, r.stars from laundromat l, address a, review r where l.lid=a.lid and l.lid = r.lid")
  names = []
  sublist = []
  for result in cursor:
    names.append(list(result))
    # can also be accessed using result[0]
  cursor.close()
  print (names)
  return render_template('layout.html', my_list=names, title="Welcome")

@app.route('/store/profile/<string:laundry_id>')
def show_store_profile(laundry_id):
    print("In store profile")
    cursor = g.conn.execute("select l.name, a.street, r.stars, r.reviews from laundromat l, address a, review r where l.lid=a.lid and l.lid = r.lid AND l.lid=%s",laundry_id)
    info = []
    for result in cursor:
        info.append(result['name'])  # can also be accessed using result[0]
    print (info)
    cursor.close()


@app.route('/user/profile/<string:user_id>')
def show_user_profile(user_id):
    print("In user profile")
    cursor = g.conn.execute("select fname, lname, email from customer where cid=%s", user_id)
    user = []
    for result in cursor:
        user.append(result['fname'])  # can also be accessed using result[0]
    print (user)
    cursor.close()


@app.route("/search", methods=['POST','GET'])
def searchresult():
  term = request.form['term']
  print ("request is" +term)

  #cur.execute("UPDATE Cars SET Price=%s WHERE Id=%s", (uPrice, uId))
  cursor = g.conn.execute("select l.lid, l.name, a.street, r.stars from laundromat l, address a, review r where l.lid=a.lid and l.lid = r.lid AND a.zipcode=%s",term)
  store_profile = []
  dict = {}
  for result in cursor:
    store_profile.append(result['name']) 
    store_profile.append(result['street'])
    store_profile.append(result['stars'])
    store_profile.append(result['lid']) 
     # can also be accessed using result[0]
  cursor.close()
  

  print (store_profile)
  return render_template('layout.html', my_list=store_profile, title="Welcome")

@app.route("/about")
def about():
    return render_template('laundromat.html',priceList=[10,20,30,40,50,60])

@app.route("/signup", methods=['POST','GET'])
def signup():
    print("In signup")
    print (request.method)
    if request.method == 'POST':
        print("hola")
        fname = request.form['firstname']
        print ('hoop')
        lname = request.form['lastname']
        print ('hola again')
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        street = request.form['address-line1']
        city = request.form['city']
        state = request.form['region']
        zipcode = request.form['postal-code']
        print (fname)
        #cmd = 'INSERT INTO laundryapp(customer) VALUES (:fname), (:lname), (:email), (:phone), (:password)';
        #stmt = g.conn.execute(text(cmd), fname = fname, lname = lname, email=email, phone=phone, pasword=pasword);
        return redirect('/')
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
    print ('In Logged in')
    if request.method == 'POST':
        cursor = g.conn.execute("SELECT email, password FROM customer WHERE email=%s", request.form['email'])
        info = []
        for result in cursor:
            info.append(result['email'])  # can also be accessed using result[0]
            info.append(result['password'])
        print (info)
        if request.method == 'POST':
            if request.form['email'] != info[0]:
                error = 'Invalid username'
        
            elif request.form['password'] != info[1]:
                error = 'Invalid password'

            else:
                #session['logged_in'] = True
                #flash('You were logged in')
                print('yey')
                return redirect(url_for('show_user_profile'))
    return render_template('login.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)
