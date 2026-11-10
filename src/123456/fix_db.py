import mysql.connector

DB_NAME = 'sch688_vvedenie'
DB_USER = 'sch688_vvedenie'
DB_HOST = '185.114.247.43'
DB_PASS = 'Qwerty123'

try:
    print("Подключение к БД...")
    cnx = mysql.connector.connect(
        host=DB_HOST, port=3306, database=DB_NAME,
        user=DB_USER, password=DB_PASS
    )
    cursor = cnx.cursor()

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN first_name VARCHAR(50) DEFAULT 'Имя'")
        print("✅ Колонка first_name добавлена")
    except Exception as e:
        print("ℹ️ first_name уже есть или ошибка:", e)

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_name VARCHAR(50) DEFAULT 'Фамилия'")
        print("✅ Колонка last_name добавлена")
    except Exception as e:
        print("ℹ️ last_name уже есть или ошибка:", e)

    cnx.commit()
    print("Готово!")

except Exception as e:
    print("❌ Ошибка подключения:", e)
finally:
    if 'cursor' in locals(): cursor.close()
    if 'cnx' in locals() and cnx.is_connected(): cnx.close()