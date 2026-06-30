from shutil import rmtree
from os.path import join,basename
from tempfile import mkdtemp
from atexit import register
from hashlib import sha256

class CacheManager:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or mkdtemp()
        self.cache = {}
        register(self.cleanup)

    def cleanup(self):
        rmtree(self.base_dir, ignore_errors=True)

    def get_file_hash(self,file_path) -> str:
        h = sha256()
        with open(file_path,"rb") as file:
            for part in iter(lambda: file.read(8192), b""):
                h.update(part)
        return h.hexdigest()


    def get_output_path(self, input_key: str) -> str:
        
        file_hash = self.get_file_hash(input_key)
        if file_hash in self.cache:
            return self.cache[file_hash]

        path = join(self.base_dir, f"{basename(input_key)}.flac")
        self.cache[file_hash] = path
        return path