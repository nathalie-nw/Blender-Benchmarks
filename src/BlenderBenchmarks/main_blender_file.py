import datetime
import functools
import gc
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import bpy

logger = logging.getLogger()
logging.basicConfig(
    filename=r"C:\Users\awink\Desktop\BA\my-results\log.log",
    encoding="utf-8",
    level=logging.DEBUG,
)
logger.setLevel(logging.DEBUG)

VERSION = "4.2.13"
TEST_DIR = Path(r"C:\Users\awink\Desktop\BA\my-test")
TEST_FILES = list(TEST_DIR.glob(f"**/{VERSION}/**/*.blend"))
OUTPUT_DIR = Path(r"C:\Users\awink\Desktop\BA\my-results")


class MeasurePlayFramerange:
    def __init__(self, result_dir: Path, monitoring_interval: int = 100, **kwargs):
        self.end_frame = None
        self.start_time = None
        self.result_dir = result_dir
        self.result_dir.mkdir(exist_ok=True, parents=True)
        self.context = create_context()
        self.monitoring_interval = monitoring_interval
        self.gpu_monitor = None
        self.cpu_monitor = None
        self._running = False

    @property
    def running(self):
        return self._running

    def start_cpu_gpu_monitoring(self):
        self.cpu_monitor, self.gpu_monitor = start_cpu_gpu_monitoring(
            self.result_dir, self.monitoring_interval
        )

    def setup(self, handler_function):
        for handler in bpy.app.handlers.frame_change_post:
            if handler.__name__ == "stop_playback":
                bpy.app.handlers.frame_change_post.remove(handler)
        bpy.app.handlers.frame_change_post.append(handler_function)

    def start(self):
        self.start_cpu_gpu_monitoring()
        self._running = True
        with bpy.context.temp_override(**self.context):
            scene = bpy.context.scene
            scene.frame_current = 1
            self.end_frame = scene.frame_end
            self.start_time = time.time()
            bpy.ops.screen.animation_play()

    def stop(self):
        measured_time = time.time() - self.start_time
        self.write_timing_result(measured_time, "play_time.txt")
        self._running = False
        self.cpu_monitor.stop()
        self.gpu_monitor.stop()

    def write_timing_result(self, result: float, filename: str):
        with open(self.result_dir / filename, "w") as f:
            f.write(str(result))
        print("Wrote result to", self.result_dir / filename)


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
    PATH_TO_SCRIPT = r"C:\Users\awink\Desktop\Blender-Benchmarks\scripts\cpu_monitor.py"

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


play_framerange_test: MeasurePlayFramerange = None
file_loaded = False
is_a_test_running = False


def start_cpu_gpu_monitoring(
    result_dir: Path, delay: int
) -> tuple[MonitoringBase, MonitoringBase]:
    gpu_monitor = GPUMonitoring(logfile_path=result_dir / "gpu.csv", delay=delay)
    cpu_monitor = CPUMonitoring(logfile_path=result_dir / "cpu.csv", delay=delay)

    cpu_monitor.start()
    gpu_monitor.start()
    time.sleep(0.2)

    return cpu_monitor, gpu_monitor


def stop_cpu_gpu_monitoring(*args: MonitoringBase):
    for arg in args:
        arg.stop()


def create_context():
    screen = bpy.context.screen
    context_override = bpy.context.copy()

    if screen is None:
        window = bpy.context.window_manager.windows[-1]
        screen = window.screen
        context_override["window"] = window
        context_override["screen"] = screen

    for area in (a for a in screen.areas if a.type == "VIEW_3D"):
        region = next(
            (region for region in area.regions if region.type == "WINDOW"), None
        )
        if region is not None:
            break

    context_override["selected_objects"] = list(bpy.context.scene.objects)[0]
    context_override["area"] = area
    context_override["region"] = region
    return context_override


# TODO check if it works
def reset_blender_memory():
    for obj in bpy.data.objects:
        for mod in obj.modifiers:
            if hasattr(mod, "point_cache"):
                mod.point_cache.clear()

    for psys in bpy.data.particles:
        psys.point_cache.clear()

    for img in list(bpy.data.images):
        if img.users > 0:
            img.user_clear()
        bpy.data.images.remove(img)

    bpy.ops.outliner.orphans_purge(
        do_local_ids=True, do_linked_ids=True, do_recursive=True
    )

    bpy.ops.ed.undo_push(message="Reset undo stack")
    bpy.ops.ed.undo_history()

    gc.collect()


def measure_context_switch_time():
    if bpy.context.mode not in "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    obj = bpy.data.objects["GP_Obj_1"]
    obj.select_set(True)

    context_override = create_context()
    with bpy.context.temp_override(**context_override):

        start_time = time.time()

        if bpy.app.version < (4, 3, 0):
            bpy.ops.object.mode_set(mode="EDIT_GPENCIL")
        else:
            bpy.ops.object.mode_set(mode="EDIT")
    print("measure_context_switch_time DONE")

    return time.time() - start_time


