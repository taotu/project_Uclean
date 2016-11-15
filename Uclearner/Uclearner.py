#!/usr/bin/env python3.5
from time import sleep
import os
import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, render_template, request, session, g, redirect, url_for, abort, flash, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

# configuration
DATABASEURI = 'postgresql://postgres:allah@localhost/laundryapp'

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
  session.pop('logged_in', None)
  session.pop('user_id', None)
  session.clear()
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
  islogged = false
  for result in cursor:
    names.append(list(result))
    # can also be accessed using result[0]
  cursor.close()
  print (names)
  if 'logged_in' in session and session['logged_in']:
    islogged = True
  return render_template('layout.html', my_list=names, title="Welcome", logged=islogged)

@app.route('/store/profile/<string:laundry_id>')
def show_store_profile(laundry_id):
    print("In store profile")
    session['lid'] = laundry_id
    cursor = g.conn.execute("select l.name, a.street, a.city, a.state, a.zipcode, r.stars from laundromat l, address a, review r where l.lid=a.lid and l.lid = r.lid AND l.lid=%s",laundry_id)
    info = []
    reviews = []
    items =[]
    for result in cursor:
        info.append(list(result))  # can also be accessed using result[0]
    print (info)
    cursor.close()
    cursor = g.conn.execute("select c.email, r.reviews, r.stars from laundromat l, customer c, review r where c.cid=r.cid and l.lid = r.lid AND l.lid=%s",laundry_id)
    for result in cursor:
      reviews.append(list(result))  # can also be accessed using result[0]
    print (reviews)
    cursor.close()
    cursor = g.conn.execute("select item_type, price from item")
    for result in cursor:
      items.append(list(result))  # can also be accessed using result[0]
    session['item_type'] = items
    return render_template('laundromat.html', my_list=info, review=reviews, priceList=items, title="Store Profile")

@app.route('/user/profile', methods=['POST', 'GET'])
def show_user_profile():
    print("In user profile")
    print(session['user_id'])
    if 'logged_in' in session and session['logged_in']:
      cursor = g.conn.execute("select c.fname, c.lname, c.email, c.phone, a.street, a.apt, a.city, a.state, a.zipcode from customer c, address a where c.cid = a.cid and c.cid=%s", session['user_id'])
      user = []
      for result in cursor:
          user.append(list(result))  # can also be accessed using result[0]
      cursor.close()
      print(user)
      cursor = g.conn.execute("select o.order_id, o.total, o.status, o.date_created from order_table o where o.cid=%s", session['user_id'])
      order_history = []
      for result in cursor:
          order_history.append(list(result))  # can also be accessed using result[0]
      cursor.close()

      return render_template('userprofile.html', my_list=user, orders = order_history, title="User Profile")
    return render_template('login.html')

@app.route("/search", methods=['POST','GET'])
def searchresult():
  term = request.form['term']
  print ("request is " +term)

  #cur.execute("UPDATE Cars SET Price=%s WHERE Id=%s", (uPrice, uId))
  cursor = g.conn.execute("select l.lid, l.name, a.street, r.stars from laundromat l, address a, review r where l.lid=a.lid and l.lid = r.lid AND a.zipcode=%s",term)
  store_profile = []
  islogged = False
  for result in cursor:
    store_profile.append(list(result))
     # can also be accessed using result[0]
  cursor.close()

  print (store_profile)
  if 'logged_in' in session and session['logged_in']:
    islogged = True
  return render_template('layout.html', my_list=store_profile, title="Welcome", logged = islogged)

@app.route("/about")
def about():
#    return render_template('laundromat.html',priceList=[10,20,30,40,50,60])
#     return render_template('checkout.html')
      return render_template('about.html')

@app.route("/checkout", methods=['POST'])
def checkout():
  print ('In checkout')
  print(request.method)
  if 'logged_in' in session and session['logged_in']:
    if request.method == 'POST':
      a = -1
      b = -1
      c = -1
      totalsum = int(request.form['amount'])
      add1 = request.form['address-line1']
      add2 = request.form['address-line2']
      city = request.form['city'] 
      region = request.form['region'] 
      zipcode = request.form['postal-code'] 
      pickup = request.form.get('date-pick-up') 
      delivery = request.form.get('date-delivery')
      cnum = request.form['number'] 
      print(cnum)
      fname = request.form['fname']
      lname = request.form['lname']
      cvc = request.form['cvc']
      cursor = g.conn.execute("select MAX(order_id) FROM order_table")
      for i in cursor:
        a = i[0]
        a = a + 1
      cmd1 = 'INSERT INTO order_table VALUES ((:order_id), (:total), (:status), (:pickup_time), (:delivery_time), (:date_created), (:cid), (:lid))'
      g.conn.execute(text(cmd1), order_id=a, total = totalsum, status = 'Pickup', pickup_time=pickup, delivery_time=delivery, date_created=datetime.date.today(), cid=session['user_id'], lid=session['lid'])
      cursor.close()
      payment = []
      cursor = g.conn.execute("select cnumber from payment_info WHERE cnumber = %s", cnum)
      for result in cursor:
            payment.append(result[0])
      print (payment)
      if len(payment) == 0:
        cursor = g.conn.execute("select MAX(pid) FROM payment_info")
        for i in cursor:
          c = i[0]
          c = c + 1
        cmd2 = 'INSERT INTO payment_info VALUES ((:pid), (:ptype), (:cnumber), (:cvv), (:cid))'
        g.conn.execute(text(cmd2), pid=c, ptype = "", cnumber = cnum, cvv=cvc, cid=session['user_id'])
        cursor.close()
      return show_user_profile()
  return redirect(url_for('login'))

