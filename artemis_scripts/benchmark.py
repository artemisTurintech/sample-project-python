import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import psutil


def _total_rss(procs):
    total = 0
    for p in procs:
        try:
            total += p.memory_info().rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return total


def run_once(raw_json_path: Path) -> dict:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "--benchmark-only",
        f"--benchmark-json={raw_json_path}",
    ]
    psutil.cpu_percent(interval=None)
    proc = subprocess.Popen(cmd)
    parent = psutil.Process(proc.pid)

    peak_rss = 0
    cpu_samples = []
    while proc.poll() is None:
        try:
            procs = [parent] + parent.children(recursive=True)
        except psutil.NoSuchProcess:
            procs = []
        peak_rss = max(peak_rss, _total_rss(procs))
        cpu_samples.append(psutil.cpu_percent(interval=None))
        time.sleep(0.05)
    proc.wait()

    with raw_json_path.open() as f:
        stats = json.load(f)["benchmarks"][0]["stats"]

    return {
        "throughput": stats["ops"],
        "memory_peak": peak_rss / (1024 * 1024),
        "cpu_usage": sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0.0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--output", type=Path, default=Path("artemis_results.csv"))
    parser.add_argument("--raw-json", type=Path, default=Path("artemis_raw.json"))
    args = parser.parse_args()

    rows = [run_once(args.raw_json) for _ in range(args.runs)]

    with args.output.open("w") as f:
        f.write("throughput,memory_peak,cpu_usage\n")
        for r in rows:
            f.write(f'{r["throughput"]},{r["memory_peak"]},{r["cpu_usage"]}\n')

    try:
        args.raw_json.unlink()
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    main()
