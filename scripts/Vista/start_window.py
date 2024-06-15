from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from .show_playlists_window import ShowPlayListsWindow
from .options_window import OptionsWindow
from Controlador.utils import open_window, load_settings, load_translations
from Controlador.spotify_client import fetch_user_profile
import requests


class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Start Window")
        self.setGeometry(400, 100, 400, 200)

        user_name, user_image_url = fetch_user_profile()
        settings = load_settings()
        lenguage = settings.get('lenguage', 'en')
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #191414")
        
        main_layout = QVBoxLayout(self.central_widget)

        btnOptions = QPushButton("")
        btnOptions.clicked.connect(lambda: open_window(self, OptionsWindow, StartWindow))
        btnOptions.setStyleSheet("background-color: #1DB954; color: #191414;")
        icon = QIcon("assets/settings.png")
        btnOptions.setIcon(icon)
        btnOptions.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        main_layout.addWidget(btnOptions, alignment=Qt.AlignRight | Qt.AlignTop)

        # Nombre de usuario
        self.user_name_label = QLabel(f"{load_translations(lenguage,'welcome')}, {user_name}!")
        self.user_name_label.setStyleSheet("color: #1DB954; font-size: 20px")
        self.user_name_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.user_name_label)

        # Imagen
        if user_image_url:
            image_data = requests.get(user_image_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.user_image_label = QLabel()
            self.user_image_label.setPixmap(pixmap)
            self.user_image_label.setAlignment(Qt.AlignCenter)
            self.user_image_label.setStyleSheet("""
                border: 2px solid #1DB954;
                border-radius: 10px;
                padding: 5px;
            """)
            self.user_image_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
            main_layout.addWidget(self.user_image_label, alignment=Qt.AlignCenter)
        
        # Label
        label = QLabel(f"{load_translations(lenguage,'choose_way')}")
        label.setStyleSheet("color: #1DB954; padding-bottom: 20px")
        label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(label)

        button_width = 200

        # Boton playlists dadas de base
        btnDefaultPlay = QPushButton(f"{load_translations(lenguage,'spotify_playlists')}")
        btnDefaultPlay.clicked.connect(lambda: open_window(self, ShowPlayListsWindow, StartWindow, False))
        btnDefaultPlay.setStyleSheet("background-color: #1DB954; color: #191414;")
        btnDefaultPlay.setFixedWidth(button_width)
        main_layout.addWidget(btnDefaultPlay, alignment=Qt.AlignCenter)
        
        # Boton playlists del usuario
        btnPlaylists = QPushButton(f"{load_translations(lenguage,'user_playlists')}")
        btnPlaylists.clicked.connect(lambda: open_window(self, ShowPlayListsWindow, StartWindow, True))
        btnPlaylists.setStyleSheet("background-color: #1DB954; color: #191414;")
        btnPlaylists.setFixedWidth(button_width)
        main_layout.addWidget(btnPlaylists, alignment=Qt.AlignCenter)