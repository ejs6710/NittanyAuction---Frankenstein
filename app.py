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

app.secret_key = hash_password("12314214151241")
@app.route('/')
def index():
	return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		session['email'] = request.form['email']
		session['password'] =  request.form['password']

		connection = connect()
		cursor = connection.execute("SELECT * FROM Users WHERE email = ? AND password = ?", (session.get('email'), hash_password(session.get('password'))))
		user = cursor.fetchone()
		connection.close()

		if user:
			connection = connect()

			if connection.execute("SELECT * FROM Helpdesk WHERE email = ?", (session.get('email'),)).fetchone():
				session['role'] = 'Helpdesk'
				connection.close()
				return render_template('UserProfile.html', email=session.get('email'), role =session.get('role'))

			if connection.execute("SELECT * FROM Bidders WHERE email = ?", (session.get('email'),)).fetchone():
				session['role'] = 'Bidders'
				connection.close()
				return render_template('UserProfile.html', email=session.get('email'), role =session.get('role'))

			if connection.execute("SELECT * FROM Sellers WHERE email = ?", (session.get('email'),)).fetchone():
				session['role'] = 'Sellers'
				connection.close()
				return render_template('UserProfile.html', email=session.get('email'), role =session.get('role'))

			if connection.execute("SELECT * FROM Users WHERE email = ?", (session.get('email'),)).fetchone():
				connection.close()
				return render_template('users.html', email=session.get('email'))
			
			connection.close()
			error = "Unexpected error"

		else:
			error = "Invalid email or password"
	return render_template('login.html', error=error)

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
 
@app.route(rule="/UserProfile", methods=["GET", "POST"])
def user_profile(): #Reroutes to UserProfile
	error = None
	return render_template('UserProfile.html', email=session.get('email'), role = session.get('role'))

@app.route(rule='/Home', methods=['GET', 'POST'])
def home(): #Reroutes to home page
	error = None
	return render_template('Home.html', error=error)

@app.route(rule='/Personal_Information', methods=['GET', 'POST'])
def personal_information(): #Reroutes to personal information update page
	error = None
	return render_template('Personal_Information.html', error=error)

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
