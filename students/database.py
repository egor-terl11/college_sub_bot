import aiosqlite

DB_NAME = "students.sql"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                group_name TEXT NOT NULL
            )
        """)
        await db.commit()

async def create_user(id, name, group):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO users (id, name, group_name) VALUES(?, ?, ?)",
            (id, name, group)
        )
        await db.commit()

async def user_exists(id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT 1 FROM users WHERE id = ?", (id,)) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def get_user(id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT name, group_name FROM users WHERE id = ?", (id,)
        )
        row = await cursor.fetchone()
        if row:
            return {
                "name": row["name"],
                "group": row["group_name"]
            }
        return None

async def change_group(id: int, new_group: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET group_name = ? WHERE id = ?",
            (new_group, id)
        )
        await db.commit()