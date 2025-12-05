import os
import json
import time
import uuid
import redis

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest

# Logging helper
def log(*args):
    print("[BACKEND]", *args, flush=True)

app = FastAPI()

# ------------------------------------------
# Static File Mount (serves /static/app.js)
# ------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

# ------------------------------------------
# INDEX HTML served at "/"
# ------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html", "r") as f:
        return f.read()

# ------------------------------------------
# CORS (frontend is now same-origin, but harmless)
# ------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------
# Redis init
# ------------------------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "chess-redis-master")
log("Connecting to Redis at:", REDIS_HOST)

try:
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    r.ping()
    log("Connected to Redis OK")
except Exception as e:
    log("ERROR connecting to Redis:", e)
    raise

REQUEST_COUNT = Counter("api_requests_total", "Total API requests")
JOB_LATENCY = Histogram("job_latency_seconds", "Time waiting for Stockfish")


class MoveRequest(BaseModel):
    game_id: str
    move: str
    fen: str


# ------------------------------------------
# API: Start game
# ------------------------------------------
@app.get("/start")
def start_game():
    REQUEST_COUNT.inc()
    game_id = str(uuid.uuid4())
    return {"game_id": game_id}

# ------------------------------------------
# API: Make move
# ------------------------------------------
@app.post("/move")
def make_move(req: MoveRequest):

    REQUEST_COUNT.inc()
    job_id = str(uuid.uuid4())

    job_payload = {
        "job_id": job_id,
        "game_id": req.game_id,
        "move": req.move,
        "fen": req.fen,
    }

    r.rpush("jobs", json.dumps(job_payload))

    with JOB_LATENCY.time():
        # Wait for worker result
        while True:
            result = r.get(f"result:{job_id}")
            if result:
                r.delete(f"result:{job_id}")
                return json.loads(result)

            time.sleep(0.05)

# ------------------------------------------
# Prometheus metrics
# ------------------------------------------
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
