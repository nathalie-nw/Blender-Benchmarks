import bpy

total_points = 0
per_object = {}

for obj in bpy.context.scene.objects:
    obj_points = 0

    # Blender 4.2.10
    if obj.type == "GPENCIL":
        gp_data = obj.data
        for layer in gp_data.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:
                    obj_points += len(stroke.points)

    # Blender 4.5.2
    elif obj.type == "GREASEPENCIL":
        gp_data = obj.data
        for layer in gp_data.layers:
            for frame in layer.frames:
                strokes = frame.drawing.strokes
                for stroke in strokes:
                    obj_points += len(stroke.points)

    # Store counts if object has points
    if obj_points > 0:
        per_object[obj.name] = obj_points
        total_points += obj_points


for name, count in per_object.items():
    print(f"  {name}: {count}")
print("Total Grease Pencil points:", total_points)
