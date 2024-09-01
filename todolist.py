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


def success(**kwargs):
    return {"status": "success", **kwargs}


@app.post("/todolist")
def new_item(item: TodoItem):
    maxid = max([item["id"] for item in g_todolist])
    newid = maxid + 1
    g_todolist.append({"id": newid, "text": item.text, "done": False})
    return success(url=f"/todolist/{newid}")


class ItemMods(BaseModel):
    """
    User may want to change either the text,
    or the "done" status of an item, or both.
    """

    text: str | None = None
    done: bool | None = None


@app.put("/todolist/{id}")
def mod_item(id: int, mods: ItemMods):
    item = get_item_by_id(id)
    if mods.text != None:
        item["text"] = mods.text
    if mods.done != None:
        item["done"] = mods.done
    return success()


@app.delete("/todolist/{id}")
def del_item(id: int):
    g_todolist.remove(get_item_by_id(id))
    return success()
