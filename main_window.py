import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QPushButton, QSlider, QFileDialog, QMessageBox, QProgressBar
)
from PySide6.QtGui import QColor, QPen,QIcon,QFont,QFontDatabase
from PySide6.QtCore import Qt, QTimer, QPointF, QSize,QThread,Signal
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

from core.audio_engine import AudioEngine
from core.audio_converter_worker import AudioConverterWorker
from ui.components.volume_popup import VolumePopup, VolumeValue
from ui.main_window_ui import Ui_MainWindow
from utils.helpers import has_ffmpeg,resource_path

class MainWindow(QMainWindow):
    convert_requested = Signal(str)
    def __init__(self):
        super().__init__()
        
        # ====== Variables and Engines ======
        volume_value = VolumeValue()
        self.audio_engine = AudioEngine(volume_value)
        self.is_dragging = False

        # ====== UI Setup ======
        self.ui = Ui_MainWindow()
        self.ui.setup_ui(self, self.audio_engine.block_size)
        
        # Windows Settings
        self.setWindowTitle("0x0000_waveform_signal_out")
        self.resize(600, 400)
        self.setMinimumSize(600, 400)

        # ====== Thread Setup ======
        self.converter_thread = QThread()
        self.converter_worker = AudioConverterWorker()
        self.converter_worker.moveToThread(self.converter_thread)
        self.converter_worker.done.connect(self.on_convert_finished)
        self.converter_worker.error.connect(self.on_error)
        self.convert_requested.connect(self.converter_worker.convert_to_wav)
        self.converter_thread.start()

        # Logic Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_player_ui)

        # ====== Signals & Slots ======
        self.ui.open_action.triggered.connect(self.on_open)
        self.ui.exit_action.triggered.connect(self.on_exit)
        self.ui.about_action.triggered.connect(self.on_about)
        
        self.ui.volume_popup.volume_changed.connect(self.on_volume_changed)
        self.ui.volume_popup.slider.valueChanged.connect(volume_value.set_value)
        
        self.ui.play_button.clicked.connect(self.on_toggle_playback)
        self.ui.stop_button.clicked.connect(self.on_stop)
        self.ui.volume_button.clicked.connect(self.show_volume)
        
        self.ui.seek_slider.sliderPressed.connect(self.on_slider_pressed)
        self.ui.seek_slider.sliderReleased.connect(self.on_slider_released)

    def on_volume_changed(self, value):
        if value == 0:
            self.ui.volume_button.setIcon(self.ui.volume_icon_0)
        elif value <= 25:
            self.ui.volume_button.setIcon(self.ui.volume_icon_25)
        elif value <= 75:
            self.ui.volume_button.setIcon(self.ui.volume_icon_50)
        else:
            self.ui.volume_button.setIcon(self.ui.volume_icon_100)

    def show_volume(self):
        pos = self.ui.volume_button.mapToGlobal(self.ui.volume_button.rect().topLeft())
        pos.setY(pos.y() - self.ui.volume_popup.height())
        self.ui.volume_popup.move(pos)
        self.ui.volume_popup.show()

    def on_slider_pressed(self):
        self.is_dragging = True

    def on_slider_released(self):
        self.is_dragging = False
        target_seconds = self.ui.seek_slider.value()
        self.audio_engine.seek_to_second(target_seconds)

    def update_time_label(self):
        if not self.audio_engine.sample_rate: return

        total_seconds = self.audio_engine.processed_samples / self.audio_engine.sample_rate
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds % 1) * 1000)
        self.ui.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}:{milliseconds:03d}")

    def update_seek_slider(self):
        if not self.is_dragging and self.audio_engine.sample_rate:
            total_seconds = self.audio_engine.processed_samples / self.audio_engine.sample_rate
            self.ui.seek_slider.setValue(int(total_seconds))

    def update_player_ui(self):
        if not self.audio_engine.is_playing:
            self.on_stop()
            return

        self.update_time_label()
        self.update_seek_slider()

        meter_value = int((self.audio_engine.current_amplitude / 1.5) * 100)
        self.ui.volume_meter.setValue(min(max(meter_value, 0), 100))
        
        latest_data = None
        while not self.audio_engine.visualizer_queue.empty():
            latest_data = self.audio_engine.visualizer_queue.get()

        if latest_data is not None:
            points = [QPointF(i, value) for i, value in enumerate(latest_data)]
            self.ui.series.replace(points)

    def on_toggle_playback(self):
        if not self.audio_engine.music_path:
            return

        if self.audio_engine.is_playing:
            self.audio_engine.pause() 
            self.ui.play_button.setIcon(self.ui.play_icon)
            self.timer.stop()
        else:
            self.audio_engine.play() 
            self.ui.play_button.setIcon(self.ui.pause_icon)
            self.timer.start(33)

    def on_stop(self):
        self.audio_engine.cleanup()
        self.ui.play_button.setIcon(self.ui.play_icon)
        self.timer.stop()
        self.ui.series.clear()
        self.ui.volume_meter.setValue(0)
        self.ui.seek_slider.setValue(0)
        self.ui.time_label.setText("00:00:00.000")

    def on_convert_finished(self, file_path, music_name):
        try:
            duration = self.audio_engine.load_file(file_path)
            self.ui.seek_slider.setRange(0, duration)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {e}")
            self.ui.progress_bar.hide()
            self.ui.open_action.setEnabled(True)
            return

        if len(music_name) > 25:
            music_name = music_name[:25] + "..."
        self.ui.music_name_label.setText(music_name)
        self.ui.progress_bar.hide()
        self.ui.open_action.setEnabled(True)

    def on_error(self, e):
        QMessageBox.critical(self, "Error", f"Error: {e}")
        self.ui.progress_bar.hide()
        self.ui.open_action.setEnabled(True)

    def on_open(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose an audio file", "",
            "Audio Files (*.wav *.ogg *.flac *.aiff *.caf *.mp3 *.opus *.m4a *.alac)"
        )
        if not file_path:
            return

        self.ui.open_action.setEnabled(False)
        self.on_stop()
        self.ui.progress_bar.show()

        ffmpeg_formats = (".mp3", ".m4a", ".opus", ".alac")
        _, extension = os.path.splitext(file_path)

        if extension.lower() in ffmpeg_formats and not has_ffmpeg():
            QMessageBox.warning(self, "FFmpeg Required", "This audio format requires FFmpeg.")
            self.ui.progress_bar.hide()
            self.ui.open_action.setEnabled(True)
            return

        if extension.lower() in ffmpeg_formats:
            self.convert_requested.emit(file_path)
        else:
            music_name = os.path.basename(file_path)
            duration = self.audio_engine.load_file(file_path)
            self.ui.music_name_label.setText(music_name[:25] + "..." if len(music_name) > 25 else music_name)
            self.ui.seek_slider.setRange(0, duration)
            self.ui.progress_bar.hide()
            self.ui.open_action.setEnabled(True)

        

    

    def closeEvent(self, event):
        self.converter_thread.quit()
        self.converter_thread.wait()
        self.on_stop()
        event.accept()

    def on_exit(self):
        self.close()

    def on_about(self):
        title = "About Music Player"
        text = """
        <h3>0x0000_waveform_signal_out v1.1.0</h3>
        <p>Copyright &copy; 2026 Berke</p>
        <p>An open-source desktop music player application.</p>
        <hr>
        <p><b>License Information:</b><br>
        This program is licensed under the <b>GNU GPLv3 (or later)</b>. 
        The source code is fully accessible and open to the community.</p>
    
        <p><b>Third-Party Components:</b><br>
        This application utilizes the <b>PySide6 (Qt)</b> library, which is dynamically linked 
        and covered under the <b>GNU LGPLv3</b>. Users are granted the right to modify the 
        Qt library and relink the application accordingly under LGPLv3 terms.</p>
    
        <p>Other integrated libraries (NumPy, sounddevice, soundfile) and the Python license 
        are subject to their respective open-source licenses, which are located in the 
        <code>third_party_licenses/</code> directory of this project.</p>
        """
        QMessageBox.about(self,title,text)
