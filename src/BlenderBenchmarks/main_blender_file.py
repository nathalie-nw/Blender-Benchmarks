import datetime
import functools
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import bpy

logger = logging.getLogger()
logging.basicConfig(
    filename=r"C:\Users\work\Documents\HdM\Bachelor\files\my-results\log.log",
    encoding="utf-8",
    level=logging.DEBUG,
)
logger.setLevel(logging.DEBUG)


class MonitoringBase:
    def __init__(self, logfile_path, delay):
        self.process = None
        self.logfile = None
        self.logfile_path = logfile_path
        self.delay = delay
        with open(logfile_path, "w") as _:
            pass

    def check_if_already_running(self):
        if self.process is not None or self.logfile is not None:
            raise RuntimeError("Can't start logging if already started")

    def start(self):
        self.check_if_already_running()

        self.logfile = open(self.logfile_path, "a")
        self.process = subprocess.Popen(
            self.command_args,
            stdout=self.logfile,
        )

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            self.process.wait(1)
        if self.logfile is not None:
            self.logfile.close()

    @property
    def command_args(self):
        raise NotImplementedError()

    def __del__(self):
        self.stop()


class CPUMonitoring(MonitoringBase):
    # TODO: format
    PATH_TO_SCRIPT = r"C:\Users\work\Documents\HdM\Bachelor\code\Blender-Benchmarks\scripts\cpu_monitoring.py"

    @property
    def command_args(self):
        return [
            "py.exe",
            self.PATH_TO_SCRIPT,
            "--loop-ms",
            str(self.delay),
            str(self.logfile_path),
        ]

    def start(self):
        if not Path(self.PATH_TO_SCRIPT).exists():
            raise RuntimeError("Couldn't find Monitoring Script")
        self.check_if_already_running()

        self.process = subprocess.Popen(
            self.command_args,
        )


class GPUMonitoring(MonitoringBase):
    query = "--query-gpu=timestamp,pstate,temperature.gpu,utilization.gpu,memory.free,memory.used"

    @property
    def command_args(self):
        return ["nvidia-smi", self.query, "--format=csv", f"--loop-ms={self.delay}"]


def start_cpu_gpu_monitoring(
    result_dir: Path, delay: int
) -> tuple[MonitoringBase, MonitoringBase]:
    gpu_monitor = GPUMonitoring(logfile_path=result_dir / "gpu.csv", delay=delay)
    cpu_monitor = CPUMonitoring(logfile_path=result_dir / "cpu.csv", delay=delay)

    cpu_monitor.start()
    gpu_monitor.start()

    return cpu_monitor, gpu_monitor


def stop_cpu_gpu_monitoring(*args: MonitoringBase):
    for arg in args:
        arg.stop()


def create_context():
    # for window in bpy.context.window_manager.windows:
    #    screen = window.screen

    # for screen in bpy.data.screens:
    screen = bpy.context.screen
    for area in (a for a in screen.areas if a.type == "VIEW_3D"):
        region = next(
            (region for region in area.regions if region.type == "WINDOW"), None
        )
        if region is not None:
                # print(region.type)
            break

    context_override = bpy.context.copy()
    context_override["selected_objects"] = list(bpy.context.scene.objects)[0]
    context_override["area"] = area
    # context_override["screen"] = screen
    # context_override["window"] = window
    context_override["region"] = region
    return context_override


def measure_context_switch_time():
    if bpy.context.mode not in "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    obj = bpy.data.objects["GP_Obj_1"]
    obj.select_set(True)

    context_override = create_context()
    with bpy.context.temp_override(**context_override):
        # print(bpy.context.area, bpy.context.region)

        start_time = time.time()

        if bpy.app.version < (4, 3, 0):
            bpy.ops.object.mode_set(mode="EDIT_GPENCIL")
        else:
            bpy.ops.object.mode_set(mode="EDIT")
    print("measure_context_switch_time DONE")

    return time.time() - start_time


def set_noise_modifier(obj, modifier_type: str, noise_scale: int):
    mod = obj.grease_pencil_modifiers.new(name="NOISE", type=modifier_type)
    mod.noise_scale = noise_scale


