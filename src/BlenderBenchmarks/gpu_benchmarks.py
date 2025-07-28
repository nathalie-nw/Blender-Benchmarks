import csv
import os
import subprocess
import time
from datetime import datetime


class bpy:
    pass


def measure_gpu_data(filepath: str):
    queried_data = query_data("memory.total")
    memory_total = int(queried_data.split(" ")[0])

    while not is_file_open(filepath):
        time.sleep(0.1)


def query_data(gpu_attribute: str) -> str:
    return subprocess.run(
        ["nividia-smi", f"--query-gpu={gpu_attribute}", "--format=noheader"],
        capture_output=True,
    ).stdout.decode("cp1252")


def collect_nividia_smi_data():

    # TODO: figure out which metrics to use (for example utilisation)


    queried_data = query_data("memory.used")
    memory_used = int(queried_data.split(" ")[0])

    queried_data = query_data("utilization.gpu")
    utilization_gpu = int(queried_data.split(" ")[0])

    return (memory_used, utilization_gpu)


def is_file_open(filepath: str) -> bool:
    """check if file is opened by another process"""
    try:
        os.rename(filepath, filepath)
    except OSError:
        return True
    return False



"""writes gpu data into a file while blender file is open"""
def gpu_memory_write(
    filepath: str,
    output_filepath: str,
    gpu_memory_over_time: list[tuple[datetime, float]],
) -> None:
    with open(output_filepath, "w", newline="") as logfile:
        writer = csv.DictWriter(
            logfile, delimiter=";", fieldnames=["time", "gpu_percentage", "gpu_utilization"]
        )
        writer.writeheader()

        # schreiben wenn file open
        while True:
            for timestamp, memory_percentage in gpu_memory_over_time:
                writer.writerow({"time": timestamp, "GPU %": gpu_percentage}, "GPU Utilization %": gpu_utilization)
            else:
                print("file closed")


# timestamp woher?

# memory_percentage = (memory_used / memory_total) * 100

#fps, render times