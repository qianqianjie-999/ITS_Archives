import os
import pymysql

def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', 3306)),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', '123456'),
        database=os.environ.get('DB_NAME', 'smart_traffic'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
