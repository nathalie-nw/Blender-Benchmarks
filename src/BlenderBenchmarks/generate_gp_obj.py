import random

import bpy
from mathutils import Vector

num_obj = 1
frames = 1
position_radius = 5  # max dis from origin
scale = 1
collection_name = "GP_Obj"
type = "STROKE" # STROKE or MONKEY

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

    for i in range(num_obj):
        # add monkey (MONKEY), or stroke (STROKE)
        if use_gpencil_type == "GPENCIL":
            if type == "STROKE":
                bpy.ops.object.gpencil_add(
                    align="WORLD", location=(0, 0, 0), scale=(1, 1, 1), type="STROKE"
                )
            elif type == "MONKEY":
                bpy.ops.object.gpencil_add(
                    align="WORLD", location=(0, 0, 0), scale=(1, 1, 1), type="MONKEY"
                )
        elif use_gpencil_type == "GREASEPENCIL":
            if type == "STROKE":
                 bpy.ops.object.grease_pencil_add(type="STROKE", location=(0, 0, 0))
            elif type == "MONKEY":
                bpy.ops.object.grease_pencil_add(type="MONKEY", location=(0, 0, 0))

        gp_con_obj = bpy.context.object
        gp_con_obj.name = f"GP_Obj_{i+1}"
        gp_con_obj.scale = (scale, scale, scale)

        # Random pos
        gp_con_obj.location = Vector(
            (
                random.uniform(-position_radius, position_radius),
                random.uniform(-position_radius, position_radius),
                random.uniform(-position_radius, position_radius),
            )
        )

        # insert blank keyframe one frame later
        gp_obj = bpy.data.objects.get(gp_con_obj.name)
        gp_data = gp_obj.data
        
        gp_layer_lines = gp_data.layers["Lines"]
        gp_layer_lines.frames.new(f + 2)
        
        if type == "STROKE" and use_gpencil_type == "GPENCIL":
            gp_layer_colors = gp_data.layers["Colors"]
            gp_layer_colors.frames.new(f + 2)
            
        elif type == "STROKE" and use_gpencil_type == "GREASEPENCIL":
            gp_layer_color = gp_data.layers["Color"]
            gp_layer_color.frames.new(f + 2)     
                      
        elif type == "MONKEY":
            gp_layer_fills = gp_data.layers["Fills"]
            gp_layer_fills.frames.new(f + 2)

        # monkey in col
        for c in gp_con_obj.users_collection:
            c.objects.unlink(gp_con_obj)
        col.objects.link(gp_con_obj)
