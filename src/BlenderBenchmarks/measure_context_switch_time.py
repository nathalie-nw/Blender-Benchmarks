import bpy
import time


def measure_context_switch_time(gpencil_type: str):
    bpy.ops.object.mode_set(mode="OBJECT")
    start_time = time.time()

    if gpencil_type == "GPENCIL":
        bpy.ops.object.mode_set(mode="EDIT_GPENCIL")
    elif gpencil_type == "GREASEPENCIL":
        bpy.ops.object.mode_set(mode="EDIT")

    return time.time() - start_time


if __name__ == "__main__":
    gpencil_type = "GPENCIL" if bpy.app.version < (4, 5, 0) else "GREASEPENCIL"
    context_switch_time = measure_context_switch_time(gpencil_type)

    print(f"Time: {context_switch_time:.4f} seconds")
