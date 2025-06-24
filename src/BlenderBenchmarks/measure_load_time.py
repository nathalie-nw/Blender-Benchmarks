import time
from datetime import datetime

import bpy


def measure_load_time(filepath: str) -> None:
    start_time = time.time()
    bpy.ops.wm.open_mainfile(filepath)
    end_time = time.time()

    with open(
        "C:\\Users\\work\\Desktop\\empty_4.3_4.4_openingtime.txt", "a"
    ) as logfile:
        logfile.write(
            f"{datetime.now().isoformat()}: Ladezeit: {end_time - start_time:.2f} Sekunden\n"
        )

    # add filesize to write (amount of strokes/points frames etc)
