import os.path
import time

import bpy

start_time = time.time()


if bpy.context.mode not in {'PAINT_GREASE_PENCIL', 'PAINT_GPENCIL'}:
    if bpy.app.version < (4, 3, 0):
        bpy.ops.object.mode_set(mode="PAINT_GPENCIL")
    else:
        bpy.ops.object.mode_set(mode="PAINT_GREASE_PENCIL")


# Undo
bpy.ops.ed.undo()
print(
    "\nfile:",
    os.path.basename(bpy.data.filepath),
    "\nundo time:",
    time.time() - start_time,
)