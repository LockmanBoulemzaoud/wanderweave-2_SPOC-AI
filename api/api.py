# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow CORS so the UI (Streamlit or other) can call this API in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict to your UI origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
