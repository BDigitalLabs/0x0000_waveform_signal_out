import os
import subprocess
from PySide6.QtCore import QObject, Signal, Slot
from services.cache_manager import CacheManager

class AudioConverterWorker(QObject):
    done = Signal(str, str) 
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self.cache_manager = CacheManager()

    @Slot(str)
    def convert_to_wav(self, input_file: str):
        try:
            music_name = os.path.basename(input_file)
            output_file = self.cache_manager.get_output_path(music_name)

            if os.path.exists(output_file):
                self.done.emit(output_file, music_name)
                return

            subprocess_kwargs = {
                "check": True,
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL
            }
            if os.name == "nt":
                subprocess_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            subprocess.run([
                "ffmpeg",
                "-y",
                "-i", input_file,
                "-acodec", "pcm_s16le",
                output_file
            ], **subprocess_kwargs)

            self.done.emit(output_file, music_name)

        except Exception as e:
            self.error.emit(str(e))