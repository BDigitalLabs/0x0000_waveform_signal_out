import queue
import threading
import numpy as np
import soundfile
import sounddevice as sd

from ui.components.volume_popup import VolumeValue

class AudioEngine:
    def __init__(self, volume_value: VolumeValue):
        self.volume_value = volume_value
        self.volume_value.changed.connect(self.on_volume_changed)
        self.current_volume = 100

        self.lock = threading.Lock()

        self.processed_samples = 0
        self.music_path = ""
        self.is_playing = False
        self.block_size = 2048
        self.sample_rate = None
        self.channels = None
        self.audio_streamer = None
        self.stream = None
        
        self.visualizer_queue = queue.Queue(maxsize=10)
        self.current_amplitude = 0.0

    def on_volume_changed(self, value: int):
        self.current_volume = value

    def load_file(self, file_path: str) -> int:
        self.cleanup()
        
        with self.lock:
            self.music_path = file_path
            info = soundfile.info(self.music_path)
            self.sample_rate = info.samplerate
            self.channels = info.channels
            self.audio_streamer = soundfile.blocks(self.music_path, blocksize=self.block_size, always_2d=True)
        
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            blocksize=self.block_size,
            callback=self.audio_callback
        )
        self.stream.start()
        return info.frames // self.sample_rate

    def audio_callback(self, outdata, frames, time, status):
        if not self.is_playing:
            outdata.fill(0)
            return

        try:
            with self.lock:
                if self.audio_streamer is None:
                    raise StopIteration
                data_block = next(self.audio_streamer)

            volume_factor = self.current_volume / 100.0
            data_block = data_block * volume_factor 

            self.processed_samples += len(data_block)
            self.current_amplitude = np.sqrt(np.mean(data_block**2))

            if len(data_block) < frames:
                outdata[:len(data_block)] = data_block
                outdata[len(data_block):].fill(0)
                self.is_playing = False
            else:
                outdata[:] = data_block
                
            if self.visualizer_queue.full():
                try:
                    self.visualizer_queue.get_nowait()
                except queue.Empty:
                    pass
            self.visualizer_queue.put(data_block[:, 0])
            
        except StopIteration:
            outdata.fill(0)
            self.is_playing = False

    def play(self):
        if not self.music_path:
            return
            
        if self.stream is None:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.block_size,
                callback=self.audio_callback
            )
            self.stream.start()
            
        self.is_playing = True

    def pause(self):
        self.is_playing = False

    def seek_to_second(self, seconds):
        if not self.music_path or self.sample_rate is None:
            return
        
        target_sample = int(seconds * self.sample_rate)
        self.processed_samples = target_sample
        
        was_playing = self.is_playing
        if was_playing:
            self.is_playing = False
            
        with self.lock:
            try:
                self.audio_streamer = soundfile.blocks(
                    self.music_path, 
                    blocksize=self.block_size, 
                    start=target_sample, 
                    always_2d=True
                )
            except Exception as e:
                print(f"Seek streamer error: {e}")
            
        if was_playing:
            self.is_playing = True

    def cleanup(self):
        self.is_playing = False
        self.processed_samples = 0
        self.current_amplitude = 0
        
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None
            
        with self.lock:
            if self.music_path:
                try:
                    self.audio_streamer = soundfile.blocks(self.music_path, blocksize=self.block_size, always_2d=True)
                except Exception:
                    self.audio_streamer = None
            else:
                self.audio_streamer = None