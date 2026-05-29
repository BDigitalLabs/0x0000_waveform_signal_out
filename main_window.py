import os,sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QPushButton, QSlider, QFileDialog, QMessageBox, QProgressBar
)
from PySide6.QtGui import QColor, QPen,QIcon,QFont,QFontDatabase
from PySide6.QtCore import Qt, QTimer, QPointF, QSize
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

from audio_engine import AudioEngine


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    
    proje_kok_dizini = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(proje_kok_dizini, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ====== Variables ======
        self.audio_engine = AudioEngine()
        self.is_dragging = False
        
        self.play_icon = QIcon(resource_path("assets/play_button_icon.png"))
        self.pause_icon = QIcon(resource_path("assets/pause_button_icon.png"))
        self.stop_icon = QIcon(resource_path("assets/stop_button_icon.png"))
        
        time_label_font_id = QFontDatabase.addApplicationFont(resource_path("assets/ShareTechMono-Regular.ttf"))
        if time_label_font_id != -1:
            time_label_font_family = QFontDatabase.applicationFontFamilies(time_label_font_id)[0]
        else:
            time_label_font_family = "Monospace"

        music_name_label_font_id = QFontDatabase.addApplicationFont(resource_path("assets/NotoSansMono-Regular.ttf"))
        if music_name_label_font_id != -1:
            music_name_label_font_family = QFontDatabase.applicationFontFamilies(music_name_label_font_id)[0]
        else:
            music_name_label_font_family = "Sans-Serif"

        self.colors = {
            "BACKGROUND": "#000000",
            "PANEL_BACKGROUND": "#000000",
            "SLIDER_TRACK_BACKGROUND":"#505050",
            "BUTTON_BACKGROUND": "#505050",
            "BUTTON_PRESSED":"#383838",
            "BUTTON_HOVER": "#5A5A5A",
            "BUTTON_BORDER": "#3A3A3A",
            "BUTTON_HIGHLIGHT":"rgba(255, 255, 255, 0.25)",
            "BUTTON_SHADOW":"#151515",
            "HOVER_BACKGROUND": "#29292e", 
            "TEXT": "#e1e1e6",         
            "ACCENT": "#00a8ff",
            "BORDER": "#29292e",
            "LINE": "#e1e1e6"
        }

        # ====== Chart Setup ======
        self.series = QLineSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.legend().hide()
        
        self.axis_x = QValueAxis()
        self.axis_x.setRange(0, self.audio_engine.block_size)
        self.axis_x.setVisible(False)
        
        self.axis_y = QValueAxis()
        self.axis_y.setRange(-1.0, 1.0)
        self.axis_y.setVisible(False)
        
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_player_ui)
        
        # ====== Window Settings ======
        self.setWindowTitle("0x0000_waveform_signal_out")
        self.resize(600, 400)
        self.setMinimumSize(600, 400)

        # ====== Menu Bar ======
        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu("&File")
        open_action = menu_file.addAction("&Open...\tCtrl+O")
        open_action.triggered.connect(self.on_open) 
        menu_file.addSeparator()
        exit_action = menu_file.addAction("Exit")
        exit_action.triggered.connect(self.on_exit)

        menu_help = menu_bar.addMenu("&Help")
        about_action = menu_help.addAction("About")
        about_action.triggered.connect(self.on_about)

        # ====== Main UI ======
        main_panel = QWidget()
        main_panel.setObjectName("mainPanel")
        self.setCentralWidget(main_panel)
        main_panel_layout = QVBoxLayout(main_panel)
        main_panel_layout.setContentsMargins(0, 0, 0, 0)
        main_panel_layout.setSpacing(0)

        track_info_panel = QWidget()
        track_info_panel.setObjectName("trackInfoPanel")
        track_info_panel.setFixedHeight(40)
        track_info_layout = QHBoxLayout(track_info_panel)
        track_info_layout.setContentsMargins(5, 0, 0, 0)

        self.time_label = QLabel("00:00:00:000")
        self.time_label.setObjectName("timeLabel")
        self.time_label.setFont(QFont(time_label_font_family, 14))

        label_line = QFrame()
        label_line.setObjectName("label_line")
        label_line.setFrameShape(QFrame.Shape.VLine)
        label_line.setFrameShadow(QFrame.Shadow.Sunken)

        self.music_name_label = QLabel("No track loaded")
        self.music_name_label.setObjectName("musicNameLabel")
        self.music_name_label.setFont(QFont(music_name_label_font_family,10))
        track_info_layout.addWidget(self.time_label, 0)
        track_info_layout.addWidget(label_line, 0)
        track_info_layout.addWidget(self.music_name_label, 1)

        line1 = QFrame()
        line1.setObjectName("line1")
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)

        self.waveform_chart_view = QChartView(self.chart)

        self.volume_meter = QProgressBar()
        self.volume_meter.setRange(0, 100)
        self.volume_meter.setTextVisible(False) 
        self.volume_meter.setFixedHeight(15)

        line2 = QFrame()
        line2.setObjectName("line2")
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)

        control_panel = QWidget()
        control_panel.setObjectName("controlPanel")
        
        control_panel_layout = QHBoxLayout(control_panel)
        control_panel_layout.setContentsMargins(5,5,5,5)
        
        self.play_button = QPushButton()
        self.stop_button = QPushButton()

        self.play_button.setObjectName("playButton")
        self.stop_button.setObjectName("stopButton")

        self.play_button.setFixedHeight(40)
        self.stop_button.setFixedHeight(40)

        self.play_button.setFixedWidth(40)
        self.stop_button.setFixedWidth(40)

        self.play_button.setIcon(self.play_icon)
        self.play_button.setIconSize(QSize(32, 32))

        self.stop_button.setIcon(self.stop_icon)
        self.stop_button.setIconSize(QSize(32, 32))

        self.play_button.clicked.connect(self.on_toggle_playback)
        self.stop_button.clicked.connect(self.on_stop)

        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setObjectName("seekSlider")
        self.seek_slider.setRange(0, 100)
        self.seek_slider.sliderPressed.connect(self.on_slider_pressed)
        self.seek_slider.sliderReleased.connect(self.on_slider_released)

        control_panel_layout.addWidget(self.play_button, 0)
        control_panel_layout.addWidget(self.stop_button, 0)
        control_panel_layout.addWidget(self.seek_slider, 1)

        
        main_panel_layout.addWidget(track_info_panel, 0)
        main_panel_layout.addWidget(line1, 0)
        main_panel_layout.addWidget(self.waveform_chart_view, 1)
        main_panel_layout.addWidget(self.volume_meter, 0)
        main_panel_layout.addWidget(line2, 0)
        main_panel_layout.addWidget(control_panel, 0)

        self.apply_theme(resource_path("main_window.qss"))

    def apply_theme(self, qss_file_name):
        
        try:
            with open(qss_file_name, "r", encoding="utf-8") as f:
                qss_data = f.read()
                
                for key, value in self.colors.items():
                    qss_data = qss_data.replace(f"{{{key}}}", value)
                    
                pack_assets_path = resource_path("assets/").replace("\\", "/")
                qss_data = qss_data.replace("assets/", pack_assets_path)
                
                self.setStyleSheet(qss_data)
                
        except FileNotFoundError:
            QMessageBox.critical(self,"Error",f"File not found: {qss_file_name}")
        except Exception as e:
            QMessageBox.critical(self,"Error",f"Error: {e}")
            
        pen = QPen()
        pen.setColor(QColor(self.colors["ACCENT"]))
        pen.setWidth(2)
        self.series.setPen(pen)
            
        self.chart.setBackgroundBrush(QColor(self.colors["PANEL_BACKGROUND"]))
        self.waveform_chart_view.setBackgroundBrush(QColor(self.colors["PANEL_BACKGROUND"]))


    def on_slider_pressed(self):

        self.is_dragging = True

    def on_slider_released(self):
        self.is_dragging = False
        target_seconds = self.seek_slider.value()
        self.audio_engine.seek_to_second(target_seconds)

    def update_time_label(self):
        if not self.audio_engine.sample_rate: return

        total_seconds = self.audio_engine.processed_samples / self.audio_engine.sample_rate
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds % 1) * 1000)
        self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}:{milliseconds:03d}")

    def update_seek_slider(self):
        if not self.is_dragging and self.audio_engine.sample_rate:
            total_seconds = self.audio_engine.processed_samples / self.audio_engine.sample_rate
            self.seek_slider.setValue(int(total_seconds))

    def update_player_ui(self):
        if not self.audio_engine.is_playing:
            self.on_stop()
            return

        self.update_time_label()
        self.update_seek_slider()
        
        meter_value = int(self.audio_engine.current_amplitude * 150)
        self.volume_meter.setValue(min(max(meter_value, 0), 100))
        
        latest_data = None
        while not self.audio_engine.visualizer_queue.empty():
            latest_data = self.audio_engine.visualizer_queue.get()

        if latest_data is not None:
            points = [QPointF(i, value) for i, value in enumerate(latest_data)]
            self.series.replace(points)


    def on_toggle_playback(self):
        if not self.audio_engine.music_path:
            return

        if self.audio_engine.is_playing:
            self.audio_engine.pause() 
            self.play_button.setIcon(self.play_icon)
            self.timer.stop()
        else:
            self.audio_engine.play() 
            self.play_button.setIcon(self.pause_icon)
            self.timer.start(33)

    def on_stop(self):
        self.audio_engine.cleanup()
        self.play_button.setIcon(self.play_icon)
        self.timer.stop()
        self.series.clear()
        self.volume_meter.setValue(0)
        self.seek_slider.setValue(0)
        self.time_label.setText("00:00:00.000")

    def on_open(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose an audio file", "", "Audio Files (*.wav *.ogg *.flac *.aiff *.caf)"
        )
        if not file_path: return

        self.on_stop()
        music_name = os.path.basename(file_path)
        if len(music_name) > 25:
            music_name = music_name[:25] + "..."
        self.music_name_label.setText(music_name)
        
        try:
            duration = self.audio_engine.load_file(file_path)
            self.seek_slider.setRange(0, duration)

        except Exception as e:
            QMessageBox.critical(self,"Error",f"Error: {e}")

    def closeEvent(self, event):
        self.on_stop()
        event.accept()

    def on_exit(self):
        self.close()

    def on_about(self):
        title = "About Music Player"
        text = """
        <h3>0x0000_waveform_signal_out v1.0.0</h3>
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
