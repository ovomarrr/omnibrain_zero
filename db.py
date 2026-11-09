import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("omnibrain.db")

def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL, created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, document_id INTEGER NOT NULL, content TEXT NOT NULL)""")

def create_conversation(title="New conversation"):
    with connect() as c:
        cur = c.execute("INSERT INTO conversations(title,created_at) VALUES(?,?)", (title, datetime.utcnow().isoformat()))
        return cur.lastrowid

def list_conversations():
    with connect() as c:
        return c.execute("SELECT * FROM conversations ORDER BY id DESC").fetchall()

def get_messages(cid):
    with connect() as c:
        return c.execute("SELECT role,content FROM messages WHERE conversation_id=? ORDER BY id", (cid,)).fetchall()

def save_message(cid, role, content):
    with connect() as c:
        c.execute("INSERT INTO messages(conversation_id,role,content,created_at) VALUES(?,?,?,?)",
                  (cid, role, content, datetime.utcnow().isoformat()))

def rename_conversation(cid, title):
    with connect() as c:
        c.execute("UPDATE conversations SET title=? WHERE id=?", (title[:80], cid))

def delete_conversation(cid):
    with connect() as c:
        c.execute("DELETE FROM messages WHERE conversation_id=?", (cid,))
        c.execute("DELETE FROM conversations WHERE id=?", (cid,))
