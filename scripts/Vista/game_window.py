import sys
import requests
from io import BytesIO
from PIL import Image
from PySide6.QtMultimedia import QMediaPlayer
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QPushButton, QLabel, QWidget, QMessageBox, QGridLayout, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from Controlador.utils import open_window, load_settings, save_settings, censor_image, mute_player, load_translations
from Controlador.spotify_client import sp
from Vista.answer_dialog import AnswerDialog
from Vista.statistics_dialog import StatisticsDialog
#from .start_window import StartWindow
import random
import time


class GameWindow(QMainWindow):
    def __init__(self, playlist, back_view_class, user_or_defaults, fix_4_circular_import):
        super().__init__()
        self.setWindowTitle("Game window")
        self.setGeometry(400, 100, 400, 400)
        self.back_view_class = back_view_class
        self.user_or_defaults = user_or_defaults
        self.fix_4_circular_import = fix_4_circular_import
        self.start_time = time.time()
        self.total_time = 0

        # game variables
        self.playing = False
        self.playlist = playlist
        self.correct_song = None
        # estos son los intentos internos para calcular que tipo de censurado hacer
        self.img_max_attempts = 3
        self.img_attempts = self.img_max_attempts - 1
        # intentos del juego
        self.attempts = 0
        self.max_attempts = 5

        self.current_img_url = ""
        self.songs_played = 0
        self.max_songs = 10
        self.previous_volume = 50
        self.mute_state = False
        
        settings = load_settings()
        self.lenguage = settings.get('lenguage', 'en')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #191414")
        main_layout = QVBoxLayout(self.central_widget)

        self.player = QMediaPlayer()
        self.audioOutput = QAudioOutput()
        self.player.setAudioOutput(self.audioOutput)
        self.player.mediaStatusChanged.connect(self.media_status_changed)

        # Load settings
        settings = load_settings()
        volume = settings.get('volume', 50)
        self.cheats_enabled = settings.get('cheats_enabled', False)
        self.audioOutput.setVolume(volume / 100.0)

        # Label playlist name
        if playlist:
            label = QLabel(f"{load_translations(self.lenguage,'playlist')}: {playlist['name']}")
            label.setStyleSheet("color: #1DB954; font-size: 24px;")
            main_layout.addWidget(label)

        # label intentos
        self.intentos = QLabel(f"{load_translations(self.lenguage,'attempts')}: {self.max_attempts - self.attempts}/{self.max_attempts}")
        self.intentos.setStyleSheet("color: #FFFFFF; font-size: 20px;")
        main_layout.addWidget(self.intentos, alignment=Qt.AlignCenter)

        # Label to display songs left
        self.songs_left_label = QLabel(f"{load_translations(self.lenguage,'songs_left')}: {self.songs_played}/{self.max_songs}")
        self.songs_left_label.setStyleSheet("color: #FFFFFF; font-size: 18px;")
        main_layout.addWidget(self.songs_left_label, alignment=Qt.AlignCenter)

        # label de la imagen
        self.song_image_label = QLabel()
        self.song_image_label.setAlignment(Qt.AlignCenter)
        self.song_image_label.setStyleSheet("QLabel{margin-top: 20px; margin-bottom: 20px; border: 2px solid #1DB954;}")
        main_layout.addWidget(self.song_image_label, alignment=Qt.AlignCenter)

        # label que solo aparece si estan los cheats activados
        if self.cheats_enabled == 2:
            self.song_label = QLabel("")
            self.song_label.setStyleSheet("color: #FFFFFF")
            main_layout.addWidget(self.song_label, alignment=Qt.AlignCenter)
        
        # botones del juego
        buttons_layout = QGridLayout()
        self.option_buttons = []
        for i in range(4):
            row = i // 2
            col = i % 2
            button = QPushButton(f"Option {i+1}")
            button.setStyleSheet("background-color: #1DB954; color: #191414;")
            button.clicked.connect(self.check_answer)
            buttons_layout.addWidget(button, row+3, col)
            self.option_buttons.append(button)
        main_layout.addLayout(buttons_layout)

        # verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # main_layout.addItem(verticalSpacer)
        spacer_widget = QWidget()
        spacer_widget.setFixedHeight(40)
        main_layout.addWidget(spacer_widget)

        button_width = 200

        # boton mute
        self.btnMute = QPushButton()
        self.btnMute.setStyleSheet("background-color: #1DB954; color: #191414;")
        self.btnMute.setFixedWidth(button_width)
        self.btnMute.clicked.connect(lambda: self.mute_act())
        icon = QIcon("assets/volume_up.png")
        self.btnMute.setIcon(icon)
        main_layout.addWidget(self.btnMute, alignment=Qt.AlignCenter)

        # boton ir para atras
        button = QPushButton()
        button.setStyleSheet("background-color: #1DB954; color: #191414;")
        button.setFixedWidth(button_width)
        icon = QIcon("assets/undo.png")
        button.setIcon(icon)
        button.clicked.connect(lambda: self.stop_and_open_window())
        main_layout.addWidget(button, alignment=Qt.AlignCenter)

        self.songs = self.fetch_playlist_songs()
        # self.played_songs = set()
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
                    else:
                        preview_url = None

                    if preview_url is not None:
                        all_tracks.append({
                            'name': track_name,
                            'images': album_images,
                            'preview_url': preview_url
                        })

            return all_tracks

    def choose_random_song(self):
        random.shuffle(self.songs)

        # for song in self.songs:
        #     if song['name'] not in self.played_songs:
        self.correct_song = self.songs[0]['name']
        if self.cheats_enabled == 2:
            self.song_label.setText(f"{load_translations(self.lenguage,'cheat_label')}: {self.correct_song}")
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

        # añadimos el nombre para evitar q se repita
        # self.played_songs.add(song['name'])

        all_options = [song['name'] for song in self.songs[1:4]]
        all_options.append(self.correct_song)
        random.shuffle(all_options)

        for button, option in zip(self.option_buttons, all_options):
            button.setText(option)
        # esto en caso de que no haya mas de 10 canciones si se van a repetir
        # self.reset_played_songs()

    def reset_played_songs(self):
        self.played_songs.clear()

    def update_image(self, image_url):
        #REQUEST
        response = requests.get(image_url)
        image_data = response.content
        img = Image.open(BytesIO(image_data))

        #CENSOR
        uncensored_parts =  self.img_max_attempts - self.img_attempts
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
        self.img_attempts -= 1
        sender_button = self.sender()
        selected_option = sender_button.text()

        if selected_option == self.correct_song:
            self.answer_dialog = AnswerDialog(f"{load_translations(self.lenguage,'correct')}",1, self)
            self.answer_dialog.exec_()

            self.songs_played += 1
            self.img_attempts = self.img_max_attempts - 1
            self.songs_left_label.setText(f"{load_translations(self.lenguage,'songs_left')} {self.songs_played}/{self.max_songs}")
            self.player.stop()
            if self.songs_played >= self.max_songs:
                self.end_game()
            else:
                self.choose_random_song()
            for button in self.option_buttons:
                if button != sender_button:
                    button.setEnabled(True)
                    button.setStyleSheet("background-color: #1DB954; color: #191414")
        else:
            self.attempts+=1
            self.intentos.setText(f"{load_translations(self.lenguage,'attempts')}: {self.max_attempts - self.attempts}/{self.max_attempts}")
            self.answer_dialog = AnswerDialog(f"{load_translations(self.lenguage,'incorrect')}",2, self)
            self.answer_dialog.exec_()
            sender_button.setEnabled(False)
            sender_button.setStyleSheet("background-color: #FF0000; color: #FFFFFF")
            self.update_image(self.current_img_url)

        if self.attempts >= self.max_attempts:
            for button in self.option_buttons:
                button.setEnabled(True)
                button.setStyleSheet("background-color: #1DB954; color: #191414")
            self.end_game()
    
    def media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.player.setPosition(0)
            self.player.play()

    def mute_act(self):
        mute_player(self)
        icon = QIcon("assets/volume_up.png") if self.mute_state else QIcon("assets/volume_off.png")
        self.btnMute.setIcon(icon)
        self.mute_state = not self.mute_state

    def end_game(self):
        self.total_time = time.time() - self.start_time
        if self.songs_played >= self.max_songs:
            self.answer_dialog = AnswerDialog(f"{load_translations(self.lenguage,'good_end')}",3, self)
            self.answer_dialog.exec_()
        else:
            self.answer_dialog = AnswerDialog(f"{load_translations(self.lenguage,'bad_end')}",2, self)
            self.answer_dialog.exec_()
        dialog = StatisticsDialog(self.songs_played, self.attempts, self.total_time)
        dialog.exec_()


        self.reset_game()
    
    def reset_game(self):
        self.start_time = time.time()
        self.total_time = 0
        self.attempts = 0
        self.img_attempts = self.img_max_attempts - 1
        self.songs_played = 0
        self.songs_left_label.setText(f"Songs Left: {self.songs_played}/{self.max_songs}")
        self.intentos.setText(f"{load_translations(self.lenguage,'attempts')}: {self.max_attempts - self.attempts}/{self.max_attempts}")
        self.choose_random_song()