from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Game State (per session) ───
game_state = {
    "config": {},
    "levels": {},
    "moves": 0,
    "goal": 0,
    "won": False
}

# ─── Request Models ───
class StartRequest(BaseModel):
    mode: int   # 1 = two jugs, 2 = three jugs

class JugRequest(BaseModel):
    jug: str    # "A", "B", or "C"

class PourRequest(BaseModel):
    from_jug: str
    to_jug: str


# ══════════════════════════════════
#  ROUTES
# ══════════════════════════════════

@app.get("/")
def root():
    return {"status": "Water Jug API is running 🪣"}


@app.post("/start")
def start_game(req: StartRequest):
    if req.mode == 1:
        config = {"A": 4, "B": 3}
    else:
        config = {"A": 8, "B": 5, "C": 3}

    game_state["config"] = config
    game_state["levels"] = {k: 0 for k in config}
    game_state["moves"]  = 0
    game_state["goal"]   = random.randint(1, max(config.values()))
    game_state["won"]    = False

    return game_state


@app.post("/fill")
def fill_jug(req: JugRequest):
    jug = req.jug
    game_state["levels"][jug] = game_state["config"][jug]
    game_state["moves"] += 1
    game_state["won"] = check_win()
    return game_state


@app.post("/empty")
def empty_jug(req: JugRequest):
    jug = req.jug
    game_state["levels"][jug] = 0
    game_state["moves"] += 1
    game_state["won"] = check_win()
    return game_state


@app.post("/pour")
def pour_jug(req: PourRequest):
    a = req.from_jug
    b = req.to_jug
    space = game_state["config"][b] - game_state["levels"][b]
    amt   = min(game_state["levels"][a], space)
    game_state["levels"][a] -= amt
    game_state["levels"][b] += amt
    game_state["moves"] += 1
    game_state["won"] = check_win()
    return game_state


@app.post("/reset")
def reset_game():
    for k in game_state["levels"]:
        game_state["levels"][k] = 0
    game_state["moves"] = 0
    game_state["won"]   = False
    return game_state


# ─── Win Check (your original logic) ───
def check_win():
    return any(
        v == game_state["goal"]
        for v in game_state["levels"].values()
    )
