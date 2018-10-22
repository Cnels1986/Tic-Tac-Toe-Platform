from flask import Flask, render_template, request, jsonify, make_response, json, session, flash
from pusher import pusher
from flaskext.mysql import MySQL

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
        password = request.form["password"]
        name = request.form["name"]

        # Queries database to see if the username already exists, they must be unique
        cursor.execute("SELECT * FROM Users WHERE userName = '{}'".format(username))
        user = cursor.fetchone();

        # user name does not exist within the database, will now add the information to the Users table
        if user == None:
            # adds new user to Users table
            cursor.execute("INSERT INTO Users(userName, password) VALUES('{}','{}')".format(username, password))
            conn.commit()

            userID = cursor.execute("SELECT id FROM Users WHERE userName = '{}'".format(username))

            cursor.execute("INSERT INTO Stats(user_id, name, wins, losses, winStreak, lossStreak) VALUES('{}','{}','{}','{}','{}','{}')".format(userID, name, 0, 0, 0, 0))
            conn.commit()
            # print(test)
            # cursor.execute("DELETE FROM Users WHERE userName = '{}'".format(username))
            # conn.commit()

        else:
            error = "Username already exists"

    return render_template('register.html', error=error)

#####################

# will be the first page to load, if not logged in this will display, nothing else
@app.route('/login')
def login():
    return render_template('login.html')

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
