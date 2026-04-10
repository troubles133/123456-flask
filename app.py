from flask import*

import mysql.connector

DB_NAME = 'sch688_vvedenie'
DB_USER = 'sch688_vvedenie'
DB_HOST = '185.114.247.43'
DB_PASS = 'Qwerty123'



app = Flask(__name__)



@app.route("/")
def reg():
    return render_template('reg.html')

@app.route("/login")
def login():
    return render_template('login.html')
@app.route("/ajax/register", methods=['POST'])
def user_registration():
    cnx = mysql.connector.connect(
        host=DB_HOST,
        port=3306,
        user=DB_USER,
        password=DB_PASS)

    cur = cnx.cursor()
    req = request.get_json()
    st=(req['name'], req['email'],req['password'])
    cur.execute("INSERT INTO users(name,login,password)VALUES(%s, %s, %s)", st)
    cnx.commit()
    row = cur.lastrowid
    cnx.close()
    return jsonify(row)

app.run()