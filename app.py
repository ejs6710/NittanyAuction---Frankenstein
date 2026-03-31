from flask import Flask, render_template, request
import sqlite3
import hashlib

app = Flask(__name__)

HOST = 'http://127.0.0.1:5000/'
DB_NAME = 'database.db'

def connect():
  return sqlite3.connect(DB_NAME)

def hash_password(password):
  return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
	return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		email, password = request.form['email'], request.form['password']

		connection = connect()
		cursor = connection.execute("SELECT * FROM Users WHERE email = ? AND password = ?", (email, hash_password(password)))
		user = cursor.fetchone()
		connection.close()

		if user:
			connection = connect()

			if connection.execute("SELECT * FROM Helpdesk WHERE email = ?", (email,)).fetchone():
				connection.close()
				return render_template('helpdesk.html', email=email)

			if connection.execute("SELECT * FROM Bidders WHERE email = ?", (email,)).fetchone():
				connection.close()
				return render_template('bidders.html', email=email)

			if connection.execute("SELECT * FROM Sellers WHERE email = ?", (email,)).fetchone():
				connection.close()
				return render_template('sellers.html', email=email)

			if connection.execute("SELECT * FROM Users WHERE email = ?", (email,)).fetchone():
				connection.close()
				return render_template('users.html', email=email)
			
			connection.close()
			error = "Unexpected error"

		else:
			error = "Invalid email or password"
	return render_template('login.html', error=error)

if __name__ == "__main__":
	app.run(debug=True, port=5000)
