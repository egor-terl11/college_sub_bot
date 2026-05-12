import os
import aiohttp

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
BASE_URL = TURSO_DATABASE_URL.replace("libsql://", "https://") + "/v2/pipeline"

async def _execute_sql(sql, params=None):
    """Выполняет SQL-запрос через HTTP API Turso."""
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
        if params:
            for p in params:
                if isinstance(p, str):
                    sql = sql.replace("?", f"'{p}'", 1)
                else:
                    sql = sql.replace("?", str(p), 1)
        payload = {
            "requests": [
                {"type": "execute", "stmt": sql}
            ]
        }
        async with session.post(BASE_URL, json=payload, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"Turso API error: {resp.status} {await resp.text()}")
            return await resp.json()

async def _fetch_one(sql, params=None):
    res = await _execute_sql(sql, params)
    try:
        rows = res["results"][0]["response"]["result"]["rows"]
        return rows[0] if rows else None
    except (KeyError, IndexError):
        return None

async def _execute_insert(sql, params=None):
    await _execute_sql(sql, params)

async def init_db():
    await _execute_sql("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            group_name TEXT NOT NULL
        )
    """)

async def create_user(id, name, group):
    await _execute_insert(
        "INSERT INTO users (id, name, group_name) VALUES(?, ?, ?)",
        (id, name, group)
    )

async def user_exists(id: int):
    row = await _fetch_one("SELECT 1 FROM users WHERE id = ?", [id])
    return row is not None

async def get_user(id: int):
    row = await _fetch_one("SELECT name, group_name FROM users WHERE id = ?", [id])
    if row:
        return {
            "name": row[0]["value"],
            "group": row[1]["value"]
        }
    return None

async def change_group(id: int, new_group: str):
    await _execute_insert(
        "UPDATE users SET group_name = ? WHERE id = ?",
        (new_group, id)
    )
