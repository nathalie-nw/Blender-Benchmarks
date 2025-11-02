from pathlib import Path
import time

import bpy


def measure_save_time():
    start_time = time.time()

    bpy.ops.wm.save_mainfile()
    return time.time() - start_time


save_time = measure_save_time()
print(f"File: {Path(bpy.data.filepath).name}, save time: {measure_save_time}")
