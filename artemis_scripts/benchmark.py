import json
import os

import psutil


def main():
    process = psutil.Process(os.getpid())
    with open("artemis_raw.json") as f:
        data = json.load(f)
    stats = data["benchmarks"][0]["stats"]
    print("throughput,memory_peak,cpu_usage")
    print(
        f'{stats["ops"]},'
        f"{process.memory_info().rss / (1024 * 1024)},"
        f"{psutil.cpu_percent(interval=1)}"
    )


if __name__ == "__main__":
    main()
