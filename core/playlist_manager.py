# core/playlist_manager.py

class PlaylistManager:
    def __init__(self):
        self.music_list = []      
        self.current_index = 0

    def get_current_music_path(self) -> str|None:
        # Checked self.music_list empty or full
        if not self.music_list:
            return None
        return self.music_list[self.current_index]
    
    def clear_music_list(self):
        self.music_list.clear()

    def get_music_path(self, index: int) -> str | None:
        if 0 <= index < len(self.music_list):
            return self.music_list[index]
        return None

    def set_current_index(self, index: int):
        if 0 <= index < len(self.music_list):
            self.current_index = index

    def add_music(self, music_path: str):
        print(f"Debug-1: {music_path}")
        self.music_list.append(music_path)

    def add_music_paths(self, music_paths: list):
        print(f"Debug-2: {music_paths}")
        self.music_list.extend(music_paths)
        

    def next_music(self) -> str | None:
        if not self.music_list:
            return None
        
        self.current_index = (self.current_index + 1) % len(self.music_list)
        return self.music_list[self.current_index]
