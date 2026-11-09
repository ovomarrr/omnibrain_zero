from datetime import datetime
from omnibrain.db import connect

def extract_text(filename, data):
    suffix = filename.lower().rsplit(".", 1)[-1]
    if suffix in ("txt", "md"):
        return data.decode("utf-8", errors="replace")
    if suffix == "pdf":
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == "docx":
        from docx import Document
        import io
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Unsupported file type.")

def split_chunks(text, size=1200, overlap=150):
    text = " ".join(text.split())
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(len(text), start + size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks

def ingest_document(filename, data):
    text = extract_text(filename, data)
    chunks = split_chunks(text)
    if not chunks:
        raise ValueError("No readable text found in document.")
    with connect() as c:
        cur = c.execute("INSERT INTO documents(filename,created_at) VALUES(?,?)", (filename, datetime.utcnow().isoformat()))
        did = cur.lastrowid
        c.executemany("INSERT INTO chunks(document_id,content) VALUES(?,?)", [(did, x) for x in chunks])
    return filename, len(chunks)

def list_documents():
    with connect() as c:
        return c.execute("""SELECT d.id,d.filename,d.created_at,COUNT(ch.id) AS chunks
            FROM documents d LEFT JOIN chunks ch ON ch.document_id=d.id
            GROUP BY d.id ORDER BY d.id DESC""").fetchall()

def delete_document(did):
    with connect() as c:
        c.execute("DELETE FROM chunks WHERE document_id=?", (did,))
        c.execute("DELETE FROM documents WHERE id=?", (did,))

def search_documents(query, limit=6):
    terms = [t.lower() for t in query.split() if len(t) > 2]
    with connect() as c:
        rows = c.execute("""SELECT chunks.content,documents.filename FROM chunks
            JOIN documents ON documents.id=chunks.document_id""").fetchall()
    scored = []
    for row in rows:
        text = row["content"].lower()
        score = sum(text.count(term) for term in terms)
        if score:
            scored.append((score, {"filename": row["filename"], "content": f"[{row['filename']}] {row['content']}"}))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in scored[:limit]]
