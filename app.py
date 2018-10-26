from flask import Flask, render_template, request, jsonify, make_response, json, session, flash, redirect, url_for
from pusher import pusher
from flaskext.mysql import MySQL
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
mysql = MySQL()

pusher = pusher_client = pusher.Pusher(
    app_id = "625212",
    key = "3e87945a40da57312dea",
    secret = "a4422b546645ab786621",
    cluster = "us2",
    ssl=True
)

name = ''

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'appdb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

# function checks the session loggin in status to see if user is logged in, if not it redirects them to the login page
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            # flash("This is a test...")
            return redirect(url_for('login'))
    return wrap

#####################

@app.route('/')
@login_required
def index():
    return render_template('index.html')

#####################

@app.route('/dashboard')
@login_required
def dash():
    return render_template('dashboard.html')

#####################

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == "POST":
        # retrieves input from the register form
        username = request.form["userName"]
        password = sha256_crypt.encrypt(str(request.form["password"]))
        name = request.form["name"]

        # Queries database to see if the username already exists, they must be unique
        cursor.execute("SELECT * FROM Users WHERE userName = (%s)", thwart(username))
        user = cursor.fetchone();

        # user name does not exist within the database, will now add the information to the Users table
        if user == None:
            # adds new user to Users table
            cursor.execute("INSERT INTO Users(userName, password) VALUES(%s, %s)", (thwart(username), thwart(password)))
            cursor.execute("SELECT * FROM Users WHERE userName = '{}'".format(username))
            userID = cursor.fetchone();
            cursor.execute("INSERT INTO Stats(user_id, name, wins, losses, winStreak, lossStreak) VALUES(%s, %s, 0,0,0,0)", (int(userID[0]), thwart(name)))
            conn.commit()
            conn.close()
            # sets the session so user is now logged in to the app
            session['logged_in'] = True
            session['username'] = username
            flash("Thank you for registering")
            return redirect(url_for('dash'))
        else:
            error = "Username already exists"

    return render_template('register.html', error=error)

#####################

# will be the first page to load, if not logged in this will display, nothing else
@app.route('/login', methods=['GET', 'POST'])
def login():
    errorName = None
    errorPass = None
    if request.method == "POST":
        # retrieves input from the login form
        username = request.form["userName"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM Users WHERE userName = (%s)", thwart(username))
        # retrieves hashed password from the Users table
        user = cursor.fetchone();

        # user name does not exist within the Users table
        if user == None:
            errorName = "Username does not exist"
        else:
            if sha256_crypt.verify(request.form["password"], user[2]):
                print("Passwords match")
                session['logged_in'] = True
                session['username'] = username
                flash("You are now logged in")
                return redirect(url_for('dash'))
            else:
                errorPass = "Incorrect password"

    return render_template('login.html', errorName=errorName, errorPass=errorPass)

#####################

@app.route('/play')
def play():
    global name
    name = request.args.get('username')
    return render_template('play.html')

#####################

@app.route('/pusher/auth', methods=['POST'])
def pusher_authentication():
    auth = pusher.authenticate(
        channel=request.form['channel_name'],
        socket_id=request.form['socket_id'],
        custom_data={
            u'user_id': name,
            u'user_info': {
                u'role': u'player'
            }
        }
    )
    return json.dumps(auth)

#####################

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("You are now logged out")
    return redirect(url_for('login'))

#####################


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

name = ''
