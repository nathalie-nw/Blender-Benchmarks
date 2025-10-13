import os
import time

import bpy

start_time = time.time()


# Check if in Draw Mode
if bpy.context.mode in {"PAINT_GREASE_PENCIL", "PAINT_GPENCIL"}:
    bpy.ops.ed.undo()
    print(
        "\nFile:",
        os.path.basename(bpy.data.filepath),
        "\nundo time:",
        time.time() - start_time,
    )


else:
    bpy.context.mode
    print("Not in Grease Pencil draw mode, undo skipped.")
