import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import psutil


TEST_PREFIX = "test_benchmark_"


def _total_rss(procs):
    total = 0
    for p in procs:
        try:
            total += p.memory_info().rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return total


def _percentile(sorted_data, pct):
    if not sorted_data:
        return 0.0
    idx = min(int(len(sorted_data) * pct), len(sorted_data) - 1)
    return sorted_data[idx]


def _short_name(full_name: str) -> str:
    return full_name[len(TEST_PREFIX):] if full_name.startswith(TEST_PREFIX) else full_name


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
        benchmarks = json.load(f)["benchmarks"]

    row = {
        "memory_peak": peak_rss / (1024 * 1024),
        "cpu_usage": sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0.0,
    }
    for b in sorted(benchmarks, key=lambda x: x["name"]):
        name = _short_name(b["name"])
        stats = b["stats"]
        data_sorted = sorted(stats["data"])
        row[f"{name}_throughput"] = stats["ops"]
        row[f"{name}_latency_p50"] = stats["median"] * 1_000_000
        row[f"{name}_latency_p99"] = _percentile(data_sorted, 0.99) * 1_000_000
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--output", type=Path, default=Path("artemis_results.csv"))
    parser.add_argument("--raw-json", type=Path, default=Path("artemis_raw.json"))
    args = parser.parse_args()

    rows = [run_once(args.raw_json) for _ in range(args.runs)]
    columns = list(rows[0].keys())

    with args.output.open("w") as f:
        f.write(",".join(columns) + "\n")
        for r in rows:
            f.write(",".join(f"{r[c]}" for c in columns) + "\n")

    try:
        args.raw_json.unlink()
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    main()
