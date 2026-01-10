from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Question(BaseModel):
    text: str


@app.post("/ask")
def ask(q: Question):
    return {"question": q.text, "answer": "test"}