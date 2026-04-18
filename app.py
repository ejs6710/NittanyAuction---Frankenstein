import email
import os

from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import hashlib
import random
import string
app = Flask(__name__)

HOST = 'http://127.0.0.1:5000/'
DB_NAME = 'identifier.sqlite'

def connect():
  return sqlite3.connect(DB_NAME)

def hash_password(password):
  return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('email'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

app.secret_key = hash_password("12314214151241")
@app.route('/')
def index():
	return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		session['email'] = request.form['email']
		session['password'] = request.form['password']
 
		connection = connect()
		cursor = connection.execute("SELECT * FROM Users WHERE email = ? AND password = ?", (session.get('email'), hash_password(session.get('password'))))
		user = cursor.fetchone()
		connection.close()
 
		if user:
			connection = connect()
			email = session.get('email')
 
			if connection.execute("SELECT * FROM HelpDesk WHERE email = ?", (email,)).fetchone():
				session['role'] = 'Helpdesk'
			elif connection.execute("SELECT * FROM Sellers WHERE email = ?", (email,)).fetchone():
				session['role'] = 'Sellers'
			elif connection.execute("SELECT * FROM Bidders WHERE email = ?", (email,)).fetchone():
				session['role'] = 'Bidders'
			else:
				session['role'] = None
				connection.close()
				return render_template('users.html', email=email)
 
			connection.close()
			return redirect(url_for('user_profile'))
 
		else:
			error = "Invalid email or password"
	return render_template('login.html', error=error)
 

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register(): # user registration
    error  = None
    if request.method  == 'POST':

        email =  request.form['email'].strip()
        password = request.form['password']
        confirm =  request.form['confirm_password']
 
        if password != confirm:
            error = "Passwords do not match."
            return render_template('register.html', error=error)

		
        connection = connect()
		# check if input email already exist in User table
        existing  = connection.execute(
            "SELECT 1 FROM Users WHERE email = ?", (email,)
        ).fetchone()

		# email registered, reject registration
        if existing:
            connection.close()
            error  = f"{email} account already exists."
            return render_template('register.html', error=error)

		# email is unique, accept registration with hashed password
        connection.execute(
            "INSERT INTO Users (email, password) VALUES (?, ?)",
            (email, hash_password(password))
        )
        connection.commit()
        connection.close()


        session['email'] = email
        session['role'] =  None # No role yet

        return render_template('UserProfile.html', email=session.get('email'), role = session.get(None))
 
    return render_template('register.html', error=error)

@app.route(rule='/Home', methods=['GET', 'POST'])
def home(): #Reroutes to home page
	error = None
	return render_template('Home.html', error=error)
 
@app.route('/UserProfile', methods=['GET'])
@login_required
def user_profile():
    email = session.get('email')
    role  = session.get('role')
 
    profile_data = {}
 
    connection = connect()
 
    if role == 'Bidders':
        row = connection.execute(
            """SELECT b.first_name, b.last_name, b.age, b.major,
                      a.street_num, a.street_name, a.zipcode
               FROM Bidders b
               LEFT JOIN Address a ON b.home_address_id = a.address_id
               WHERE b.email = ?""",
            (email,)
        ).fetchone()
 
        cards = connection.execute(
            """SELECT credit_card_num, card_type, expire_month, expire_year
               FROM Credit_Cards WHERE owner_email = ?""",
            (email,)
        ).fetchall()
 
        if row:
            profile_data = {
                'first_name'  : row[0],
                'last_name'   : row[1],
                'age'         : row[2],
                'major'       : row[3],
                'street_num'  : row[4],
                'street_name' : row[5],
                'zipcode'     : row[6],
                'credit_cards': [
                    {
                        'number'      : c[0],
                        'type'        : c[1],
                        'expire_month': c[2],
                        'expire_year' : c[3],
                    }
                    for c in cards
                ],
            }
 
    elif role == 'Sellers':
        # Sellers are also bidders — fetch personal info from Bidders + Address
        bidder_row = connection.execute(
            """SELECT b.first_name, b.last_name, b.age, b.major,
                      a.street_num, a.street_name, a.zipcode
               FROM Bidders b
               LEFT JOIN Address a ON b.home_address_id = a.address_id
               WHERE b.email = ?""",
            (email,)
        ).fetchone()
 
        cards = connection.execute(
            """SELECT credit_card_num, card_type, expire_month, expire_year
               FROM Credit_Cards WHERE owner_email = ?""",
            (email,)
        ).fetchall()
 
        seller_row = connection.execute(
            """SELECT bank_routing_number, bank_account_number, balance
               FROM Sellers WHERE email = ?""",
            (email,)
        ).fetchone()
 
        vendor = connection.execute(
            """SELECT business_name, customer_service_phone_number
               FROM Local_Vendors WHERE email = ?""",
            (email,)
        ).fetchone()
 
        if bidder_row or seller_row:
            profile_data = {
                # Bidder / personal fields
                'first_name'  : bidder_row[0] if bidder_row else None,
                'last_name'   : bidder_row[1] if bidder_row else None,
                'age'         : bidder_row[2] if bidder_row else None,
                'major'       : bidder_row[3] if bidder_row else None,
                'street_num'  : bidder_row[4] if bidder_row else None,
                'street_name' : bidder_row[5] if bidder_row else None,
                'zipcode'     : bidder_row[6] if bidder_row else None,
                'credit_cards': [
                    {'number': c[0], 'type': c[1],
                     'expire_month': c[2], 'expire_year': c[3]}
                    for c in cards
                ],
                # Seller fields
                'bank_routing_number' : seller_row[0] if seller_row else None,
                'bank_account_number' : seller_row[1] if seller_row else None,
                'balance'             : seller_row[2] if seller_row else None,
                'vendor': {
                    'business_name': vendor[0],
                    'phone'        : vendor[1],
                } if vendor else None,
            }
 
    elif role == 'Helpdesk':
        row = connection.execute(
            """SELECT b.first_name, b.last_name, b.age, b.major,
                      a.street_num, a.street_name, a.zipcode
               FROM Bidders b
               LEFT JOIN Address a ON b.home_address_id = a.address_id
               WHERE b.email = ?""",
            (email,)
        ).fetchone()
 
        cards = connection.execute(
            """SELECT credit_card_num, card_type, expire_month, expire_year
               FROM Credit_Cards WHERE owner_email = ?""",
            (email,)
        ).fetchall()
 
        if row:
            profile_data = {
                'first_name'  : row[0],
                'last_name'   : row[1],
                'age'         : row[2],
                'major'       : row[3],
                'street_num'  : row[4],
                'street_name' : row[5],
                'zipcode'     : row[6],
                'credit_cards': [
                    {'number': c[0], 'type': c[1],
                     'expire_month': c[2], 'expire_year': c[3]}
                    for c in cards
                ],
            }
 
 
    connection.close()
    return render_template('UserProfile.html', email=email, role=role, profile_data=profile_data)
 
@app.route('/helpdesk')
@login_required
def helpdesk_dashboard():
    if session.get('role') != 'Helpdesk':
        return redirect(url_for('user_profile'))
    email = session.get('email')
    connection = connect()
    row = connection.execute(
        "SELECT position FROM HelpDesk WHERE email = ?", (email,)
    ).fetchone()
    connection.close()
    position = row[0] if row else 'Unknown'
    return render_template('helpdesk.html', email=email, position=position)

@app.route(rule='/Update_Info', methods=['GET', 'POST'])
def Update_Information(): #Updates information for users not part of any role
	#Automatically adds them to bidders table
	error = None
	connection = connect()
	if request.method == 'POST':
		#Retrieves all values
		major = request.form['Major']
		age = request.form['Age']
		lastname = request.form['Last_Name']
		firstname = request.form['First_Name']
		zipcode = request.form['Zipcode']
		streetnum = request.form['Street_Number']
		streetname = request.form['Street_Name']
		address_id = "" #Generates a random 40 character address id
		for i in range(0, 20):
			address_id += str(random.randint(0, 9))
			address_id += random.choice(string.ascii_letters)
		#Inserts the address and user into the tables
		connection.execute("INSERT INTO Address (address_id, zipcode, street_num, street_name) VALUES (?,?,?,?)", (address_id, zipcode, streetnum, streetname))
		connection.execute("INSERT INTO Bidders (email, first_name, last_name, age, home_address_id, major) VALUES (?,?,?,?,?,?)", (session.get("email"), firstname, lastname, age, address_id, major))
		connection.commit()
	connection.close()
	#Reroutes to the UserProfile table
	return render_template('UserProfile.html', email=session.get('email'), role = session.get('Bidder'))


if __name__ == "__main__":
	app.run(debug=True, port=5000)
