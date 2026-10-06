from flask import Flask, render_template, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
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

@app.route("/ajax/registr", methods=['POST'])
def user_registration():
    cnx = None
    try:
        req = request.get_json()
        
        print(f"Получен пароль: {req['password']}")  
        

        hashed_password = generate_password_hash(req['password'])
        
        print(f"Хэш: {hashed_password}")  
        

        if 'script' in hashed_password:
            return jsonify({'code': 500, 'error': 'Ошибка хэширования'})
        
        cnx = mysql.connector.connect(
            host=DB_HOST,
            port=3306,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS)
        
        cur = cnx.cursor()
        
        cur.execute("SELECT id FROM users WHERE username = %s", (req['name'],))
        if cur.fetchone():
            return jsonify({'code': 400, 'error': 'Это имя уже занято'})
        
        cur.execute("SELECT id FROM users WHERE email = %s", (req['email'],))
        if cur.fetchone():
            return jsonify({'code': 400, 'error': 'Этот email уже зарегистрирован'})
        
        st = (req['name'], req['email'], hashed_password)
        cur.execute("INSERT INTO users(username, email, password_hash) VALUES(%s, %s, %s)", st)
        
        cnx.commit()
        row = cur.lastrowid
        
        return jsonify({'id': row, 'code': 200, 'message': 'Регистрация успешна'})
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({'code': 500, 'error': str(e)})
    finally:
        if cnx and cnx.is_connected():
            cnx.close()

@app.route("/ajax/login", methods=['POST'])
def user_login():
    cnx = None
    try:
        req = request.get_json()
        
        if not req or not all(k in req for k in ('email', 'password')):
            return jsonify({'code': 400, 'error': 'Заполните все поля'})
        
        email = req['email'].strip().lower()
        password = req['password']
        
        cnx = mysql.connector.connect(
            host=DB_HOST,
            port=3306,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS)
        
        cursor = cnx.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT id, username, email, password_hash FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        
        if user:
           
            is_valid = check_password_hash(user['password_hash'], password)
            if is_valid:
                return jsonify({
                    'code': 200,
                    'username': user['username'],
                    'user_id': user['id']
                })
            else:
                return jsonify({'code': 401, 'error': 'Неверный пароль'})
        else:
            return jsonify({'code': 401, 'error': 'Пользователь не найден'})
        
    except Exception as e:
        print(f"Ошибка входа: {e}")
        return jsonify({'code': 500, 'error': 'Ошибка сервера'})
    finally:
        if cnx and cnx.is_connected():
            cnx.close()

@app.route("/dashboard")
def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Успешный вход</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; }
            .success { color: green; font-size: 24px; }
            a { color: #007bff; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="success">✅ Вы успешно вошли в систему!</div>
        <a href="/">Вернуться на главную</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)