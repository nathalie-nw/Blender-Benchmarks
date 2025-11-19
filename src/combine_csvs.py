import csv
import json
from pathlib import Path
from typing import Literal

DIRECTORY = Path(r"")


def read_time(path: Path) -> float:
    with open(path) as f:
        return float(f.read().strip())


def combine_test_time(input_dir: Path, output_file: Path):
    rows = []
    for path in input_dir.rglob("metadata.json"):
        with open(path, "r") as f:
            row = json.load(f)
        row["context_switch_time"] = read_time(
            path.parent / "test_measure_context_switch" / "context_switch_time.txt"
        )
        row["load_time"] = read_time(
            path.parent / "test_measure_file_opening" / "load_time.txt"
        )
        row["fx_time"] = read_time(path.parent / "test_measure_fx" / "fx_time.txt")
        row["modifier_time"] = read_time(
            path.parent / "test_measure_modifier" / "modifier_time.txt"
        )
        row["save_time"] = read_time(
            path.parent / "test_measure_save" / "save_time.txt"
        )
        row["play_time"] = read_time(
            path.parent / "test_play_framerange" / "play_time.txt"
        )

        rows.append(row)

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, rows[0].keys(), escapechar=";")
        writer.writeheader()
        writer.writerows(rows)
    pass


def combine_test_csvs(
    input_dir: Path, output_file: Path, data_type: Literal["cpu", "gpu"]
):
    input_files = list(input_dir.glob(f"**/{data_type}.csv"))
    lines = []
    for i, path in enumerate(input_files):
        print(f"At file {i+1}/{len(input_files)}", end="\r")
        with open(path) as f:
            reader = csv.DictReader(f)
            metadata_path = path.parent.parent / "metadata.json"
            if not metadata_path.exists():
                continue  # skip files which don't have metadata
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            for line in reader:
                if data_type == "gpu" and line[" memory.free [MiB]"] is not None:
                    line[" memory.free [MiB]"] = (
                        line[" memory.free [MiB]"].replace("MiB", "").strip()
                    )
                    line[" memory.used [MiB]"] = (
                        line[" memory.used [MiB]"].replace("MiB", "").strip()
                    )
                line["blender_version"] = metadata["version"]
                line["test_case"] = path.parent.name
                line["test"] = path.parent.parent.parent.parent.name
                line["test file path"] = metadata["test file path"]
                line["timestamp"] = metadata["timestamp"]
                line["file size in bytes"] = metadata["file size in bytes"]
                line["gp objects"] = metadata["gp objects"]
                line["gp layers"] = metadata["gp layers"]
                line["gp points"] = metadata["gp points"]
                line["frame range"] = metadata["frame range"]
                lines.append(line)
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, lines[0].keys(), escapechar=";")
        writer.writeheader()
        writer.writerows(lines)
    print()


INPUT_DIR = Path(r"C:\Users\awink\Desktop\BA\my-results")

combine_test_csvs(
    INPUT_DIR,
    Path(r"C:\Users\awink\Desktop\BA\my-results\cpu_combined.csv"),
    "cpu",
)
combine_test_csvs(
    INPUT_DIR,
    Path(r"C:\Users\awink\Desktop\BA\my-results\gpu_combined.csv"),
    "gpu",
)

combine_test_time(
    INPUT_DIR, Path(r"C:\Users\awink\Desktop\BA\my-results\test_times_combined.csv")
)
