from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QSlider, QCheckBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from Controlador.utils import open_window, load_settings, save_settings



class OptionsWindow(QMainWindow):
    def __init__(self, back_view_class):
        super().__init__()
        self.setWindowTitle("Options window")
        self.setGeometry(400, 100, 400, 400)
        self.back_view_class = back_view_class
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #191414")
        main_layout = QVBoxLayout(self.central_widget)

        # Load settings
        settings = load_settings()
        initial_volume = settings.get('volume', 50)
        cheats_enabled = settings.get('cheats_enabled', 0)

        slider_layout = QHBoxLayout()

        volume_label = QLabel("Volume")
        volume_label.setStyleSheet("color: #FFFFFF")
        slider_layout.addWidget(volume_label)

        # Volume Slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #1DB954;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                border: 1px solid #5c5c5c;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -7px 0;
            }
            QSlider::add-page:horizontal {
                background: #c4c4c4;
            }
            QSlider::sub-page:horizontal {
                background: #1DB954;
            }
        """)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(initial_volume)
        self.volume_slider.valueChanged.connect(self.change_volume)
        slider_layout.addWidget(self.volume_slider)

        self.value_label = QLabel(str(initial_volume))
        self.value_label.setStyleSheet("color: #FFFFFF")
        slider_layout.addWidget(self.value_label)

        main_layout.addLayout(slider_layout)

        self.cheats_checkbox = QCheckBox("Enable Cheats")
        self.cheats_checkbox.setChecked(cheats_enabled)
        self.cheats_checkbox.setStyleSheet("color: #FFFFFF")
        self.cheats_checkbox.stateChanged.connect(self.change_cheats)
        main_layout.addWidget(self.cheats_checkbox)

        button = QPushButton()
        button.setStyleSheet("background-color: #1DB954; color: #191414;")
        icon = QIcon("assets/undo.png")
        button.setIcon(icon)
        button.clicked.connect(lambda: open_window(self, self.back_view_class))
        main_layout.addWidget(button)
        
    def change_volume(self, value):
        settings = load_settings()
        self.value_label.setText(str(value))
        settings['volume'] = value
        save_settings(settings)

    def change_cheats(self, state):
        # state se repressenta con un 2 y un 0
        settings = load_settings()
        settings['cheats_enabled'] = state
        save_settings(settings)