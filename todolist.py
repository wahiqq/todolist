import sqlite3
from fastapi 
import FastAPI, HTTPException
from pydantic import BaseModel


app = fastapi.FastAPI()

g_todolist = [
    {"id": 1, "text": "Something to do", "done": True},
    {"id": 2, "text": "Something else to do later", "done": False},
]


@app.get("/todolist")
def todolist(filter: str | None = "all"):
    if filter == "completed":
        return [item for item in g_todolist if item["done"]]
    if filter == "pending":
        return [item for item in g_todolist if not item["done"]]
    if filter == "all":
        return g_todolist
    raise fastapi.HTTPException(status_code=400, detail="Invalid filter name")


def get_item_by_id(id: int):
    for item in g_todolist:
        if item["id"] == id:
            return item
    raise fastapi.HTTPException(status_code=404, detail="Not found")


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
