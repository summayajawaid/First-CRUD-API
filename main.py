from datetime import datetime
from uuid import uuid4
 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
 
app = FastAPI(title="Notes CRUD API", version="1.0.0")
 
NOTES: dict[str, dict] = {}
 
 
class NoteIn(BaseModel):
    title: str
    body: str = ""
    pinned: bool = False
 
 
class Note(NoteIn):
    id: str
    created_at: datetime
    updated_at: datetime
 
 
@app.get("/notes", response_model=list[Note])
def list_notes(q: str | None = None, pinned: bool | None = None):
    items = list(NOTES.values())
    if q:
        needle = q.lower()
        items = [n for n in items if needle in n["title"].lower() or needle in n["body"].lower()]
    if pinned is not None:
        items = [n for n in items if n["pinned"] is pinned]
    return sorted(items, key=lambda n: n["updated_at"], reverse=True)
 
 
@app.post("/notes", response_model=Note, status_code=201)
def create_note(payload: NoteIn):
    now = datetime.utcnow()
    note = {"id": str(uuid4()), "created_at": now, "updated_at": now, **payload.dict()}
    NOTES[note["id"]] = note
    return note
 
 
@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: str):
    note = NOTES.get(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note
 
 
@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: str, payload: NoteIn):
    note = NOTES.get(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.update(payload.dict(), updated_at=datetime.utcnow())
    return note
 
 
@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: str):
    if note_id not in NOTES:
        raise HTTPException(status_code=404, detail="Note not found")
    del NOTES[note_id]
 
 
@app.get("/stats")
def stats():
    values = NOTES.values()
    return {"total": len(NOTES), "pinned": sum(1 for n in values if n["pinned"])}
 
 
@app.post("/reset", status_code=204)
def reset():
    NOTES.clear()
