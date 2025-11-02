import bpy
from dataclasses import dataclass

@dataclass
class GP_Contents_Count:
    objects: int = 0
    layers: int = 0
    points: int = 0


def count_gp_contents() -> GP_Contents_Count:
    object_count = 0
    layer_count = 0
    point_count = 0

    bpy.ops.object.mode_set (mode="OBJECT")

    for obj in bpy.context.scene.objects:
        if obj.type in ("GPENCIL", "GREASEPENCIL"):
            object_count += 1
            gp_data = obj.data
            for layer in gp_data.layers:
                layer_count += 1
                for frame in layer.frames:
                    strokes = frame.strokes if obj.type == "GPENCIL" else frame.drawing.strokes
                    for stroke in strokes:
                        point_count += len(stroke.points)

    return GP_Contents_Count(object_count, layer_count, point_count)


if __name__ == '__main__':

    gp_content_counts = count_gp_contents()
    print("Total Grease Pencil objects:", gp_content_counts.objects)
    print("Total Grease Pencil layers:", gp_content_counts.layers)   
    print("Total Grease Pencil points:", gp_content_counts.points)

