from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QPushButton, QSlider, QMessageBox, QProgressBar,
    QListWidget
)
from PySide6.QtGui import QColor, QPen, QIcon, QFont, QFontDatabase
from PySide6.QtCore import Qt, QSize
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

from ui.components.volume_popup import VolumePopup
from utils.helpers import resource_path

class Ui_MainWindow:
    def setup_ui(self, window, block_size):
        # ====== Icons and Variables ======
        self.volume_icon_0 = QIcon(resource_path("assets/volume_button_icon_0.png"))
        self.volume_icon_25 = QIcon(resource_path("assets/volume_button_icon_25.png"))
        self.volume_icon_50 = QIcon(resource_path("assets/volume_button_icon_50.png"))
        self.volume_icon_100 = QIcon(resource_path("assets/volume_button_icon_100.png"))

        self.play_icon = QIcon(resource_path("assets/play_button_icon.png"))
        self.pause_icon = QIcon(resource_path("assets/pause_button_icon.png"))
        self.stop_icon = QIcon(resource_path("assets/stop_button_icon.png"))

        self.repeat_one_icon = QIcon(resource_path("assets/repeat_one_icon.png"))
        self.repeat_all_icon = QIcon(resource_path("assets/repeat_all_icon.png"))
        self.repeat_off_icon = QIcon(resource_path("assets/repeat_off_icon.png"))

        
        
        time_label_font_id = QFontDatabase.addApplicationFont(resource_path("assets/ShareTechMono-Regular.ttf"))
        time_label_font_family = QFontDatabase.applicationFontFamilies(time_label_font_id)[0] if time_label_font_id != -1 else "Monospace"

        music_name_label_font_id = QFontDatabase.addApplicationFont(resource_path("assets/NotoSansMono-Regular.ttf"))
        music_name_label_font_family = QFontDatabase.applicationFontFamilies(music_name_label_font_id)[0] if music_name_label_font_id != -1 else "Sans-Serif"

        self.colors = {
            "BACKGROUND": "#000000",
            "PANEL_BACKGROUND": "#000000",
            "SLIDER_TRACK_BACKGROUND":"#505050",
            "CONTROL_BUTTON_BACKGROUND": "#505050",
            "CONTROL_BUTTON_PRESSED":"#383838",
            "CONTROL_BUTTON_HOVER": "#5A5A5A",
            "CONTROL_BUTTON_BORDER": "#3A3A3A",
            "CONTROL_BUTTON_HIGHLIGHT":"rgba(255, 255, 255, 0.25)",
            "CONTROL_BUTTON_SHADOW":"#151515",
            "REPEAT_MODE_BUTTON_BACKGROUND":"#000000",
            "REPEAT_MODE_BUTTON_HOVER":"#101010",
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
        self.axis_x.setRange(0, block_size)
        self.axis_x.setVisible(False)
        
        self.axis_y = QValueAxis()
        self.axis_y.setRange(-1.0, 1.0)
        self.axis_y.setVisible(False)
        
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)

        # ====== Menu Bar ======
        menu_bar = window.menuBar() 
        menu_file = menu_bar.addMenu("&File")
        self.open_action = menu_file.addAction("Open")
        self.open_folder_action = menu_file.addAction("Open Folder")
        menu_file.addSeparator()
        self.toggle_recursive_action = menu_file.addAction("Toggle Recursive")
        self.toggle_recursive_action.setCheckable(True)
        menu_file.addSeparator()
        self.exit_action = menu_file.addAction("Exit")

        menu_view = menu_bar.addMenu("&View")
        self.toggle_playlist_action = menu_view.addAction("Toggle Playlist")
        self.toggle_playlist_action.setCheckable(True)

        menu_help = menu_bar.addMenu("&Help")
        self.about_action = menu_help.addAction("About")

        # ====== Central Container ======
        central_container = QWidget()
        window.setCentralWidget(central_container)
        central_layout = QHBoxLayout(central_container)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        # ====== Main Panel ======
        main_panel = QWidget()
        main_panel.setObjectName("mainPanel")
        main_panel_layout = QVBoxLayout(main_panel)
        main_panel_layout.setContentsMargins(0, 0, 0, 0)
        main_panel_layout.setSpacing(0)

        # ====== Track Info Panel ======
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
        self.music_name_label.setFont(QFont(music_name_label_font_family, 10))
        track_info_layout.addWidget(self.time_label, 0)
        track_info_layout.addWidget(label_line, 0)
        track_info_layout.addWidget(self.music_name_label, 1)

        line1 = QFrame()
        line1.setObjectName("line1")
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)


        # ====== Waveform Chart, Volume Meter, Progress Bar ======
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()

        self.waveform_chart_view = QChartView(self.chart)

        self.volume_meter = QProgressBar()
        self.volume_meter.setObjectName("volumeMeter")
        self.volume_meter.setRange(0, 100)
        self.volume_meter.setTextVisible(False) 
        self.volume_meter.setFixedHeight(15)

        line2 = QFrame()
        line2.setObjectName("line2")
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)

        # ====== Control Panel ======
        control_panel = QWidget()
        control_panel.setObjectName("controlPanel")
        control_panel_layout = QHBoxLayout(control_panel)
        control_panel_layout.setContentsMargins(5, 5, 5, 5)
        
        self.play_button = QPushButton(control_panel)
        self.stop_button = QPushButton(control_panel)
        self.volume_button = QPushButton(control_panel)
        self.volume_popup = VolumePopup(control_panel)

        self.play_button.setObjectName("playButton")
        self.stop_button.setObjectName("stopButton")
        self.volume_button.setObjectName("volumeButton")

        self.play_button.setFixedHeight(40)
        self.stop_button.setFixedHeight(40)
        self.volume_button.setFixedHeight(40)

        self.play_button.setFixedWidth(40)
        self.stop_button.setFixedWidth(40)
        self.volume_button.setFixedWidth(40)

        self.play_button.setIcon(self.play_icon)
        self.play_button.setIconSize(QSize(32, 32))

        self.stop_button.setIcon(self.stop_icon)
        self.stop_button.setIconSize(QSize(32, 32))

        self.volume_button.setIcon(self.volume_icon_100)
        self.volume_button.setIconSize(QSize(32, 32))

        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setObjectName("seekSlider")
        self.seek_slider.setRange(0, 100)

        control_panel_layout.addWidget(self.play_button, 0)
        control_panel_layout.addWidget(self.stop_button, 0)
        control_panel_layout.addWidget(self.volume_button, 0)
        control_panel_layout.addWidget(self.seek_slider, 1)
        
        main_panel_layout.addWidget(track_info_panel, 0)
        main_panel_layout.addWidget(line1, 0)
        main_panel_layout.addWidget(self.progress_bar, 0)
        main_panel_layout.addWidget(self.waveform_chart_view, 1)
        main_panel_layout.addWidget(self.volume_meter, 0)
        main_panel_layout.addWidget(line2, 0)
        main_panel_layout.addWidget(control_panel, 0)


        # ====== Playlist Panel ======
        self.playlist_panel = QWidget()
        self.playlist_panel.setObjectName("playlistPanel")
        self.playlist_panel.setFixedWidth(200)
        self.playlist_panel.hide()  # Closed in starting

        playlist_panel_layout = QVBoxLayout(self.playlist_panel)
        playlist_panel_layout.setContentsMargins(1, 1, 1, 1)
        playlist_panel_layout.setSpacing(0)


        self.repeat_mode_button=QPushButton()
        self.repeat_mode_button.setObjectName("repeatModeButton")
        self.repeat_mode_button.setFixedHeight(30)
        self.repeat_mode_button.setIcon(self.repeat_off_icon)
        self.repeat_mode_button.setIconSize(QSize(25,25))

        line3 = QFrame()
        line3.setObjectName("line3")
        line3.setFrameShape(QFrame.Shape.HLine)
        line3.setFrameShadow(QFrame.Shadow.Sunken)


        self.playlist_widget = QListWidget()
        self.playlist_widget.setObjectName("playlistWidget")
        self.playlist_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        playlist_panel_layout.addWidget(self.repeat_mode_button,0)
        playlist_panel_layout.addWidget(line3,0)
        playlist_panel_layout.addWidget(self.playlist_widget,1)


        central_layout.addWidget(self.playlist_panel, 0)
        central_layout.addWidget(main_panel, 1)

        self.apply_theme(window, resource_path("ui/styles/main_window.qss"))

    def apply_theme(self, window, qss_file_name):
        try:
            with open(qss_file_name, "r", encoding="utf-8") as f:
                qss_data = f.read()
                
                for key, value in self.colors.items():
                    qss_data = qss_data.replace(f"{{{key}}}", value)
                    
                pack_assets_path = resource_path("assets/").replace("\\", "/")
                qss_data = qss_data.replace("assets/", pack_assets_path)
                
                window.setStyleSheet(qss_data)
                
        except FileNotFoundError:
            QMessageBox.critical(window, "Error", f"File not found: {qss_file_name}")
        except Exception as e:
            QMessageBox.critical(window, "Error", f"Error: {e}")
            
        pen = QPen()
        pen.setColor(QColor(self.colors["ACCENT"]))
        pen.setWidth(2)
        self.series.setPen(pen)
            
        self.chart.setBackgroundBrush(QColor(self.colors["PANEL_BACKGROUND"]))
        self.waveform_chart_view.setBackgroundBrush(QColor(self.colors["PANEL_BACKGROUND"]))