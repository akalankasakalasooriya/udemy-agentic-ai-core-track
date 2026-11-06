import platform
import shutil
import subprocess
from pathlib import Path


def cpu_brand():
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        return ""
    return ""


def retrieve_system_info():
    compiler = shutil.which("g++") or shutil.which("clang++") or ""
    version = ""
    if compiler:
        out = subprocess.check_output(
            [compiler, "--version"], text=True, stderr=subprocess.DEVNULL
        )
        version = out.splitlines()[0]
    return {
        "system": platform.system(),
        "machine": platform.machine(),
        "cpu": cpu_brand(),
        "compiler": compiler,
        "compiler_version": version,
    }


def default_commands(directory):
    directory = Path(directory)
    compiler = shutil.which("g++") or shutil.which("clang++")
    if not compiler:
        return [], []
    binary = directory / "main"
    compile_command = [
        compiler,
        "-std=c++17",
        "-O3",
        "-march=native",
        str(directory / "main.cpp"),
        "-o",
        str(binary),
    ]
    return compile_command, [str(binary)]
