from flask import Flask, render_template, request, jsonify, session, redirect
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os

try:
    from llama_cpp import Llama
    print("Загрузка модели... Пожалуйста, подождите.")
    llm = Llama.from_pretrained(
        repo_id="bartowski/Qwen2.5-0.5B-Instruct-GGUF",
        filename="Qwen2.5-0.5B-Instruct-Q4_K_M.gguf",
        n_ctx=2048,
        verbose=False
    )
    print("✅ Модель успешно загружена.")
except ImportError:
    print("❌ Ошибка: библиотека llama-cpp-python не установлена.")
    llm = None

app = Flask(__name__)
app.secret_key = "1581"

def connect():
    return mysql.connector.connect(
        host="185.114.247.43", port=3306,
        database="sch688_vvedenie",
        user="sch688_vvedenie", password="Qwerty123"
    )

@app.route("/api/user_register", methods=['POST'])
def user_register():
    req = request.get_json()
    name = req.get('name')
    email = req.get('email')
    password = req.get('password')

    cnx = connect()
    try:
        cur = cnx.cursor(dictionary=True)
        cur.execute('SELECT id FROM users WHERE email = %s', (email,))
        if cur.fetchone():
            return jsonify({'error': 'Пользователь с таким email уже существует'})

        hashed_pw = generate_password_hash(password)
        cur.execute(
            'INSERT INTO `users`(`username`, `email`, `password_hash`, `balance`) VALUES (%s, %s, %s, %s)',
            (name, email, hashed_pw, 1000.00)
        )
        cnx.commit()
    finally:
        cur.close()
        cnx.close()

    return jsonify({'ok': True})

@app.route('/api/login', methods=['POST'])
def login():
    req = request.get_json()
    email = req.get('email')
    password = req.get('password')

    cnx = connect()
    try:
        cur = cnx.cursor(dictionary=True)
        cur.execute('SELECT id, username, email, password_hash FROM users WHERE email = %s', (email,))
        user = cur.fetchone()
    finally:
        cur.close()
        cnx.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Неверный email или пароль'})

    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']

    return jsonify({'id': user['id'], 'username': user['username'], 'email': user['email']})

@app.route('/profile')
@app.route('/lk')
def profile_page():
    if 'user_id' not in session:
        return redirect('/login')

    cnx = connect()
    try:
        cur = cnx.cursor(dictionary=True)
        cur.execute('SELECT id, username, email, balance FROM users WHERE id = %s', (session['user_id'],))
        user = cur.fetchone()
    finally:
        cur.close()
        cnx.close()

    if not user:
        session.clear()
        return redirect('/login')

    return render_template('lk.html', user=user)

@app.route('/api/get_balance', methods=['GET'])
def get_balance():
    if 'user_id' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    cnx = connect()
    try:
        cur = cnx.cursor(dictionary=True)
        cur.execute("SELECT balance FROM users WHERE id = %s", (session['user_id'],))
        bal = cur.fetchone()['balance']
        return jsonify({'balance': bal})
    finally:
        cur.close()
        cnx.close()


@app.route('/api/chat', methods=['POST'])
def api_chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Не авторизован'}), 401
    
    if llm is None:
        return jsonify({'error': 'Нейросеть не загружена'}), 500
    
    req = request.get_json(silent=True) or {}
    message = (req.get('message') or '').strip()
    if not message:
        return jsonify({'error': 'Пустое сообщение'}), 400

    prompt = f"<|im_start|>system\nТы полезный ассистент. Отвечай кратко и по-русски.<|im_end|>\n<|im_start|>user\n{message}<|im_end|>\n<|im_start|>assistant\n"
    
    try:
        output = llm(prompt, max_tokens=150, temperature=0.7, stop=["<|im_end|>"])
        reply = output['choices'][0]['text'].strip()
    except Exception as e:
        print("Ошибка ИИ:", e)
        return jsonify({'error': 'Ошибка при генерации ответа'}), 500


    cnx = connect()
    try:
        cur = cnx.cursor(dictionary=True)
        
        cur.execute("SELECT balance FROM users WHERE id = %s", (session['user_id'],))
        user_data = cur.fetchone()
        
        if user_data and user_data['balance'] >= 10.0:
            cur.execute("UPDATE users SET balance = balance - 10.0 WHERE id = %s", (session['user_id'],))
            cur.execute(
                "INSERT INTO transactions (user_id, amount, description) VALUES (%s, %s, %s)",
                (session['user_id'], -10.0, f"Запрос к ИИ: {message[:30]}...")
            )
            cnx.commit()
        else:
            return jsonify({'error': 'Недостаточно средств на балансе (нужно 10 ₽)'}), 400
            
    except Exception as e:
        print("Ошибка при записи транзакции:", e)
        return jsonify({'error': 'Ошибка базы данных при списании'}), 500
    finally:
        cur.close()
        cnx.close()

    return jsonify({'reply': reply})

@app.route('/api/deposit', methods=['POST'])
def deposit():
    if 'user_id' not in session:
        return jsonify({'error': 'Не авторизован'}), 401

    cnx = connect()
    try:
        cur = cnx.cursor(dictionary=True)
        
        cur.execute("UPDATE users SET balance = balance + 100.0 WHERE id = %s", (session['user_id'],))
        cur.execute(
            "INSERT INTO transactions (user_id, amount, description) VALUES (%s, %s, %s)",
            (session['user_id'], 100.0, "Пополнение баланса")
        )
        cnx.commit()
        
        cur.execute("SELECT balance FROM users WHERE id = %s", (session['user_id'],))
        new_balance = cur.fetchone()['balance']
        
        return jsonify({'ok': True, 'new_balance': new_balance})
        
    except Exception as e:
        print("Ошибка при пополнении:", e)
        return jsonify({'error': 'Ошибка сервера при пополнении'}), 500
    finally:
        cur.close()
        cnx.close()

@app.route('/transactions')
def transactions_page():
    if 'user_id' not in session:
        return redirect('/login')

    cnx = connect()
    try:
        cur = cnx.cursor(dictionary=True)
        cur.execute('''
            SELECT id, amount, description, created_at
            FROM transactions
            WHERE user_id = %s
            ORDER BY created_at DESC, id DESC
        ''', (session['user_id'],))
        transactions = cur.fetchall()
        
        cur.execute("SELECT balance FROM users WHERE id = %s", (session['user_id'],))
        user_balance = cur.fetchone()['balance']
    finally:
        cur.close()
        cnx.close()

    return render_template('transactions.html', transactions=transactions, balance=user_balance)

@app.route('/logout', methods=['GET', 'POST'])
def api_logout():
    session.clear()
    return redirect('/login')

@app.route("/")
def registration():
    return render_template('reg.html')

@app.route("/login")
def login_page():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)