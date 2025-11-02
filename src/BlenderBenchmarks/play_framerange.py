import bpy

scene = bpy.context.scene
start_frame = scene.frame_current
end_frame = scene.frame_end

# stop playback when reaching the end
start_frame = 1

def stop_playback(scene):
    if scene.frame_current >= end_frame:
        bpy.ops.screen.animation_cancel(restore_frame=False)
        bpy.app.handlers.frame_change_post.remove(stop_playback)

# Remove old handlers to avoid duplicates
for handler in bpy.app.handlers.frame_change_post:
    if handler.__name__ == 'stop_playback':
        bpy.app.handlers.frame_change_post.remove(handler)

bpy.app.handlers.frame_change_post.append(stop_playback)

bpy.ops.screen.animation_play()

print(end_frame)
