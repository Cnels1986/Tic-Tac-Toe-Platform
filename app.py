from flask import Flask, render_template, request, jsonify, make_response, json, session, flash
from pusher import pusher
from flaskext.mysql import MySQL
from passlib.hash import sha256_crypt

app = Flask(__name__)
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

#####################

@app.route('/')
def index():
    return render_template('index.html')

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
        cursor.execute("SELECT * FROM Users WHERE userName = '{}'".format(username))
        user = cursor.fetchone();

        # user name does not exist within the database, will now add the information to the Users table
        if user == None:
            # adds new user to Users table
            cursor.execute("INSERT INTO Users(userName, password) VALUES('{}','{}')".format(username, password))
            conn.commit()

            cursor.execute("SELECT * FROM Users WHERE userName = '{}'".format(username))
            userID = cursor.fetchone();

            cursor.execute("INSERT INTO Stats(user_id, name, wins, losses, winStreak, lossStreak) VALUES('{}','{}','{}','{}','{}','{}')".format(userID[0], name, 0, 0, 0, 0))
            conn.commit()
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

        cursor.execute("SELECT * FROM Users WHERE userName = '{}'".format(username))
        # retrieves hashed password from the Users table
        user = cursor.fetchone();

        # user name does not exist within the Users table
        if user == None:
            errorName = "Username does not exist"
        else:
            if sha256_crypt.verify(request.form["password"], user[2]):
                print("Passwords match")
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

name = ''
