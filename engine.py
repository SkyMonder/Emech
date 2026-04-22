import os, chess, chess.engine, psutil
from fastapi import FastAPI, HTTPException

app = FastAPI()
engine = None
EMERGENCY_MODE = False
MEMORY_THRESHOLD = 85

def check_memory():
    global EMERGENCY_MODE
    mem = psutil.virtual_memory().percent
    if mem > MEMORY_THRESHOLD and not EMERGENCY_MODE:
        EMERGENCY_MODE = True
        if engine:
            engine.configure({"Hash": 16, "Threads": 1})
    elif mem <= MEMORY_THRESHOLD and EMERGENCY_MODE:
        EMERGENCY_MODE = False
        if engine:
            engine.configure({"Hash": 32, "Threads": 1})
    return EMERGENCY_MODE

def init_engine():
    global engine
    engine = chess.engine.SimpleEngine.popen_uci("./emergency_engine")
    engine.configure({"Skill Level": 18, "Hash": 32, "Threads": 1})

@app.on_event("startup")
async def startup():
    init_engine()

@app.get("/health")
def health():
    mem = psutil.virtual_memory()
    return {"status": "ok", "memory_percent": mem.percent, "emergency_mode": EMERGENCY_MODE}

@app.post("/get_move")
async def get_move(data: dict):
    try:
        check_memory()
        fen = data.get("fen")
        move_time = min(data.get("move_time", 0.5), 0.3 if EMERGENCY_MODE else 0.5)
        board = chess.Board(fen)
        result = engine.play(board, chess.engine.Limit(time=move_time, depth=8))
        return {"move": result.move.uci() if result.move else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
