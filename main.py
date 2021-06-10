from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysql'
app.config['MYSQL_DB'] = 'pythonlogin'

# Intialize MySQL
mysql = MySQL(app)

# http://127.0.0.1:7000/- this will be the login page
@app.route('/', methods=['GET', 'POST'])
def login():
    # There will be a output message
    msg = ''
    #Will check if the user exits or not 
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch a record and return it
        account = cursor.fetchone()
        # If account exists in the out database
        if account:
            # Create session data, so we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # You will be directed to home page
            return redirect(url_for('home'))
        else:
            # If the account doesnt exist or username/password are incorrect
            msg = 'Incorrect username/password!'
    # Will show the login form with message if possible
    return render_template('index.html', msg=msg)

# http://127.0.0.1:7000/ - this is the login page, which will appear once you logout
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out and place the none value in the session
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # You will be directed to the login page
   return redirect(url_for('login'))


# http://127.0.0.1:7000/register - this will be the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    # There will be a output message
    msg = ''
    #Will check if the user exits or not
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # If doesnt account doesnt exist in the database and the form data is valid,  you can now insert details into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Will show the login form with message if possible
    return render_template('register.html', msg=msg)

#http://127.0.0.1:7000/home - this will be the home page, for loggedin users
@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # If user is loggedin show then show the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

#http://127.0.0.1:7000/profile - profile page, it has you details
@app.route('/profile')
def profile():
    # will check if user is loggedin
    if 'loggedin' in session:
        # It will get all the account info for the databse and will be displayed on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True,port=7000)