def measure_modifier_apply_time(
    apply_to_all: bool = False, noise_scale: int = 1
) -> float:
    # measure modifier apply time
    context_override = create_context()
    with bpy.context.temp_override(**context_override):
        # print(bpy.context.area, bpy.context.region)
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        start_time = time.time()

        active_obj = bpy.context.active_object
        if active_obj.type not in ("GPENCIL", "GREASEPENCIL"):
            raise TypeError(
                f"object has to be 'GPENCIL' or 'GREASEPENCIL', not {active_obj.type}"
            )

        if active_obj.type == "GPENCIL":
            modifier_type = "GP_NOISE"
        elif active_obj.type == "GREASEPENCIL":
            modifier_type = "GREASE_PENCIL_NOISE"

        if apply_to_all:
            for obj in bpy.data.objects:
                if obj.type in ("GPENCIL", "GREASEPENCIL"):
                    set_noise_modifier(obj, modifier_type, noise_scale)
                    bpy.ops.object.gpencil_modifier_apply(modifier="Noise")

        else:
            set_noise_modifier(active_obj, modifier_type, noise_scale)
            bpy.ops.object.gpencil_modifier_apply(modifier="Noise")

        bpy.ops.object.gpencil_modifier_apply(modifier="NOISE")
        print("measure_modifier_apply_time DONE")
        return time.time() - start_time


def measure_fx_apply_time(apply_to_all: bool = False):
    context_override = create_context()
    with bpy.context.temp_override(**context_override):
        # print(bpy.context.area, bpy.context.region)
        if bpy.app.version < (4, 3, 0):
            bpy.ops.object.mode_set(mode="EDIT_GPENCIL")
        else:
            bpy.ops.object.mode_set(mode="EDIT")

        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        active_obj = bpy.context.active_object
        if active_obj.type not in ("GPENCIL", "GREASEPENCIL"):
            raise TypeError(
                f"object has to be 'GPENCIL' or 'GREASEPENCIL', not {active_obj.type}"
            )

        start_time = time.time()
        if apply_to_all:
            for obj in bpy.data.objects:
                obj.shader_effects.new(name="BLUR", type="FX_BLUR")
        else:
            obj = bpy.context.active_object
            obj.shader_effects.new(name="BLUR", type="FX_BLUR")

        bpy.ops.object.modifier_apply(modifier="BLUR")
        print("measure_fx_apply_time DONE")
        return time.time() - start_time


def measure_undo_time() -> float:
    start_time = time.time()
    if bpy.context.mode not in {"PAINT_GREASE_PENCIL", "PAINT_GPENCIL"}:
        if bpy.app.version < (4, 3, 0):
            bpy.ops.object.mode_set(mode="PAINT_GPENCIL")
        else:
            bpy.ops.object.mode_set(mode="PAINT_GREASE_PENCIL")
    bpy.ops.ed.undo()

    print("measure_undo_time DONE")

    return time.time() - start_time


def measure_save_time(filepath: str):
    start_time = time.time()

    bpy.ops.wm.save_as_mainfile(filepath=str(filepath))
    print("measure_save_time DONE")
    return time.time() - start_time


def measure_load_time(filepath: str) -> float:
    start_time = time.time()
    bpy.ops.wm.open_mainfile(filepath=str(filepath))
    print("measure_load_time DONE")
    return time.time() - start_time


# TODO: measure time it takes to play the whole timelone
def play_framerange() -> float:
    context_override = create_context()
    with bpy.context.temp_override(**context_override):
        # print(bpy.context.area, bpy.context.region)

        scene = bpy.context.scene
        scene.frame_current = 1

        end_frame = scene.frame_end

        # stop_data = {"stoptime": None}

        def stop_playback(scene):
            if scene.frame_current >= end_frame:
                bpy.ops.screen.animation_cancel(restore_frame=False)
                bpy.app.handlers.frame_change_post.remove(stop_playback)
                print("play_framerange DONE")
                # stop_data["stoptime"] = time.time()

        # Remove old handlers to avoid duplicates
        for handler in bpy.app.handlers.frame_change_post:
            if handler.__name__ == "stop_playback":
                bpy.app.handlers.frame_change_post.remove(handler)

        bpy.app.handlers.frame_change_post.append(stop_playback)

        bpy.ops.screen.animation_play()
        # start_time = time.time()

        # return stop_data["stoptime"] - start_time


