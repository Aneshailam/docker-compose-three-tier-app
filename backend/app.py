import os

import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_conn():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        autocommit=True,
    )


def serialize(row):
    row["created_at"] = row["created_at"].isoformat()
    return row


@app.get("/api/health")
def health():
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        return jsonify(status="ok", database="up")
    except Exception:
        return jsonify(status="degraded", database="down"), 503


@app.get("/api/tasks")
def list_tasks():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id, title, created_at FROM tasks ORDER BY id DESC LIMIT 100")
        rows = [serialize(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(tasks=rows)


@app.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    if not title:
        return jsonify(error="Field 'title' is required"), 400
    if len(title) > 200:
        return jsonify(error="Field 'title' is too long (max 200)"), 400

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO tasks (title) VALUES (%s)", (title,))
        task_id = cur.lastrowid
        cur.execute("SELECT id, title, created_at FROM tasks WHERE id = %s", (task_id,))
        row = serialize(cur.fetchone())
    conn.close()
    return jsonify(row), 201


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        deleted = cur.rowcount
    conn.close()
    if not deleted:
        return jsonify(error="Task not found"), 404
    return jsonify(deleted=task_id)
