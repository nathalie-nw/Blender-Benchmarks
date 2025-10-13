import os.path
import time

import bpy

# ----
apply_to_all = "NO"
# ----

start_time = time.time()
obj = bpy.context.active_object

# use_gpencil_type = "GPENCIL" if bpy.app.version < (4, 5, 0) else "GREASEPENCIL"

# measure modifier apply time
if apply_to_all == "YES":
    for obj in bpy.data.objects:
        if obj.type == "GPENCIL":
            mod = obj.grease_pencil_modifiers.new(name="NOISE", type="GP_NOISE")
            mod.noise_scale = 1
        elif obj.type == "GREASEPENCIL":
            mod = obj.modifiers.new(name="NOISE", type="GREASE_PENCIL_NOISE")
            mod.noise_scale = 1
elif obj.type == "GPENCIL":
    mod = obj.grease_pencil_modifiers.new(name="NOISE", type="GP_NOISE")
    mod.noise_scale = 1
elif obj.type == "GREASEPENCIL":
    mod = obj.modifiers.new(name="NOISE", type="GREASE_PENCIL_NOISE")
    mod.noise_scale = 1
else:
    print("error")

print(
    "\nfile:",
    os.path.basename(bpy.data.filepath),
    "\nmodifier time:",
    time.time() - start_time,
)


# measure fx apply time
start_time = time.time()
if apply_to_all == "YES":
    for obj in bpy.data.objects:
        obj.shader_effects.new(name="BLUR", type="FX_BLUR")
else:
    obj.shader_effects.new(name="BLUR", type="FX_BLUR")

print(
    "\nfile:",
    os.path.basename(bpy.data.filepath),
    "\nfx time:",
    time.time() - start_time,
)
