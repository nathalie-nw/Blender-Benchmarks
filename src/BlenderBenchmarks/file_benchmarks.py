import csv
import os
import time
from datetime import datetime


class bpy:
    pass


def measure_load_time(filepath: str) -> float:
    start_time = time.time()
    bpy.ops.wm.open_mainfile(filepath)
    return time.time() - start_time


def read_filesize(filepath: str) -> int:
    return os.stat(filepath).st_size


def write_result(
    output_filepath: str, load_times: list[tuple[datetime, float]]
) -> None:
    with open(output_filepath, "w", newline="") as logfile:
        writer = csv.DictWriter(logfile, delimiter=";", fieldnames=["time", "loadtime"])
        writer.writeheader()
        for timestamp, load_time in load_times:
            writer.writerow({"time": timestamp, "loadtime": load_time})

        # logfile.write(
        #    f"{datetime.now().isoformat()}: Ladezeit: {load_time:.2f} Sekunden\n"
        # )
