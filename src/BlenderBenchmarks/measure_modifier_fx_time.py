import os.path
from pathlib import Path
import time

import bpy


# use_gpencil_type = "GPENCIL" if bpy.app.version < (4, 5, 0) else "GREASEPENCIL"


def set_noise_modifier(obj, modifier_type: str, noise_scale: int):
    mod = obj.grease_pencil_modifiers.new(name="NOISE", type=modifier_type)
    mod.noise_scale = noise_scale


def measure_modifier_apply_time(
    apply_to_all: bool = False, noise_scale: int = 1
) -> float:
    # measure modifier apply time
    start_time = time.time()

    active_obj = bpy.context.active_object
    if active_obj.type not in ("GPENCIL", "GREASEPENCIL"):
        raise TypeError(f"object has to be 'GPENCIL' or 'GREASEPENCIL', not {active_obj.type}")


    if active_obj.type == "GPENCIL":
        modifier_type = "GP_NOISE"
    elif active_obj.type == "GREASEPENCIL":
        modifier_type = "GREASE_PENCIL_NOISE"

    if apply_to_all:
        for obj in bpy.data.objects:
            if obj.type in ("GPENCIL", "GREASEPENCIL"):
                set_noise_modifier(obj, modifier_type, noise_scale)
    else:
        set_noise_modifier(active_obj, modifier_type, noise_scale)
    return time.time() - start_time


def measure_fx_apply_time(apply_to_all: bool = False):
    start_time = time.time()
    if apply_to_all:
        for obj in bpy.data.objects:
            obj.shader_effects.new(name="BLUR", type="FX_BLUR")
    else:
        obj.shader_effects.new(name="BLUR", type="FX_BLUR")
    return time.time() - start_time


loaded_file_name = Path(bpy.data.filepath).name
modifier_apply_time = measure_modifier_apply_time()
fx_apply_time = measure_fx_apply_time()

print(f"File: {loaded_file_name}, modifier time: {modifier_apply_time}")
print(f"File: {loaded_file_name}, fx time: {fx_apply_time}")
