import random

import bpy
from mathutils import Vector

NUM_LINES = 5
POINTS_PER_LINE = 15
FRAME_NUMBER = 1
RANGE_X = (-5, 5)
RANGE_Z = (-5, 5)
LINE_WIDTH = 30
GP_NAME = "GPencilObj"
NUM_LAYERS = 1
LAYER_NAME = "Layer"
MATERIAL_NAME = "GP_Material"

# Blender 4.2.10 uses "GPENCIL", 4.5.2 uses "GREASEPENCIL"
use_gpencil_type = "GPENCIL" if bpy.app.version < (4, 5, 0) else "GREASEPENCIL"

# Grease Pencil object
if GP_NAME in bpy.data.objects:
    gp_obj = bpy.data.objects[GP_NAME]
    gp = gp_obj.data
elif use_gpencil_type == "GPENCIL":
    bpy.ops.object.gpencil_add(type="EMPTY")
    gp_obj = bpy.context.object
    gp_obj.name = GP_NAME
elif use_gpencil_type == "GREASEPENCIL":
    bpy.ops.object.grease_pencil_add(type="EMPTY")
    gp_obj = bpy.context.object
    gp_obj.name = GP_NAME
gp_obj.select_set(True)
bpy.context.view_layer.objects.active = gp_obj
gp = gp_obj.data

# material
if not gp_obj.data.materials:
    if MATERIAL_NAME in bpy.data.materials:
        mat = bpy.data.materials[MATERIAL_NAME]
        if use_gpencil_type == "GREASEPENCIL":
            mat.grease_pencil.line_thickness = 30
    else:
        mat = bpy.data.materials.new(MATERIAL_NAME)
        if use_gpencil_type == "GREASEPENCIL":
            mat.grease_pencil.line_thickness = 30
    gp_obj.data.materials.append(mat)

material_index = 0


# layer
layer = None

if NUM_LAYERS == 1:
    # use current selected layer
    if hasattr(gp_obj.data, "layers") and gp_obj.data.layers.active:
        layer = gp_obj.data.layers.active
    else:
        # If no active layer, just use the first one or create one
        if len(gp_obj.data.layers) > 0:
            layer = gp_obj.data.layers[0]
        else:
            # Create a new one if none exist
            if use_gpencil_type == "GPENCIL":
                layer = gp_obj.data.layers.new(LAYER_NAME)
            else:
                layer = gp_obj.data.layers.new(name=LAYER_NAME)

else:
    # Create multiple layers
    for i in range(NUM_LAYERS):
        if use_gpencil_type == "GPENCIL":
            layer = gp_obj.data.layers.new(f"{LAYER_NAME}_{i+1}")
        else:
            layer = gp_obj.data.layers.new(name=f"{LAYER_NAME}_{i+1}", set_active=True)

# Unlock
layer.lock = False
layer.hide = False

#frame
frame = None
for f in layer.frames:
    if f.frame_number == FRAME_NUMBER:
        frame = f
        break
if frame is None:
    if use_gpencil_type == "GPENCIL":
        frame = layer.frames.new(FRAME_NUMBER)
    elif use_gpencil_type == "GREASEPENCIL":
        frame = layer.frames.new(frame_number=FRAME_NUMBER)


# random strokes
for _ in range(NUM_LINES):
    stroke = frame.strokes.new()
    stroke.material_index = material_index
    if use_gpencil_type == "GPENCIL":
        stroke.line_width = LINE_WIDTH
        stroke.points.add(count=POINTS_PER_LINE)
        for p in stroke.points:
            p.co = (
                random.uniform(*RANGE_X),
                0.0,
                random.uniform(*RANGE_Z),
            )

    # not working in 4.5
    elif use_gpencil_type == "GREASEPENCIL":
        stroke.points = [
            Vector((random.uniform(*RANGE_X), 0.0, random.uniform(*RANGE_Z)))
            for _ in range(POINTS_PER_LINE)
        ]
