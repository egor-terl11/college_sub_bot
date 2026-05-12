import libsql_experimental as libsql
import os

# Получаем данные для подключения из переменных окружения
DB_URL = os.getenv("TURSO_DATABASE_URL")
DB_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

def _get_conn():
    """Создаёт подключение к Turso, используя URL и токен."""
    return libsql.connect(database=DB_URL, auth_token=DB_TOKEN)

async def init_db():
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            group_name TEXT NOT NULL
        )
    """)
    conn.commit()

async def create_user(id, name, group):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO users (id, name, group_name) VALUES(?, ?, ?)",
        (id, name, group)
    )
    conn.commit()

async def user_exists(id: int):
    conn = _get_conn()
    result = conn.execute("SELECT 1 FROM users WHERE id = ?", (id,)).fetchone()
    return result is not None

async def get_user(id: int):
    conn = _get_conn()
    conn.row_factory = lambda cursor, row: {"name": row[0], "group": row[1]}
    row = conn.execute("SELECT name, group_name FROM users WHERE id = ?", (id,)).fetchone()
    return row

async def change_group(id: int, new_group: str):
    conn = _get_conn()
    conn.execute(
        "UPDATE users SET group_name = ? WHERE id = ?",
        (new_group, id)
    )
    conn.commit()