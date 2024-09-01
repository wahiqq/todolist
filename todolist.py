import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = fastapi.FastAPI()

def init_db():
    with sqlite3.connect('todolist.db') as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS todolist (
                id integer primary key autoincrement,
                task text not null,
                done boolean not null
            )
        ''')
        cur.commit()


init_db()

def get_db_cursor():
    cur = sqlite3.connect('todolist.db')
    return cur.cursor(), cur


def fetch_items(filter: str):
    cur, cur = get_db_cursor()
    if filter == "completed":
        cur.execute("SELECT * FROM todolist WHERE done = 1")
    elif filter == "pending":
        cur.execute("SELECT * FROM todolist WHERE done = 0")
    elif filter == "all":
        cur.execute("SELECT * FROM todolist")
    else:
        cur.close()
        raise HTTPException(status_code=400, detail="Invalid filter name")
    items = cur.fetchall()
    cur.close()
    return items

@app.get("/todolist")
def todolist(filter: str | None = "all"):
    items = fetch_items(filter)
    return [{"id": item[0], "task": item[1], "done": item[2]} for item in items]


def get_item_by_id(id: int):
    cur, cur = get_db_cursor()
    cur.execute("SELECT * FROM todolist WHERE id = ?", (id,))
    item = cur.fetchone()
    cur.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Not found")
    return {"id": item[0], "task": item[1], "done": item[2]}

@app.get("/todolist/{id}")
def get_item(id: int):
    return get_item_by_id(id)


class TodoItem(BaseModel):
    text: str

class ItemMods(BaseModel):
    text: str | None = None
    done: bool | None = None



@app.post("/todolist")
def add_item(item: TodoItem):
    cur, cur = get_db_cursor()
    cur.execute("INSERT INTO todolist (task, done) VALUES (?, ?)", (item.text, False))
    cur.commit()
    newid = cur.lastrowid
    cur.close()
    return {"url": f"/todolist/{newid}"}

@app.put("/todolist/{id}")
def mod_item(id: int, mods: ItemMods):
    cur, cur = get_db_cursor()
    if mods.text is not None:
        cur.execute("UPDATE todolist SET task = ? WHERE id = ?", (mods.text, id))
    if mods.done is not None:
        cur.execute("UPDATE todolist SET done = ? WHERE id = ?", (mods.done, id))
    cur.commit()
    cur.close()
    return {"status": "success"}

@app.delete("/todolist/{id}")
def del_item(id: int):
    cur, cur = get_db_cursor()
    cur.execute("DELETE FROM todolist WHERE id = ?", (id,))
    cur.commit()
    cur.close()
    return {"status": "success"}