@app.route("/order", methods=['POST'])
def order():
  print ('In order')
  if 'logged_in' in session and session['logged_in']:
    if request.method == 'POST':
      print(session['user_id'])
      print ('user_id is after')
      cursor = g.conn.execute("select a.street, a.apt, a.city, a.state, a.zipcode, c.fname, c.lname, p.cnumber, p.cvv from customer c, payment_info p, address a where c.cid = a.cid and p.cid = c.cid and c.cid=%s", session['user_id'])
      payment_info = []
      for result in cursor:
         payment_info.append(list(result))  # can also be accessed using result[0]
      cursor.close()
      if len(payment_info) == 0:
        cursor = g.conn.execute("select a.street, a.apt, a.city, a.state, a.zipcode, c.fname, c.lname from customer c, address a where c.cid = a.cid and c.cid=%s", session['user_id'])
        payment_info = []
        for result in cursor:
          payment_info.append(list(result))  # can also be accessed using result[0]
      cursor.close()
      print (payment_info)
      order_total = request.form['totalsum']
      order_items = request.form.getlist("total")
      qty = request.form.getlist("qty")
      session['order_total'] = order_total
      session['order_items'] = order_total
      session['qty'] = qty
      session['payment_info'] = payment_info
      #return redirect(url_for('checkout')
      print ('before render')
      return render_template('checkout.html', my_list=payment_info, order_total=order_total)
  return redirect(url_for('login'))

@app.route("/signup", methods=['POST','GET'])
def signup():
    print("In signup")
    print (request.method)
    if request.method == 'POST':
        a = -1
        b = -1
        fname = str(request.form['firstname'])
        lname = str(request.form['lastname'])
        email = str(request.form['email'])
        password = str(request.form['password'])
        phone = str(request.form['phone'])
        street = str(request.form['address-1'])
        apt = str(request.form['apt'])
        city =str(request.form['city'])
        state = str(request.form['state'])
        zipcode = str(request.form['zipcode'])
        cursor = g.conn.execute("select MAX(cid) FROM customer")
        for i in cursor:
          a = i[0]
        a = a + 1

        cmd1 = 'INSERT INTO customer VALUES ((:cid), (:fname), (:lname), (:email), (:password), (:phone))'
        g.conn.execute(text(cmd1), cid=a, fname = fname, lname = lname, email=email, password=password, phone=phone)
        cursor.close()
        cursor = g.conn.execute("select MAX(addr_id) FROM address")
        for i in cursor:
          b = i[0]
        b = b + 1
        cmd2 = 'INSERT INTO address VALUES ((:addr_id), (:street), (:city), (:state), (:apt), (:zipcode), (:cid))'
        g.conn.execute(text(cmd2), addr_id=b, street = street, city = city, state=state, apt=apt, zipcode=zipcode, cid=a)
        #print(stmt)
        session['logged_in'] = True
        session['user_id'] = a
        # print(session['user_id'])
        #return show_user_profile()
        return login()
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    print ('In Logged in')
    if 'logged_in' in session and session['logged_in']:
      return show_user_profile()
    if request.method == 'POST':
        cursor = g.conn.execute("SELECT cid, email, password FROM customer WHERE email=%s", request.form['email'])
        info = []
        for result in cursor:
            info.append(result['cid'])
            info.append(result['email'])  # can also be accessed using result[0]
            info.append(result['password'])
        print (info)
        if len(info) == 0:
          error = 'Email not registered'
          return render_template('login.html', error=error)
        if request.method == 'POST':
            if request.form['email'] != info[1]:
                error = 'Invalid username'
        
            elif request.form['password'] != info[2]:
                error = 'Invalid password'

            else:
                session['logged_in'] = True
                session['user_id'] = info[0]
                islogged = True
                flash('You were logged in')
                return show_user_profile()
                #return redirect(url_for('show_store_profile'))
    return render_template('login.html', error=error)

@app.route('/test')
def test():
  cursor = g.conn.execute("select COUNT(*) FROM customer")
  print('before')
  for i in cursor:
    a = i
  print(a[0])


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('template_test'))

# set the secret key.  keep this really secret:
if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
