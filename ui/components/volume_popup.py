from PySide6.QtWidgets import QWidget, QSlider, QVBoxLayout,QLabel
from PySide6.QtCore import Qt,Signal,QObject

class VolumePopup(QWidget):
    volume_changed = Signal(int)
    def __init__(self,parent=None):
        super().__init__(parent,Qt.Popup)

        self.setObjectName("volumePopup")

        layout = QVBoxLayout(self)

        self.volume_label = QLabel(self)
        self.volume_label.setObjectName("volumeLabel")
        self.volume_label.setText("%100")

        self.slider = QSlider(Qt.Vertical,self)
        self.slider.valueChanged.connect(self.value_changed)
        self.slider.setObjectName("volumeSlider")
        self.slider.setRange(0, 150)
        self.slider.setValue(100)

        layout.addWidget(self.volume_label,0)
        layout.addWidget(self.slider,1)


    def value_changed(self, value):
        self.volume_label.setText(f"%{value}")
        self.volume_changed.emit(value)

    

class VolumeValue(QObject):
    changed = Signal(int)

    def __init__(self, initial : int = 100):
        super().__init__()
        self._value = initial

    def set_value(self, value: int):
        if value == self._value:
            return

        self._value = value
        self.changed.emit(value)

    def get_value(self) -> int:
        return self._value