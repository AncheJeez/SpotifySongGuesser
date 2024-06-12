from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QIcon, QPixmap
from .show_playlists_window import ShowPlayListsWindow
from .options_window import OptionsWindow
from Controlador.utils import open_window
from Controlador.spotify_client import fetch_user_profile
import requests


class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log in")
        self.setGeometry(400, 100, 400, 200)

        user_name, user_image_url = fetch_user_profile()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #191414")
        
        layout = QVBoxLayout(self.central_widget)

        self.user_name_label = QLabel(f"Welcome, {user_name}!")
        self.user_name_label.setStyleSheet("color: #FFFFFF")
        layout.addWidget(self.user_name_label)

        if user_image_url:
            image_data = requests.get(user_image_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.user_image_label = QLabel()
            self.user_image_label.setPixmap(pixmap)
            layout.addWidget(self.user_image_label)
        
        label = QLabel("Choose a way of playing")
        label.setStyleSheet("color: #FFFFFF")
        layout.addWidget(label)

        btnDefaultPlay = QPushButton("Spotify playlists")
        btnDefaultPlay.clicked.connect(lambda: open_window(self, ShowPlayListsWindow, StartWindow, False))
        btnDefaultPlay.setStyleSheet("background-color: #1DB954; color: #191414;")
        layout.addWidget(btnDefaultPlay)
        
        btnPlaylists = QPushButton("User's playlists")
        btnPlaylists.clicked.connect(lambda: open_window(self, ShowPlayListsWindow, StartWindow, True))
        btnPlaylists.setStyleSheet("background-color: #1DB954; color: #191414;")
        layout.addWidget(btnPlaylists)

        btnOptions = QPushButton("")
        btnOptions.clicked.connect(lambda: open_window(self, OptionsWindow, StartWindow))
        btnOptions.setStyleSheet("background-color: #1DB954; color: #191414;")
        icon = QIcon("assets/settings.png")
        btnOptions.setIcon(icon)
        layout.addWidget(btnOptions)
