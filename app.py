from flask import Flask, render_template, request, jsonify, make_response, json, session
from pusher import pusher
from flaskext.mysql import MySQL

app = Flask(__name__)

pusher = pusher_client = pusher.Pusher(
    app_id = "625212",
    key = "3e87945a40da57312dea",
    secret = "a4422b546645ab786621",
    cluster = "us2",
    ssl=True
)

name = ''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

# will be the first page to load, if not logged in this will display, nothing else
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/play')
def play():
    global name
    name = request.args.get('username')
    return render_template('play.html')

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

name = ''
