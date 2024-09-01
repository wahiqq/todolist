import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import closing

app = FastAPI()

class TodoItem(BaseModel):
    task: str
    status: str

def init_db():
    with sqlite3.connect('todolist.db') as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS todolist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('complete', 'pending'))
            )
        ''')
        conn.commit()

init_db()

def get_db_cursor():
    conn = sqlite3.connect('todolist.db')
    return conn.cursor(), conn

def fetch_items(filter: str):
    conn = sqlite3.connect('todolist.db')
    try:
        with closing(conn.cursor()) as cur:
            if filter == "completed":
                cur.execute("SELECT * FROM todolist WHERE status = ?", ("complete",))
            elif filter == "pending":
                cur.execute("SELECT * FROM todolist WHERE status = ?", ("pending",))
            elif filter == "all":
                cur.execute("SELECT * FROM todolist")
            else:
                raise HTTPException(status_code=400, detail="Invalid filter name")
            items = cur.fetchall()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()
    return items

@app.get("/todolist")
def todolist(filter: str = "all"):
    if filter not in ["completed", "pending", "all"]:
        raise HTTPException(status_code=400, detail="Invalid filter name")
    return fetch_items(filter)

@app.post("/todolist")
def add_item(item: TodoItem):
    cur, conn = get_db_cursor()
    try:
        with closing(cur):
            cur.execute("INSERT INTO todolist (task, status) VALUES (:task, :status)", {"task": item.task, "status": item.status})
            conn.commit()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()
    return {"message": "Todo item added successfully"}

@app.put("/todolist/{item_id}")
def update_item(item_id: int, item: TodoItem):
    cur, conn = get_db_cursor()
    try:
        with closing(cur):
            cur.execute("UPDATE todolist SET task = :task, status = :status WHERE id = :id", {"task": item.task, "status": item.status, "id": item_id})
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Todo item not found")
            conn.commit()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()
    return {"message": "Todo item updated successfully"}

@app.delete("/todolist/{item_id}")
def delete_item(item_id: int):
    cur, conn = get_db_cursor()
    try:
        with closing(cur):
            cur.execute("DELETE FROM todolist WHERE id = :id", {"id": item_id})
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Todo item not found")
            conn.commit()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        conn.close()
    return {"message": "Todo item deleted successfully"}