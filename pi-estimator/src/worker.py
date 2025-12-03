import os
import json
import random
import uuid

def estimate_chunk(num_points: int) -> tuple[int, int]:
    """Simulate num_points Monte Carlo trials.
    Returns (inside, total)."""
    inside = 0
    for _ in range(num_points):
        x = random.random() * 2 - 1   # Uniform in [-1, 1]
        y = random.random() * 2 - 1
        if x*x + y*y <= 1:
            inside += 1
    return inside, num_points


def main():
    # How many points this worker should simulate
    points_per_worker = int(os.environ.get("POINTS_PER_WORKER", "100000"))

    # Where to write the result file
    result_dir = os.environ.get("RESULT_DIR", "/results")

    # Make sure the directory exists
    os.makedirs(result_dir, exist_ok=True)

    # Perform the Monte Carlo trials
    inside, total = estimate_chunk(points_per_worker)

    # Generate a unique filename so workers don't clash
    result_file = os.path.join(result_dir, f"result-{uuid.uuid4()}.json")

    # Write out the result
    with open(result_file, "w") as f:
        json.dump({"inside": inside, "total": total}, f)

    print(f"[worker] Completed {total} points → inside={inside}")
    print(f"[worker] Wrote result to {result_file}")


if __name__ == "__main__":
    main()

