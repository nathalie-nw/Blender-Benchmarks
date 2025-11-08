import argparse
import csv
import time

import psutil

parser = argparse.ArgumentParser(prog="CPUMonitor")
parser.add_argument("--loop-ms", default=250)
parser.add_argument("OUTPUT_FILE")
ARGS = parser.parse_args()
cpus = psutil.cpu_count()
cpu_columns = [f"cpu{c}" for c in range(cpus)]
header = ["Timestamp", *cpu_columns, "Total Memory", "Free Memory", "Used Memory"]


with open(ARGS.OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(header)

timestamp = 0
while True:
    if (time.time() - timestamp) > float(ARGS.loop_ms) / 1000:
        timestamp = time.time()
        per_cpu_percent = psutil.cpu_percent(interval=None, percpu=True)

        vm_statiscs = psutil.virtual_memory()
        total_ram = vm_statiscs.total
        free_ram = vm_statiscs.available
        used_ram = vm_statiscs.used
        joinable = [
            str(v) for v in [timestamp, *per_cpu_percent, total_ram, free_ram, used_ram]
        ]
        with open(ARGS.OUTPUT_FILE, "a", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(
                [timestamp, *per_cpu_percent, total_ram, free_ram, used_ram]
            )
