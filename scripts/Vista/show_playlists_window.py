from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from Controlador.utils import open_window, list_of_defaults, load_settings, load_translations
from .game_window import GameWindow
from Controlador.spotify_client import sp
import random
import requests


class ShowPlayListsWindow(QMainWindow):
    def __init__(self,back_view_class, user_or_defaults):
        super().__init__()
        self.setWindowTitle("Show playlists")
        self.setGeometry(400, 100, 400, 400)
        self.playing = False
        self.back_view_class = back_view_class
        self.user_or_defaults = user_or_defaults

        settings = load_settings()
        lenguage = settings.get('lenguage', 'en')
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #191414")
        
        layout = QVBoxLayout(self.central_widget)

        texto = f"{load_translations(lenguage,'user_playlists')}" if user_or_defaults else f"{load_translations(lenguage,'spotify_playlists')}"
        label = QLabel(texto)
        label.setStyleSheet("color: #1DB954; font-size: 15px")
        layout.addWidget(label)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("color: #FFFFFF")
        layout.addWidget(self.list_widget)

        self.play_button = QPushButton(f"{load_translations(lenguage,'play_with_selected')}")
        self.play_button.setStyleSheet("""QPushButton {
                                            background-color: #1DB954;
                                            color: #191414;
                                        }
                                        QPushButton:disabled {
                                            background-color: #146b32;
                                            color: #191414;
                                        }
                                       """)
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.play_with_selected_playlist)
        layout.addWidget(self.play_button)

        button = QPushButton()
        button.setStyleSheet("background-color: #1DB954; color: #191414;")
        icon = QIcon("assets/undo.png")
        button.setIcon(icon)
        button.clicked.connect(lambda: open_window(self, self.back_view_class))
        layout.addWidget(button)

        self.load_playlists()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
    def load_playlists(self):

        if(self.user_or_defaults):
            #USUARIO
            playlists = self.fetch_user_playlists()
        else:
            #DEFAULTS
            playlists = self.fetch_default_playlists()

        for index, playlist in enumerate(playlists):
            image_url = playlist['images'][0]['url'] if playlist['images'] else None
            if image_url:
                image_data = requests.get(image_url).content
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                icon = QIcon(pixmap)
            else:
                icon = QIcon()

            item = QListWidgetItem(icon, playlist['name'])
            item.setData(Qt.UserRole, playlist)
            self.list_widget.addItem(item)

        self.list_widget.itemClicked.connect(self.enable_play_button)
        
    def fetch_user_playlists(self):
        user_playlists = sp.current_user_playlists(limit=20)
        playlists = []
        for playlist in user_playlists['items']:
            playlists.append({
                'id': playlist['id'],
                'name': playlist['name'],
                'images': playlist['images'],
                'external_urls': playlist['external_urls']
            })
        return playlists
    
    def fetch_default_playlists(self):
        playlists = []
        for playlist_name, playlist_id in list_of_defaults.items():
            playlist_details = sp.playlist(playlist_id, fields="name,images,external_urls")
            playlists.append({
                'id': playlist_id,
                'name': playlist_details['name'],
                'images': playlist_details['images'],
                'external_urls': playlist_details['external_urls']
            })
        return playlists

    def enable_play_button(self):
        self.play_button.setEnabled(True)

    def play_with_selected_playlist(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            playlist_data = selected_items[0].data(Qt.UserRole)
            open_window(self, GameWindow, playlist_data, ShowPlayListsWindow, self.user_or_defaults, self.back_view_class)
        else:
            open_window(self, GameWindow, None, ShowPlayListsWindow, self.user_or_defaults, self.back_view_class)
