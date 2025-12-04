import redis
import json
import time
import traceback
from prometheus_client import start_http_server, Counter
from stockfish import Stockfish
import os

# Simple logging helper
def log(*args):
    print("[WORKER]", *args, flush=True)

# --------------------------------------------------------
# 1. Load Stockfish
# --------------------------------------------------------
STOCKFISH_PATH = os.getenv("STOCKFISH_EXECUTABLE", "/usr/games/stockfish")
log("Using Stockfish path:", STOCKFISH_PATH)

try:
    ENGINE = Stockfish(
        path=STOCKFISH_PATH,
        parameters={"Threads": 1, "Skill Level": 10}
    )
    log("Stockfish initialized successfully.")
except Exception as e:
    log("Stockfish FAILED to start:", e)
    log(traceback.format_exc())
    raise

# --------------------------------------------------------
# 2. Redis connection
# --------------------------------------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "redis-master")
log("Connecting to Redis at:", REDIS_HOST)

try:
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    r.ping()
    log("Connected to Redis.")
except Exception as e:
    log("FAILED to connect to Redis:", e)
    log(traceback.format_exc())
    raise

REQUESTS = Counter("engine_requests_total", "How many Stockfish requests")

# --------------------------------------------------------
# 3. Worker loop
# --------------------------------------------------------
def main():
    log("Starting Prometheus metrics on port 9000...")
    start_http_server(9000)

    log("Worker READY. Waiting for jobs...")

    while True:
        try:
            job = r.lpop("jobs")

            if not job:
                time.sleep(0.5)
                continue

            log("Got job:", job)
            data = json.loads(job)
            REQUESTS.inc()

            # ---------------------------------------------
            # FIX: translate 'startpos' into full FEN
            # ---------------------------------------------
            fen = data["fen"]
            if fen == "startpos":
                fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
                log("Translated 'startpos' to full FEN:", fen)

            log("Setting FEN:", fen)
            ENGINE.set_fen_position(fen)

            best_move = ENGINE.get_best_move()
            log("Best move computed:", best_move)

            result_key = f"result:{data['job_id']}"
            r.set(result_key, json.dumps({"best_move": best_move}))
            log("Wrote result to Redis:", result_key)

        except Exception as e:
            log("ERROR in worker loop:", e)
            log(traceback.format_exc())

        time.sleep(0.05)

if __name__ == "__main__":
    log(">>> Worker starting up...")
    main()
