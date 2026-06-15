from shutil import rmtree
from os.path import join
from tempfile import mkdtemp
from atexit import register

class CacheManager:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or mkdtemp()
        self.cache = {}
        register(self.cleanup)

    def cleanup(self):
        rmtree(self.base_dir, ignore_errors=True)

    def get_output_path(self, key):
        if key in self.cache:
            return self.cache[key]

        path = join(self.base_dir, f"{key}.wav")
        self.cache[key] = path
        return path