import os
import subprocess
from PySide6.QtCore import QObject, Signal, Slot
from services.cache_manager import CacheManager

class AudioConverterWorker(QObject):
    done = Signal(str, str,bool) 
    error = Signal(str,bool)

    def __init__(self):
        super().__init__()
        self.cache_manager = CacheManager()

    @Slot(str,bool)
    def convert_to_flac(self, input_file: str,for_playlist: bool):
        try:
            music_name = os.path.basename(input_file)
            output_file = self.cache_manager.get_output_path(input_file)

            if os.path.exists(output_file):
                self.done.emit(output_file, music_name,for_playlist)
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
                "-c:a", "flac",
                output_file
            ], **subprocess_kwargs)

            self.done.emit(output_file, music_name,for_playlist)

        except Exception as e:
            self.error.emit(str(e),for_playlist)