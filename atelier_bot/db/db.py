from typing import List, Optional

import aiosqlite

DB_PATH = "/shared/atelier.db"

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT
);

CREATE TABLE IF NOT EXISTS paper_balance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    paper_name TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS artworks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    artwork_name TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    artwork_name TEXT NOT NULL,
    paper_name TEXT NOT NULL,
    copies INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


async def init_db(path: str = DB_PATH) -> None:
    async with aiosqlite.connect(path) as db:
        await db.executescript(CREATE_TABLES_SQL)
        await db.commit()


# Users
async def get_user(user_id: int, db_path: str = DB_PATH) -> Optional[dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT user_id, username FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = await cur.fetchone()
        await cur.close()
        if row:
            return dict(row)
        return None


async def create_or_update_user(
    user_id: int, username: Optional[str], db_path: str = DB_PATH
) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (user_id, username)"
            " VALUES (?, ?)",
            (user_id, username),
        )
        await db.commit()


# Paper balance
async def get_papers_for_user(
    user_id: int, db_path: str = DB_PATH
) -> List[dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT id, paper_name, quantity FROM paper_balance"
            " WHERE user_id = ?",
            (user_id,),
        )
        rows = await cur.fetchall()
        await cur.close()
        return [dict(r) for r in rows]


async def get_paper_by_id(
    paper_id: int, db_path: str = DB_PATH
) -> Optional[dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT id, paper_name, quantity, user_id FROM paper_balance"
            " WHERE id = ?",
            (paper_id,),
        )
        row = await cur.fetchone()
        await cur.close()
        return dict(row) if row else None


async def decrement_paper(
    paper_id: int, amount: int, db_path: str = DB_PATH
) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "UPDATE paper_balance SET quantity = quantity - ?"
            " WHERE id = ?",
            (amount, paper_id),
        )
        await db.commit()


async def add_paper_for_user(
    user_id: int, paper_name: str, quantity: int, db_path: str = DB_PATH
) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "INSERT INTO paper_balance (user_id, paper_name, quantity)"
            " VALUES (?, ?, ?)",
            (user_id, paper_name, quantity),
        )
        await db.commit()


# Artworks
async def get_artworks_for_user(
    user_id: int, db_path: str = DB_PATH
) -> List[dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT id, artwork_name FROM artworks WHERE user_id = ?",
            (user_id,),
        )
        rows = await cur.fetchall()
        await cur.close()
        return [dict(r) for r in rows]


async def create_artwork(
    user_id: int, artwork_name: str, db_path: str = DB_PATH
) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "INSERT INTO artworks (user_id, artwork_name) VALUES (?, ?)",
            (user_id, artwork_name),
        )
        await db.commit()


# Orders
async def create_order(
    user_id: int,
    artwork_name: str,
    paper_name: str,
    copies: int,
    status: str,
    created_at: str,
    db_path: str = DB_PATH,
) -> int:
    async with aiosqlite.connect(db_path) as db:
        cur = await db.execute(
            "INSERT INTO orders (user_id, artwork_name, paper_name, copies,"
            " status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, artwork_name, paper_name, copies, status, created_at),
        )
        await db.commit()
        return cur.lastrowid