def set_noise_modifier(obj, modifier_type: str, noise_scale: int):
    if bpy.app.version < (4, 3, 0):
        mod = obj.grease_pencil_modifiers.new(name="NOISE", type=modifier_type)
    else:
        mod = obj.modifiers.new(name="NOISE", type=modifier_type)
    mod.noise_scale = noise_scale
    print(mod.name)


def measure_modifier_apply_time(noise_scale: int = 1) -> float:
    context_override = create_context()
    context_override["mode"] = "OBJECT"
    noise_scale = noise_scale
    with bpy.context.temp_override(**context_override):
        start_time = time.time()
        print(bpy.context.mode)
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        # TODO: try to select correct active object instead
        active_obj = bpy.context.active_object
        if active_obj.type == "GPENCIL":
            modifier_type = "GP_NOISE"
        elif active_obj.type == "GREASEPENCIL":
            modifier_type = "GREASE_PENCIL_NOISE"
        else:
            raise TypeError(
                f"object has to be 'GPENCIL' or 'GREASEPENCIL', not {active_obj.type}"
            )

        set_noise_modifier(active_obj, modifier_type, noise_scale)
        if bpy.app.version < (4, 3, 0):
            bpy.ops.object.gpencil_modifier_apply(modifier="NOISE")
        else:
            bpy.ops.object.modifier_apply(modifier="NOISE")

    return time.time() - start_time


def measure_fx_apply_time() -> float:
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    context_override = create_context()
    context_override["mode"] = "OBJECT"
    with bpy.context.temp_override(**context_override):
        active_obj = bpy.context.active_object
        if active_obj.type not in ("GPENCIL", "GREASEPENCIL"):
            raise TypeError(
                f"object has to be 'GPENCIL' or 'GREASEPENCIL', not {active_obj.type}"
            )

        start_time = time.time()

        obj = bpy.context.active_object
        obj.shader_effects.new(name="BLUR", type="FX_BLUR")
        bpy.ops.object.modifier_apply(modifier="BLUR")

        return time.time() - start_time


def measure_undo_time() -> float:
    context_override = create_context()
    if bpy.app.version < (4, 3, 0):
        context_override["mode"] = "PAINT_GPENCIL"
    else:
        bpy.ops.object.mode_set(mode="PAINT_GREASE_PENCIL")

    start_time = time.time()
    with bpy.context.temp_override(**context_override):
        bpy.ops.ed.undo()
    return time.time() - start_time


def measure_save_time(filepath: str):
    start_time = time.time()
    bpy.ops.wm.save_as_mainfile(filepath=str(filepath))
    return time.time() - start_time


def measure_load_time(filepath: str) -> float:
    start_time = time.time()
    bpy.ops.wm.open_mainfile(filepath=str(filepath))
    print("measure_load_time DONE")
    return time.time() - start_time


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
    base = Path(r"C:\Users\awink\Desktop\BA\my-test")
    gp_contents_counts = count_gp_contents()
    meta_data = dict()
    meta_data["version"] = bpy.app.version_string
    meta_data["test file path"] = str(test_file_path.relative_to(base))
    meta_data["timestamp"] = test_start_time.isoformat()
    meta_data["file size in bytes"] = read_filesize(test_file_path)
    meta_data["gp objects"] = gp_contents_counts.objects
    meta_data["gp layers"] = gp_contents_counts.layers
    meta_data["gp points"] = gp_contents_counts.points
    meta_data["frame range"] = bpy.data.scenes["Scene"].frame_end
    with open(output_filepath, "w") as f:
        json.dump(meta_data, f, indent=4)


def create_test_dir(parent, folder_name):
    new_dir = parent / folder_name
    new_dir.mkdir()
    return new_dir


def test_measure_file_opening(
    result_dir: Path, file_to_open: str, monitoring_interval: int = 100
):
    test_result_dir = result_dir / "test_measure_file_opening"
    test_function = functools.partial(measure_load_time, file_to_open)
    base_test_function(
        test_result_dir,
        "load_time.txt",
        test_function,
        monitoring_interval,
    )


def test_measure_fx(result_dir: Path, monitoring_interval: int = 100):
    test_result_dir = result_dir / "test_measure_fx"
    base_test_function(
        test_result_dir,
        "fx_time.txt",
        measure_fx_apply_time,
        monitoring_interval,
    )


def test_measure_modifier(result_dir: Path, monitoring_interval: int = 100):
    test_result_dir = result_dir / "test_measure_modifier"
    base_test_function(
        test_result_dir,
        "modifier_time.txt",
        measure_modifier_apply_time,
        monitoring_interval,
    )


