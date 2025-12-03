import os
import json
import shutil
import subprocess

RESULT_DIR = "local_results"

def run_worker(points=100000):
    """Run the worker.py script locally."""
    print(f"[test] Running worker with {points} points...")

    env = os.environ.copy()
    env["POINTS_PER_WORKER"] = str(points)
    env["RESULT_DIR"] = RESULT_DIR

    subprocess.run(
        ["python3", "src/worker.py"],
        env=env,
        check=True
    )


def run_reducer():
    """Run the reducer.py script locally."""
    print(f"[test] Running reducer...")

    env = os.environ.copy()
    env["RESULT_DIR"] = RESULT_DIR

    subprocess.run(
        ["python3", "src/reducer.py"],
        env=env,
        check=True
    )


def reset_results():
    """Clear out the results directory."""
    if os.path.exists(RESULT_DIR):
        shutil.rmtree(RESULT_DIR)
    os.makedirs(RESULT_DIR, exist_ok=True)


def main():
    print("[test] Starting local Monte Carlo π estimation")
    reset_results()

    # Run multiple workers
    for i in range(3):
        print(f"[test] Worker {i+1}/3")
        run_worker(points=100000000)

    print()
    print("[test] Running reducer to aggregate results:")
    print("--------------------------------------------")

    run_reducer()

    print("--------------------------------------------")
    print("[test] Done.")


if __name__ == "__main__":
    main()

