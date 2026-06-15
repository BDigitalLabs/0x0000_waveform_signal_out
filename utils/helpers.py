from os.path import join,abspath,dirname
from pathlib import Path
from shutil import which
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return join(sys._MEIPASS, relative_path)

    project_root = Path(dirname(abspath(__file__))).parent

    
    return join(project_root, relative_path)

def has_ffmpeg():
    return which("ffmpeg") is not None