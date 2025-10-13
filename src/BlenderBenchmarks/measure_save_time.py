import os.path
import time

import bpy

start_time = time.time()

bpy.ops.wm.save_mainfile()

print(
    "\nfile:",
    os.path.basename(bpy.data.filepath),
    "\nsave time:",
    time.time() - start_time,
)
