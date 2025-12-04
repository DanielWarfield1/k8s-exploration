from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import redis
import json
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
import time

# Simple logger helper
def log(*args):
    print("[BACKEND]", *args, flush=True)

app = FastAPI()

# --------------------------------------------------------
# Redis initialization
# --------------------------------------------------------
REDIS_HOST = "redis-master"
log("Connecting to Redis at:", REDIS_HOST)

try:
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    r.ping()
    log("Connected to Redis successfully.")
except Exception as e:
    log("ERROR connecting to Redis:", e)
    raise

REQUEST_COUNT = Counter("api_requests_total", "Total API requests")
JOB_LATENCY = Histogram("job_latency_seconds", "Time waiting for Stockfish")


class MoveRequest(BaseModel):
    game_id: str
    move: str
    fen: str


# --------------------------------------------------------
# Routes
# --------------------------------------------------------
@app.get("/start")
def start_game():
    REQUEST_COUNT.inc()
    game_id = str(uuid.uuid4())
    log(f"/start → new game_id generated: {game_id}")
    return {"game_id": game_id}


@app.post("/move")
def make_move(req: MoveRequest):
    REQUEST_COUNT.inc()
    job_id = str(uuid.uuid4())

    log(f"/move received: game_id={req.game_id}, move={req.move}, fen={req.fen}")
    log(f"Generated job_id={job_id}")

    # Push job to Redis queue
    job_payload = {
        "job_id": job_id,
        "game_id": req.game_id,
        "move": req.move,
        "fen": req.fen
    }

    r.rpush("jobs", json.dumps(job_payload))
    log("Job pushed to Redis:", job_payload)

    # Wait for worker response
    with JOB_LATENCY.time():
        log("Waiting for worker to compute result...")
        while True:
            result_raw = r.get(f"result:{job_id}")
            if result_raw:
                log("Result received from worker:", result_raw)

                # Cleanup Redis key
                r.delete(f"result:{job_id}")
                log("Deleted Redis key:", f"result:{job_id}")

                return json.loads(result_raw)

            # Avoid spinning too hot — also logs periodically to prevent total silence
            time.sleep(0.05)


@app.get("/metrics")
def metrics():
    log("/metrics scraped")
    return Response(generate_latest(), media_type="text/plain")