def read_filesize(filepath: str) -> int:
    return os.stat(filepath).st_size  # noqa: F821


@dataclass
class GP_Contents_Count:
    objects: int = 0
    layers: int = 0
    points: int = 0


def count_gp_contents() -> GP_Contents_Count:
    object_count = 0
    layer_count = 0
    point_count = 0

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    for obj in bpy.context.scene.objects:
        if obj.type in ("GPENCIL", "GREASEPENCIL"):
            object_count += 1
            gp_data = obj.data
            for layer in gp_data.layers:
                layer_count += 1
                for frame in layer.frames:
                    strokes = (
                        frame.strokes
                        if obj.type == "GPENCIL"
                        else frame.drawing.strokes
                    )
                    for stroke in strokes:
                        point_count += len(stroke.points)

    return GP_Contents_Count(object_count, layer_count, point_count)


def write_metadata(
    test_file_path: Path, test_start_time: datetime.datetime, output_filepath: Path
):
    gp_contents_counts = count_gp_contents()
    meta_data = dict()
    meta_data["version"] = bpy.app.version_string
    meta_data["test file path"] = str(test_file_path)
    meta_data["timestamp"] = test_start_time.isoformat()
    meta_data["file size"] = read_filesize(test_file_path)
    meta_data["gp objects"] = gp_contents_counts.objects
    meta_data["gp layers"] = gp_contents_counts.layers
    meta_data["gp points"] = gp_contents_counts.points
    meta_data["framerange"] = bpy.data.scenes["Scene"].frame_end
    with open(output_filepath, "w") as f:
        json.dump(meta_data, f, indent=4)


def create_test_dir(parent, folder_name):
    new_dir = parent / folder_name
    new_dir.mkdir()
    return new_dir


def test_file_opening(
    result_dir: Path, file_to_open: str, monitoring_interval: int = 100
):
    result_dir_for_test = create_test_dir(result_dir, "test_file_opening")

    cpu_monitor, gpu_monitor = start_cpu_gpu_monitoring(
        result_dir_for_test, monitoring_interval
    )
    load_time = measure_load_time(file_to_open)
    stop_cpu_gpu_monitoring(cpu_monitor, gpu_monitor)

    with open(result_dir_for_test / "load_time.txt", "w") as f:
        f.write(str(load_time))


def test_play_framerange(result_dir: Path, monitoring_interval: int = 100):
    result_dir_for_test = create_test_dir(result_dir, "test_play_framerange")

    cpu_monitor, gpu_monitor = start_cpu_gpu_monitoring(
        result_dir_for_test, monitoring_interval
    )
    play_time = play_framerange()
    stop_cpu_gpu_monitoring(cpu_monitor, gpu_monitor)
    with open(result_dir_for_test / "play_time.txt", "w") as f:
        f.write(str(play_time))


def test_fx_apply_time(
    result_dir: Path, apply_to_all: bool = False, monitoring_interval: int = 100
):
    result_dir_for_test = create_test_dir(result_dir, "test_fx_apply_time")
    cpu_monitor, gpu_monitor = start_cpu_gpu_monitoring(
        result_dir_for_test, monitoring_interval
    )

    fx_apply_time = measure_fx_apply_time(apply_to_all)

    stop_cpu_gpu_monitoring(cpu_monitor, gpu_monitor)

    with open(result_dir_for_test / "fx_apply_time.txt", "w") as f:
        f.write(str(fx_apply_time))


def test_undo_time(result_dir, monitoring_interval: int = 100):
    result_dir_for_test = create_test_dir(result_dir, "test_undo_time")
    cpu_monitor, gpu_monitor = start_cpu_gpu_monitoring(
        result_dir_for_test, monitoring_interval
    )

    undo_time = measure_undo_time()
    stop_cpu_gpu_monitoring(cpu_monitor, gpu_monitor)

    with open(result_dir_for_test / "undo_time.txt", "w") as f:
        f.write(str(undo_time))


