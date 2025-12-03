import os
import json

def load_results(result_dir: str):
    """Load all JSON result files from the directory."""
    inside_total = 0
    points_total = 0

    if not os.path.exists(result_dir):
        print(f"[reducer] Results directory not found: {result_dir}")
        return None, None

    files = [f for f in os.listdir(result_dir) if f.endswith(".json")]

    if not files:
        print("[reducer] No result files found. Did any workers run?")
        return None, None

    for name in files:
        file_path = os.path.join(result_dir, name)
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                inside_total += data.get("inside", 0)
                points_total += data.get("total", 0)
        except Exception as e:
            print(f"[reducer] Failed to read {file_path}: {e}")

    return inside_total, points_total


def compute_pi(inside: int, total: int) -> float:
    """Compute the Monte Carlo estimate of pi."""
    if total == 0:
        return float("nan")
    return 4 * inside / total


def main():
    result_dir = os.environ.get("RESULT_DIR", "/results")

    print(f"[reducer] Collecting results from: {result_dir}")
    inside, total = load_results(result_dir)

    if inside is None:
        print("[reducer] No valid data found. Exiting.")
        return

    pi_estimate = compute_pi(inside, total)

    print(f"[reducer] inside_total = {inside}")
    print(f"[reducer] points_total = {total}")
    print()
    print(f"Distributed π estimate: {pi_estimate}")


if __name__ == "__main__":
    main()

