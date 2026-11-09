from datetime import datetime
from omnibrain.db import connect

def add_memory(content):
    with connect() as c:
        c.execute("INSERT INTO memories(content,created_at) VALUES(?,?)", (content.strip(), datetime.utcnow().isoformat()))

def list_memories():
    with connect() as c:
        return c.execute("SELECT * FROM memories ORDER BY id DESC").fetchall()

def delete_memory(mid):
    with connect() as c:
        c.execute("DELETE FROM memories WHERE id=?", (mid,))

def search_memories(query, limit=5):
    rows = list_memories()
    if not query.strip():
        return rows[:limit]
    terms = [t.lower() for t in query.split() if len(t) > 2]
    scored = []
    for row in rows:
        text = row["content"].lower()
        score = sum(text.count(term) for term in terms)
        if score:
            scored.append((score, row))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in scored[:limit]]