def test_measure_context_switch(result_dir, monitoring_interval: int = 100):
    test_result_dir = result_dir / "test_measure_context_switch"
    base_test_function(
        test_result_dir,
        "context_switch_time.txt",
        measure_context_switch_time,
        monitoring_interval,
    )


def test_measure_save(result_dir: Path, monitoring_interval: int) -> None:
    test_result_dir = result_dir / "test_measure_save"
    test_function = functools.partial(
        measure_save_time, test_result_dir / "measured_save_file.blend"
    )
    base_test_function(
        test_result_dir, "save_time.txt", test_function, monitoring_interval
    )


def test_undo_time(result_dir, monitoring_interval: int = 100):
    test_result_dir = result_dir / "test_undo_time"
    base_test_function(
        test_result_dir,
        "undo_time.txt",
        measure_undo_time,
        monitoring_interval,
    )


def base_test_function(
    result_dir: Path, result_filename: str, func: Callable, monitoring_interval: int
):
    result_dir.mkdir(exist_ok=True)
    cpu_monitor, gpu_monitor = start_cpu_gpu_monitoring(result_dir, monitoring_interval)
    result = func()
    stop_cpu_gpu_monitoring(cpu_monitor, gpu_monitor)
    with open(result_dir / result_filename, "w") as f:
        f.write(str(result))


def stop_playback(scene, other_arg):
    global play_framerange_test
    if play_framerange_test is None:
        print(bpy.app.handlers.frame_change_post)
        print()
        print(stop_playback)
    if scene.frame_current >= scene.frame_end:
        bpy.app.handlers.frame_change_post.remove(stop_playback)
        bpy.ops.screen.animation_cancel(restore_frame=False)
        play_framerange_test.stop()


def coordinate_tests_running(
    test_file: Path, result_dir: Path, test_start_time: datetime.datetime
):
    global play_framerange_test, file_loaded

    if not file_loaded:
        # TODO: check how opening file time is calculated, seems off with bigger files
        test_measure_file_opening(result_dir, test_file)
        write_metadata(test_file, test_start_time, result_dir / "metadata.json")
        file_loaded = True

    if play_framerange_test is None:
        play_framerange_test = MeasurePlayFramerange(
            result_dir=(result_dir / "test_play_framerange")
        )
        play_framerange_test.setup(stop_playback)
        play_framerange_test.start()
    elif not play_framerange_test.running:
        print("Play_framerange_test finished")
        test_measure_save(result_dir, 100)
        test_measure_context_switch(result_dir, 100)
        # TODO: undo
        # test_undo_time(result_dir, 100)
        test_measure_fx(result_dir, 100)
        test_measure_modifier(result_dir, 100)
        print("Tests finished")

        # Close file when finished
        # bpy.ops.wm.quit_blender('INVOKE_DEFAULT')
        reset_blender_memory()

        reset_testing()
        return None
    dummy_val = 2.0
    return dummy_val


# TODO: change 100ms to measure more often?
def start_measuring(test_file: Path, output_dir: Path):
    global is_a_test_running
    is_a_test_running = True
    test_start_time = datetime.datetime.now()
    logger.debug("Creating Output Directory")
    result_dir: Path = output_dir / test_start_time.strftime("%Y-%m-%d_%H%M%S")
    result_dir.mkdir(parents=True)

    bpy.app.timers.register(
        functools.partial(
            coordinate_tests_running, test_file, result_dir, test_start_time
        ),
        first_interval=2,
        persistent=True,
    )


def reset_testing():
    global play_framerange_test, file_loaded, is_a_test_running
    play_framerange_test = None
    file_loaded = False
    is_a_test_running = False


def coordinate_multiple_tests():
    if len(TEST_FILES) == 0:
        return None
    global is_a_test_running
    if not is_a_test_running:
        test_file = TEST_FILES.pop(0)
        result_directory = OUTPUT_DIR / test_file.parent.relative_to(TEST_DIR)
        start_measuring(test_file, result_directory)
    return 2.0


if __name__ == "__main__":

    bpy.app.timers.register(
        coordinate_multiple_tests,
        first_interval=2,
        persistent=True,
    )

    # test 4.2.13
    # TEST_FILE = Path(
    #   r"C:\Users\work\Documents\HdM\Bachelor\files\my-test\test-01\test-01-01\test-01-01-01\test-01-01-01-01\4.2.13\test-01-01-01-01_4.2.13 LTS.blend"
    # )
    # test 4.5
    # TEST_FILE = Path(r"C:\Users\work\Documents\HdM\Bachelor\files\my-test\test-01\test-01-01\test-01-01-01\test-01-01-01-01\4.5.2\test-01-01-01-01_4.5.2 LTS.blend")

    # result_directory = OUTPUT_DIR / TEST_FILE.parent.relative_to(TEST_DIR)
    # start_measuring(TEST_FILE, result_directory)