def test_modifier_timing(
    result_dir: Path, apply_to_all: bool = False, monitoring_interval: int = 100
):
    result_dir_for_test = create_test_dir(result_dir, "test_modifier_timing")
    cpu_monitor, gpu_monitor = start_cpu_gpu_monitoring(
        result_dir_for_test, monitoring_interval
    )

    modifier_apply_time = measure_modifier_apply_time(apply_to_all)
    stop_cpu_gpu_monitoring(cpu_monitor, gpu_monitor)

    with open(result_dir_for_test / "modifier_timing.txt", "w") as f:
        f.write(str(modifier_apply_time))


def test_context_switch_time(result_dir, monitoring_interval: int = 100):
    result_dir_for_test = create_test_dir(result_dir, "test_context_switch_time")
    cpu_monitor, gpu_monitor = start_cpu_gpu_monitoring(
        result_dir_for_test, monitoring_interval
    )

    context_switch_time = measure_context_switch_time()
    stop_cpu_gpu_monitoring(cpu_monitor, gpu_monitor)

    with open(result_dir_for_test / "context_switch_time.txt", "w") as f:
        f.write(str(context_switch_time))


def test_measure_save_time(result_dir, monitoring_interval: int = 100):
    result_dir_for_test = create_test_dir(result_dir, "test_save_time")
    cpu_monitor, gpu_monitor = start_cpu_gpu_monitoring(
        result_dir_for_test, monitoring_interval
    )

    save_time = measure_save_time(result_dir_for_test / "measured_save_file.blend")
    stop_cpu_gpu_monitoring(cpu_monitor, gpu_monitor)

    with open(result_dir_for_test / "save_time.txt", "w") as f:
        f.write(str(save_time))


def start_measuring(test_file: Path, output_dir: Path):
    test_start_time = datetime.datetime.now()
    logger.debug("Creating Output Directory")
    result_dir: Path = output_dir / test_start_time.strftime("%Y-%m-%d_%H%M%S")
    result_dir.mkdir(parents=True)

    # TODO: check how opening file time is calculated, seems off with bigger files
    logger.debug("Opening File")
    test_file_opening(result_dir, test_file)
    logger.debug("Write Metadata of current Test")
    write_metadata(test_file, test_start_time, result_dir / "metadata.json")

    # TODO: add delay or smth so that everything starts once the measurement before has ended
    logger.debug("Starting Test 'test_measure_save_time'")
    bpy.app.timers.register(
        functools.partial(test_measure_save_time, result_dir), first_interval=10
    )
    #test_measure_save_time(result_dir)

    logger.debug("Starting Test 'test_play_framerange'")
    bpy.app.timers.register(
        functools.partial(test_play_framerange, result_dir), first_interval=10
    )
    #test_play_framerange(result_dir)

    logger.debug("Starting Test 'test_context_switch_time'")
    bpy.app.timers.register(
        functools.partial(test_context_switch_time, result_dir), first_interval=10
    )
    # test_context_switch_time(result_dir)

    logger.debug("Starting Test 'test_undo_time'")
    bpy.app.timers.register(
        functools.partial(test_undo_time, result_dir), first_interval=10
    )
    # test_context_switch_time(result_dir)

    logger.debug("Starting Test 'test_fx_apply_time'")
    bpy.app.timers.register(
        functools.partial(test_fx_apply_time, result_dir), first_interval=20
    )
    # test_fx_apply_time(result_dir)

    logger.debug("Starting Test 'test_modifier_timing'")
    bpy.app.timers.register(
        functools.partial(test_modifier_timing, result_dir), first_interval=30
    )
    # test_modifier_timing(result_dir)

    # TODO: print(.... DONE) shows up before test is done. fix

if __name__ == "__main__":
    OUTPUT_DIR = Path(r"C:\Users\work\Documents\HdM\Bachelor\files\my-results")
    TEST_FILE = Path(
        r"C:\Users\work\Documents\HdM\Bachelor\files\my-test\test-05\test-05-01\test-05-01-01\test-05-01-01-01\4.2.13\test-05-01-01-01_4.2.13 LTS.blend"
    )
    start_measuring(TEST_FILE, OUTPUT_DIR)
