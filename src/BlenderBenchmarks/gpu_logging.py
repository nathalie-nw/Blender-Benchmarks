import subprocess


class GPULogging:
    query = "--query-gpu=timestamp,pstate,temperature.gpu,utilization.gpu,memory.free,memory.used"

    def __init__(self, logfile_path, delay):
        self.process = None
        self.logfile = None
        self.logfile_path = logfile_path
        self.delay = delay
        with open(logfile_path, "w") as _:
            pass

    def start(self):
        if self.process is not None or self.logfile is not None:
            raise RuntimeError("Can't start logging if already started")
        self.logfile = open(self.logfile_path, "a")
        self.process = subprocess.Popen(
            ["nvidia-smi", self.query, "--format=csv", f"--loop-ms={self.delay}"],
            stdout=self.logfile,
        )

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            self.process.wait(1)
        if self.logfile is not None:
            self.logfile.close()

    def __del__(self):
        self.stop()
