import os, chess, chess.engine, traceback, time, psutil
from fastapi import FastAPI, HTTPException

app = FastAPI()
engine = None

# Пороги срабатывания
MEMORY_THRESHOLD = 80  # % использованной памяти для перехода в экстренный режим
EMERGENCY_MODE = False

def check_memory():
    """Проверяет текущее использование памяти"""
    global EMERGENCY_MODE
    memory_percent = psutil.virtual_memory().percent
    if memory_percent > MEMORY_THRESHOLD:
        if not EMERGENCY_MODE:
            print(f"⚠️ КРИТИЧЕСКИЙ УРОВЕНЬ ПАМЯТИ: {memory_percent}%. Переход в экстренный режим")
            EMERGENCY_MODE = True
            # Переконфигурируем движок на минимальные настройки
            if engine:
                engine.configure({"Hash": 32, "Threads": 1})
        return True
    else:
        if EMERGENCY_MODE:
            print(f"✅ Память восстановлена: {memory_percent}%. Выход из экстренного режима")
            EMERGENCY_MODE = False
            if engine:
                engine.configure({"Hash": 64, "Threads": 1})
        return False

def init_engine():
    global engine
    engine = chess.engine.SimpleEngine.popen_uci("./engine")
    engine.configure({
        "Skill Level": 18,        # чуть ниже для скорости
        "Hash": 64,               # минимальный размер
        "Threads": 1,
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
