import os

import bpy

print(
    "\nFile:",
    os.path.basename(bpy.data.filepath),
    "\nframe range:",
    bpy.data.scenes["Scene"].frame_end,
)
