import bpy
import time

start_time = time. time()

use_gpencil_type = "GPENCIL" if bpy.app.version < (4, 5, 0) else "GREASEPENCIL"

if bpy.context.object.mode == "OBJECT":
    if use_gpencil_type == "GPENCIL":
        bpy.ops.object.mode_set (mode="EDIT_GPENCIL")
    elif use_gpencil_type == "GREASEPENCIL":
        bpy.ops.object.mode_set (mode="EDIT")
        
    print(f"Time: {time.time()-start_time:.4f} seconds")

else: print("wrong context")


