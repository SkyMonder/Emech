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
        raise HTTPException(status_code=500, detail=str(e))                engine.configure({"Hash": 64, "Threads": 1})
        return False

def init_engine():
    global engine
    engine = chess.engine.SimpleEngine.popen_uci("./engine")
    engine.configure({
        "Skill Level": 18,
        "Hash": 64,
        "Threads": 1,
        "Move Overhead": 30,
    })
    send_log("INFO", "Emergency Engine загружен")

@app.on_event("startup")
async def startup():
    init_engine()

@app.get("/health")
def health():
    memory = psutil.virtual_memory()
    return {
        "status": "ok",
        "memory_percent": memory.percent,
        "emergency_mode": EMERGENCY_MODE,
        "available_mb": memory.available // (1024 * 1024)
    }

@app.post("/get_move")
async def get_move(data: dict):
    try:
        check_memory()
        fen = data.get("fen")
        move_time = data.get("move_time", 0.5)
        if EMERGENCY_MODE:
            move_time = min(move_time, 0.3)
        board = chess.Board(fen)
        if EMERGENCY_MODE:
            result = engine.play(board, chess.engine.Limit(time=move_time, depth=8))
        else:
            result = engine.play(board, chess.engine.Limit(time=move_time))
        return {"move": result.move.uci() if result.move else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))        "Threads": 1,
        "Move Overhead": 30,      # очень маленький запас
    })
    print("Emergency Engine загружен и настроен на экономию памяти")

@app.on_event("startup")
async def startup():
    init_engine()

@app.get("/health")
def health():
    memory = psutil.virtual_memory()
    return {
        "status": "ok",
        "memory_percent": memory.percent,
        "emergency_mode": EMERGENCY_MODE,
        "available_mb": memory.available // (1024 * 1024)
    }

@app.post("/get_move")
async def get_move(data: dict):
    try:
        # Проверяем память перед каждым ходом
        check_memory()
        
        fen = data.get("fen")
        move_time = data.get("move_time", 0.5)  # по умолчанию 0.5 сек
        
        # Если экстренный режим, уменьшаем время на ход
        if EMERGENCY_MODE:
            move_time = min(move_time, 0.3)
        
        board = chess.Board(fen)
        
        # Используем экстренные настройки поиска
        if EMERGENCY_MODE:
            result = engine.play(board, chess.engine.Limit(time=move_time, depth=8))
        else:
            result = engine.play(board, chess.engine.Limit(time=move_time))
        
        return {"move": result.move.uci() if result.move else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def stats():
    """Возвращает статистику использования ресурсов"""
    memory = psutil.virtual_memory()
    return {
        "total_mb": memory.total // (1024 * 1024),
        "available_mb": memory.available // (1024 * 1024),
        "used_percent": memory.percent,
        "emergency_mode": EMERGENCY_MODE,
        "engine_config": {
            "Skill Level": 18 if EMERGENCY_MODE else 20,
            "Hash": 32 if EMERGENCY_MODE else 64,
        }
    }
