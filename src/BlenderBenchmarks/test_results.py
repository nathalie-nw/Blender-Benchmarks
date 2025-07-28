import csv
from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass
class TestResults:
    timestamp: datetime
    filepath: str
    loadtime: float
    filesize: int

    def write(self, filepath):
        with open(filepath, "a", newline="") as logfile:
            writer = csv.DictWriter(
                logfile, delimiter=";", fieldnames=asdict(self).keys()
            )
            writer.writerow(asdict(self))
