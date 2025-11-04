# api/index.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Input(BaseModel):
    text: str

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(inp: Input):
    # TODO: importe et appelle ton vrai code ici
    # ex: from src.mon_module import run_demo
    #     result = run_demo(inp.text)
    # Pour l'instant on renvoie juste l'echo :
    return {"result": f"you sent: {inp.text}"}
