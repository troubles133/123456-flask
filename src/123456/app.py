from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

# --- НАСТРОЙКИ БАЗЫ ДАННЫХ ---
DB_NAME = 'sch688_vvedenie'
DB_USER = 'sch688_vvedenie'
DB_HOST = '185.114.247.43'
DB_PASS = 'Qwerty123'

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_lab'

def get_db_connection():
    try:
        cnx = mysql.connector.connect(
            host=DB_HOST, port=3306, database=DB_NAME,
            user=DB_USER, password=DB_PASS
        )
        return cnx
    except mysql.connector.Error as err:
        print(f"!!! Ошибка подключения к БД: {err}")
        return None

@app.route("/")
def reg():
    return render_template('reg.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/ajax/registr", methods=['POST'])
def user_registration():
    cnx = None
    cur = None
    try:
        req = request.get_json()
        hashed_password = generate_password_hash(req['password'])
        
        cnx = get_db_connection()
        if not cnx: return jsonify({'code': 500, 'error': 'Нет связи с БД'})
        
        cur = cnx.cursor()
        
        # Проверки на занятость
        cur.execute("SELECT id FROM users WHERE username = %s", (req['name'],))
        if cur.fetchone(): return jsonify({'code': 400, 'error': 'Это имя уже занято'})
        
        cur.execute("SELECT id FROM users WHERE email = %s", (req['email'],))
        if cur.fetchone(): return jsonify({'code': 400, 'error': 'Этот email уже зарегистрирован'})
        
# Берем имя и фамилию из запроса, который прислал JavaScript
        first_name = req.get('first_name', 'Неизвестно')
        last_name = req.get('last_name', 'Неизвестно')

        st = (req['name'], req['email'], hashed_password, first_name, last_name, 1000.00)
        cur.execute("""
        INSERT INTO users(username, email, password_hash, first_name, last_name, balance) 
        VALUES(%s, %s, %s, %s, %s, %s)
        """, st)
        
        cnx.commit()
        return jsonify({'code': 200, 'message': 'Регистрация успешна'})
    except Exception as e:
        print(f"Ошибка рег: {e}")
        return jsonify({'code': 500, 'error': str(e)})
    finally:
        if cur: cur.close()
        if cnx and cnx.is_connected(): cnx.close()

@app.route("/ajax/login", methods=['POST'])
def user_login():
    cnx = None
    cursor = None
    try:
        req = request.get_json()
        email = req['email'].strip().lower()
        password = req['password']
        
        cnx = get_db_connection()
        if not cnx: return jsonify({'code': 500, 'error': 'Нет связи с БД'})
        
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email, password_hash FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            return jsonify({'code': 200, 'username': user['username'], 'user_id': user['id']})
        else:
            return jsonify({'code': 401, 'error': 'Неверный email или пароль'})
    except Exception as e:
        return jsonify({'code': 500, 'error': 'Ошибка сервера'})
    finally:
        if cursor: cursor.close()
        if cnx and cnx.is_connected(): cnx.close()

@app.route("/lk")
def lk():
    if 'user_id' not in session:
        return "Вы не авторизованы. <a href='/login'>Войти</a>", 401
    
    cnx = get_db_connection()
    if not cnx: return "Ошибка БД", 500
        
    try:
        cursor = cnx.cursor(dictionary=True)
        # Теперь запрашиваем все колонки
        cursor.execute("SELECT username, first_name, last_name, balance FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        return render_template('lk.html', user=user)
    except Exception as e:
        return f"Ошибка при загрузке данных: {e}"
    finally:
        cursor.close()
        cnx.close()

@app.route("/ajax/transactions", methods=['POST'])
def transactions():
    if 'user_id' not in session: return jsonify({'error': 'Не авторизован'}), 401
    return jsonify({'message': 'Функция транзакций в разработке!', 'code': 200})

@app.route("/ajax/ai_request", methods=['POST'])
def ai_request():
    if 'user_id' not in session: return jsonify({'error': 'Не авторизован'}), 401
    return jsonify({'message': 'Привет! Это заглушка вместо нейросети.', 'code': 200})

@app.route("/dashboard")
def dashboard():
    return "<h1>Вы вошли!</h1><a href='/lk'>Перейти в личный кабинет</a>"

if __name__ == '__main__':
    app.run(debug=True)