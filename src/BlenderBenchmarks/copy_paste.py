import bpy

frames = bpy.data.scenes["Scene"].frame_end

# frame numbers
source_frame = 1
frames_copy = 5
frames_to_copy = frames / frames_copy
target_frame = 1

use_gpencil_type = "GPENCIL" if bpy.app.version < (4, 5, 0) else "GREASEPENCIL"

obj = bpy.context.object
# blender 4.2
if use_gpencil_type == "GPENCIL":
    if not obj or obj.type != "GPENCIL":
        raise Exception("Select a Grease Pencil object first.")

    # Go to source frame
    bpy.context.scene.frame_set(source_frame)
    bpy.ops.object.mode_set(mode="EDIT_GPENCIL")

    bpy.context.area.type = "VIEW_3D"

    # select and copy strokes
    bpy.ops.gpencil.select_all(action="TOGGLE")
    bpy.ops.gpencil.copy()

    for f in range(frames_copy - 1):
        target_frame += frames_to_copy
        target_frame = int(target_frame)

        #  go to target frame
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.scene.frame_set(target_frame)
        print(target_frame)

        bpy.ops.object.mode_set(mode="EDIT_GPENCIL")
        gp = bpy.context.object.data
        print(bpy.context.object.data)
        layer = gp.layers.active

        # add frame
        if not any(f.frame_number == target_frame for f in layer.frames):
            layer.frames.new(target_frame)

        # past strokes
        layer = obj.data.layers.active
        bpy.ops.gpencil.paste()
        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.context.area.type = "TEXT_EDITOR"


# blender 4.5
elif use_gpencil_type == "GREASEPENCIL":
    if not obj or obj.type != "GREASEPENCIL":
        raise Exception("Select a Grease Pencil object first.")

    # Go to source frame
    bpy.context.scene.frame_set(source_frame)
    bpy.ops.object.mode_set(mode="EDIT")

    # select and copy strokes
    bpy.ops.grease_pencil.select_all()
    bpy.ops.grease_pencil.copy()

    for f in range(frames_copy - 1):
        target_frame += frames_to_copy
        target_frame = int(target_frame)

        #  go to target frame
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.scene.frame_set(target_frame)
        print(target_frame)

        gp = bpy.context.object.data
        layer = gp.layers.active

        # add frame
        if not any(f.frame_number == target_frame for f in layer.frames):
            bpy.context.scene.frame_set(target_frame)
            bpy.ops.grease_pencil.insert_blank_frame()

        # past strokes
        layer = obj.data.layers.active
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.grease_pencil.paste()
        bpy.ops.object.mode_set(mode="OBJECT")
