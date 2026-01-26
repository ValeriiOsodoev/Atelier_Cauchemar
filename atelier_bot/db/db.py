from typing import List, Optional

import aiosqlite
import base64
from io import BytesIO
from PIL import Image

DB_PATH = "atelier.db"


def create_artwork_icon(image_data: bytes, size: tuple = (100, 100)) -> str:
    """Create a thumbnail icon from image data and return as base64 string."""
    try:
        # Open image from bytes
        image = Image.open(BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Create thumbnail
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save to bytes buffer
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        
        # Convert to base64
        icon_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/jpeg;base64,{icon_base64}"
    
    except Exception as e:
        print(f"Error creating icon: {e}")
        return None


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
    image_icon TEXT,
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
            "SELECT id, artwork_name, image_icon FROM artworks WHERE user_id = ?",
            (user_id,),
        )
        rows = await cur.fetchall()
        await cur.close()
        return [dict(r) for r in rows]


async def create_artwork(
    user_id: int, artwork_name: str, image_icon: Optional[str] = None, db_path: str = DB_PATH
) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "INSERT INTO artworks (user_id, artwork_name, image_icon) VALUES (?, ?, ?)",
            (user_id, artwork_name, image_icon),
        )
        await db.commit()


async def get_artwork_by_name_and_user(
    user_id: int, artwork_name: str, db_path: str = DB_PATH
) -> Optional[dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT id, artwork_name, image_icon FROM artworks WHERE user_id = ? AND artwork_name = ?",
            (user_id, artwork_name),
        )
        row = await cur.fetchone()
        await cur.close()
        return dict(row) if row else None


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


async def get_all_users(db_path: str = DB_PATH) -> List[dict]:
    """Get all users from database."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT user_id, username FROM users ORDER BY user_id"
        )
        rows = await cur.fetchall()
        return [dict(row) for row in rows]


async def search_users(query: str, db_path: str = DB_PATH) -> List[dict]:
    """Search users by username or user_id."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        
        # Try to find by user_id first
        try:
            user_id = int(query)
            cur = await db.execute(
                "SELECT user_id, username FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = await cur.fetchone()
            if row:
                return [dict(row)]
        except ValueError:
            pass
        
        # Search by username (partial match)
        cur = await db.execute(
            "SELECT user_id, username FROM users WHERE username LIKE ? ORDER BY username LIMIT 10",
            (f"%{query}%",)
        )
        rows = await cur.fetchall()
        return [dict(row) for row in rows]
