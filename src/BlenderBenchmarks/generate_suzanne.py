import random

import bpy
from mathutils import Vector

num_monkeys = 5
frame_to_insert = 1
position_radius = 5  # max dis from origin
scale = 1
collection_name = "Suzanne_Monkeys"


if collection_name in bpy.data.collections:
    col = bpy.data.collections[collection_name]
else:
    col = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(col)


# Blender 4.2.10 uses "GPENCIL", 4.5.2 uses "GREASEPENCIL"
use_gpencil_type = "GPENCIL" if bpy.app.version < (4, 5, 0) else "GREASEPENCIL"


for i in range(num_monkeys):
    # add monkey suzanne
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

    # monkey in col
    for c in monkey.users_collection:
        c.objects.unlink(monkey)
    col.objects.link(monkey)

    # insert keyframe

    #monkey.keyframe_insert(data_path="location", frame=frame_to_insert)
    #monkey.keyframe_insert(data_path="scale", frame=frame_to_insert)
