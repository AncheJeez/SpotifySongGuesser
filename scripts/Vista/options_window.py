from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QSlider, QCheckBox, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from Controlador.utils import open_window, load_settings, save_settings, load_translations
import os
import sys


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
        button_width = 200

        # Load settings
        settings = load_settings()
        initial_volume = settings.get('volume', 50)
        cheats_enabled = settings.get('cheats_enabled', 0)
        self.lenguage = settings.get('lenguage', 'en')

        slider_layout = QHBoxLayout()

        self.volume_label = QLabel(f"{load_translations(self.lenguage,'volume')}: {initial_volume}")
        self.volume_label.setStyleSheet("color: #FFFFFF")
        slider_layout.addWidget(self.volume_label)

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

        main_layout.addLayout(slider_layout)

        # chetos
        self.cheats_checkbox = QCheckBox(load_translations(self.lenguage,"enable_cheats"))
        self.cheats_checkbox.setChecked(cheats_enabled)
        self.cheats_checkbox.setStyleSheet("color: #FFFFFF")
        self.cheats_checkbox.stateChanged.connect(self.change_cheats)
        main_layout.addWidget(self.cheats_checkbox)


        self.lenguage_layout = QHBoxLayout()

        # Lenguaje combo
        self.lenguage_label = QLabel(load_translations(self.lenguage,"lenguage"))
        self.lenguage_label.setStyleSheet("color: #FFFFFF")
        self.lenguage_layout.addWidget(self.lenguage_label)

        self.lenguage_combo = QComboBox()
        self.lenguage_combo.setStyleSheet("background-color: #1DB954; color: #191414;")
        self.lenguage_combo.addItem(load_translations(self.lenguage,"english"), "en")
        self.lenguage_combo.addItem(load_translations(self.lenguage,"spanish"), "es")
        index_language = 1 if self.lenguage == 'es' else 0
        self.lenguage_combo.setCurrentIndex(index_language)
        self.lenguage_combo.currentIndexChanged.connect(self.change_lenguage)
        self.lenguage_layout.addWidget(self.lenguage_combo)

        main_layout.addLayout(self.lenguage_layout)

        # borrar el cache y salir
        delete_button = QPushButton(load_translations(self.lenguage,'delete_cache_exit'))
        delete_button.setStyleSheet("background-color: #FF0000; color: #FFFFFF;")
        delete_button.clicked.connect(self.delete_cache_and_exit)
        main_layout.addWidget(delete_button)

        # volver atras
        button = QPushButton()
        button.setStyleSheet("background-color: #1DB954; color: #191414;")
        icon = QIcon("assets/undo.png")
        button.setIcon(icon)
        button.clicked.connect(lambda: open_window(self, self.back_view_class))
        main_layout.addWidget(button)
        
    def change_volume(self, value):
        settings = load_settings()
        self.volume_label.setText(f"{load_translations(self.lenguage,'volume')}: {value}")
        settings['volume'] = value
        save_settings(settings)

    def change_cheats(self, state):
        # state se repressenta con un 2 y un 0
        settings = load_settings()
        settings['cheats_enabled'] = state
        save_settings(settings)

    def change_lenguage(self, index):
        new_lenguage_code = self.lenguage_combo.itemData(index)
        settings = load_settings()
        settings['lenguage'] = new_lenguage_code
        save_settings(settings)

        self.volume_label.setText(f"{load_translations(new_lenguage_code,'volume')}: {settings['volume']}")
        self.cheats_checkbox.setText(load_translations(new_lenguage_code,"enable_cheats"))
        self.lenguage_label.setText(load_translations(new_lenguage_code,"lenguage"))

    def delete_cache_and_exit(self):
        cache_file = f".cache-current-user-spotify"
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print(f"Cache file {cache_file} deleted.")
        else:
            print(f"No cache file found at {cache_file}.")
        self.close()
        sys.exit()
        