import random

import bpy
from mathutils import Vector

num_monkeys = 1
frames = 5
position_radius = 5  # max dis from origin
scale = 1
collection_name = "Suzanne_Monkeys"

# set scene frame range
bpy.data.scenes["Scene"].frame_end = frames

if collection_name in bpy.data.collections:
    col = bpy.data.collections[collection_name]
else:
    col = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(col)


# Blender 4.2.10 uses "GPENCIL", 4.5.2 uses "GREASEPENCIL"
use_gpencil_type = "GPENCIL" if bpy.app.version < (4, 5, 0) else "GREASEPENCIL"

for f in range(frames):
    bpy.data.scenes["Scene"].frame_current = f + 1

    for i in range(num_monkeys):
        # add monkey
        if use_gpencil_type == "GPENCIL":
            bpy.ops.object.gpencil_add(
                align="WORLD", location=(0, 0, 0), scale=(1, 1, 1), type="MONKEY"
            )
        elif use_gpencil_type == "GREASEPENCIL":
            bpy.ops.object.grease_pencil_add(type="MONKEY", location=(0, 0, 0))

        monkey = bpy.context.object
        monkey.name = f"Monkey_{i+1}"
        monkey.scale = (scale, scale, scale)

        # Random pos
        monkey.location = Vector(
            (
                random.uniform(-position_radius, position_radius),
                random.uniform(-position_radius, position_radius),
                random.uniform(-position_radius, position_radius),
            )
        )

        # insert blank keyframe one frame later
        gp_obj = bpy.data.objects.get(monkey.name)
        gp_data = gp_obj.data

        gp_layer_fills = gp_data.layers["Fills"]
        gp_layer_lines = gp_data.layers["Lines"]

        gp_layer_fills.frames.new(f + 2)
        gp_layer_lines.frames.new(f + 2)

        # monkey in col
        for c in monkey.users_collection:
            c.objects.unlink(monkey)
        col.objects.link(monkey)
