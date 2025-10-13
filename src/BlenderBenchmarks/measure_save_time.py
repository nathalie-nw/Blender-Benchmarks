import os
import time

import bpy

start_time = time.time()

bpy.ops.wm.save_mainfile()

print(
    "\nFile:",
    os.path.basename(bpy.data.filepath),
    "\nsave time:",
    time.time() - start_time,
)
