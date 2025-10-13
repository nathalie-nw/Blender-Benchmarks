import os.path

import bpy

print(
    "\nfile:",
    os.path.basename(bpy.data.filepath),
    "\nframe range:",
    bpy.data.scenes["Scene"].frame_end,
)
