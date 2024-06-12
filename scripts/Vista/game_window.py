import sys
import requests
from io import BytesIO
from PIL import Image
from PySide6.QtMultimedia import QMediaPlayer
from PySide6 import QtCore
from PySide6.QtWidgets import QMainWindow, QPushButton, QLabel, QWidget, QMessageBox, QGridLayout
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from Controlador.utils import open_window, load_settings, save_settings, censor_image, mute_player
from Controlador.spotify_client import sp
#from .start_window import StartWindow
import random


class GameWindow(QMainWindow):
    def __init__(self, playlist, back_view_class, user_or_defaults, fix_4_circular_import):
        super().__init__()
        self.setWindowTitle("Game window")
        self.setGeometry(400, 100, 400, 400)
        self.playing = False
        self.playlist = playlist
        self.correct_song = None
        self.max_attempts = 3
        self.attempts = self.max_attempts - 1
        self.current_img_url = ""
        self.previous_volume = 50
        self.mute_state = False
        self.back_view_class = back_view_class
        self.user_or_defaults = user_or_defaults
        self.fix_4_circular_import = fix_4_circular_import
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #191414")
        # layout = QVBoxLayout(self.central_widget)
        layout = QGridLayout(self.central_widget)

        self.player = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.player.setAudioOutput(self.audioOutput)
        self.player.mediaStatusChanged.connect(self.media_status_changed)

        # Load settings
        settings = load_settings()
        volume = settings.get('volume', 50)
        self.cheats_enabled = settings.get('cheats_enabled', False)
        self.audioOutput.setVolume(volume / 100.0)

        if playlist:
            label = QLabel(f"{playlist['name']}")
            label.setStyleSheet("color: #FFFFFF")
            layout.addWidget(label, 0, 0, 1, 2)

        self.intentos = QLabel(f"Attempts: {self.attempts-2}")
        self.intentos.setStyleSheet("color: #FFFFFF")
        layout.addWidget(self.intentos, 0, 2, 1, 2)
        
        if self.cheats_enabled == 2:
            self.song_label = QLabel("")
            self.song_label.setStyleSheet("color: #FFFFFF")
            layout.addWidget(self.song_label, 1, 0, 1, 2)

        self.song_image_label = QLabel()
        layout.addWidget(self.song_image_label, 2, 0, 1, 2)
        
        self.option_buttons = []
        for i in range(4):
            row = i // 2
            col = i % 2
            button = QPushButton(f"Option {i+1}")
            button.setStyleSheet("background-color: #1DB954; color: #191414;")
            button.clicked.connect(self.check_answer)
            # layout.addWidget(button, row+2, col)
            layout.addWidget(button, row+3, col)
            self.option_buttons.append(button)

        button = QPushButton()
        button.setStyleSheet("background-color: #1DB954; color: #191414;")
        icon = QIcon("assets/undo.png")
        button.setIcon(icon)
        button.clicked.connect(lambda: self.stop_and_open_window())
        layout.addWidget(button)

        self.btnMute = QPushButton()
        self.btnMute.setStyleSheet("background-color: #1DB954; color: #191414;")
        self.btnMute.clicked.connect(lambda: self.mute_act())
        icon = QIcon("assets/volume_up.png")
        self.btnMute.setIcon(icon)
        layout.addWidget(self.btnMute)

        self.songs = self.fetch_playlist_songs()
        self.choose_random_song()

    def fetch_playlist_songs(self):
        if self.playlist:
            playlist_id = self.playlist['id']
            total_tracks = sp.playlist(playlist_id)['tracks']['total']
            all_tracks = []

            # Spotify limita 100 canciones por llamada
            for offset in range(0, total_tracks, 100):
                playlist_tracks = sp.playlist_tracks(playlist_id, offset=offset)
                for item in playlist_tracks['items']:
                    track = item.get('track')
                    if track is not None:
                        track_name = track.get('name', 'Unknown')
                        album_images = track.get('album', {}).get('images', [])
                        preview_url = track.get('preview_url')

                    if preview_url is not None:
                        all_tracks.append({
                            'name': track_name,
                            'images': album_images,
                            'preview_url': preview_url
                        })

            return all_tracks

    def choose_random_song(self):
        random.shuffle(self.songs)
        self.correct_song = self.songs[0]['name']
        if self.cheats_enabled == 2:
            self.song_label.setText(f"Guess the song: {self.correct_song}")
        self.preview_url = self.songs[0]['preview_url']

        #IMAGEN
        images = self.songs[0]['images']
        image_url = images[0]['url'] if images else None
        if image_url:
            self.current_img_url = image_url
            self.update_image(image_url)
        
        #CANCION
        if self.preview_url:
            url = QUrl(self.preview_url)
            self.player.setSource(url)
            self.player.play()

        all_options = [song['name'] for song in self.songs[1:4]]
        all_options.append(self.correct_song)
        random.shuffle(all_options)

        for button, option in zip(self.option_buttons, all_options):
            button.setText(option)

    def update_image(self, image_url):
        #REQUEST
        response = requests.get(image_url)
        image_data = response.content
        img = Image.open(BytesIO(image_data))

        #CENSOR
        uncensored_parts =  self.max_attempts - self.attempts
        if uncensored_parts < 0:
            uncensored_parts = 0

        censored_img = censor_image(img, uncensored_parts)
        censored_img_bytes = BytesIO()
        censored_img.save(censored_img_bytes, format="JPEG")
        censored_img_bytes.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(censored_img_bytes.read())

        #SCALE DOWN
        scaled_pixmap = pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
        self.song_image_label.setPixmap(scaled_pixmap)

    def stop_and_open_window(self):
        # FIX AQUI
        self.player.stop()
        open_window(self, self.back_view_class, self.fix_4_circular_import, self.user_or_defaults)

    def check_answer(self):
        self.attempts -= 1
        sender_button = self.sender()
        selected_option = sender_button.text()

        if selected_option == self.correct_song:
            QMessageBox.information(self, "Correct!", "Congratulations! You guessed the correct song.")
            self.attempts = self.max_attempts - 1
            self.intentos.setText(f"Attempts: {abs(self.attempts - 2)}")
            self.player.stop()
            self.choose_random_song()
            for button in self.option_buttons:
                if button != sender_button:
                    button.setStyleSheet("background-color: #1DB954; color: #191414")
        else:
            QMessageBox.warning(self, "Incorrect", "Sorry, that's not the correct song. Please try again.")
            self.intentos.setText(f"Attempts: {abs(self.attempts - 2)}")
            sender_button.setStyleSheet("background-color: #FF0000; color: #FFFFFF")
            self.update_image(self.current_img_url)
    
    def media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.player.setPosition(0)
            self.player.play()

    def mute_act(self):
        mute_player(self)
        icon = QIcon("assets/volume_up.png") if self.mute_state else QIcon("assets/volume_off.png")
        self.btnMute.setIcon(icon)
        self.mute_state = not self.mute_state
