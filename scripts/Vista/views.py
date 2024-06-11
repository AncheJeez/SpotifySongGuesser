import sys
import requests
from io import BytesIO
from PIL import Image
from PySide6.QtMultimedia import (QtAudio, QAudioFormat,
                                  QAudioSink, QMediaDevices, QMediaPlayer)
from PySide6 import QtCore
from PySide6.QtWidgets import (QListWidget, QMainWindow, QPushButton, 
                               QLabel, QVBoxLayout, QWidget, QListWidgetItem, 
                               QMessageBox, QGridLayout, QSlider, QHBoxLayout)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from Controlador.utils import list_of_defaults, open_window, load_settings, save_settings, censor_image, mute_player
import random

from dotenv import load_dotenv
import os
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

import spotipy
import spotipy.util as util

REDIRECT_URI = 'http://localhost:3000'
USERNAME = 'Test name'

token = util.prompt_for_user_token(USERNAME, scope='user-library-read,user-top-read', client_id=client_id, client_secret=client_secret, redirect_uri=REDIRECT_URI)
sp = spotipy.Spotify(auth=token)

top_tracks = sp.current_user_top_tracks(limit=20)

class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log in")
        self.setGeometry(400, 100, 400, 200)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #191414")
        
        layout = QVBoxLayout(self.central_widget)
        
        label = QLabel("Choose a way of playing")
        label.setStyleSheet("color: #FFFFFF")
        layout.addWidget(label)

        btnDefaultPlay = QPushButton("Spotify playlists")
        btnDefaultPlay.clicked.connect(lambda: open_window(self, ShowPlayListsWindow, False))
        btnDefaultPlay.setStyleSheet("background-color: #1DB954; color: #191414;")
        layout.addWidget(btnDefaultPlay)
        
        btnPlaylists = QPushButton("User's playlists")
        btnPlaylists.clicked.connect(lambda: open_window(self, ShowPlayListsWindow, True))
        btnPlaylists.setStyleSheet("background-color: #1DB954; color: #191414;")
        layout.addWidget(btnPlaylists)

        btnOptions = QPushButton("")
        btnOptions.clicked.connect(lambda: open_window(self, OptionsWindow, StartWindow))
        btnOptions.setStyleSheet("background-color: #1DB954; color: #191414;")
        icon = QIcon("assets/settings.png")
        btnOptions.setIcon(icon)
        layout.addWidget(btnOptions)

class ShowPlayListsWindow(QMainWindow):
    def __init__(self, user_or_defaults):
        super().__init__()
        self.setWindowTitle("Show playlists")
        self.setGeometry(400, 100, 400, 400)
        self.playing = False
        self.user_or_defaults = user_or_defaults
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: #191414")
        
        layout = QVBoxLayout(self.central_widget)

        texto = "Playlists from logged user" if user_or_defaults else "Playlists from Top Spotify"
        label = QLabel(texto)
        label.setStyleSheet("color: #FFFFFF")
        layout.addWidget(label)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("color: #FFFFFF")
        layout.addWidget(self.list_widget)

        self.play_button = QPushButton("Play with this PlayList")
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
        button.clicked.connect(lambda: open_window(self, StartWindow))
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
            open_window(self, GameWindow, playlist_data, ShowPlayListsWindow, self.user_or_defaults)
        else:
            open_window(self, GameWindow, None, ShowPlayListsWindow, self.user_or_defaults)

class GameWindow(QMainWindow):
    def __init__(self, playlist, back_view_class, user_or_defaults):
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
        self.audioOutput.setVolume(volume / 100.0)

        if playlist:
            label = QLabel(f"{playlist['name']}")
            label.setStyleSheet("color: #FFFFFF")
            layout.addWidget(label, 0, 0, 1, 2)

        self.intentos = QLabel(f"Attempts: {self.attempts-2}")
        self.intentos.setStyleSheet("color: #FFFFFF")
        layout.addWidget(self.intentos, 0, 2, 1, 2)
        
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
                for track in playlist_tracks['items']:
                    track_name = track['track']['name']
                    album_images = track['track']['album']['images']
                    preview_url = track['track']['preview_url']

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
        self.player.stop()
        open_window(self, self.back_view_class, self.user_or_defaults)

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
        else:
            QMessageBox.warning(self, "Incorrect", "Sorry, that's not the correct song. Please try again.")
            self.intentos.setText(f"Attempts: {abs(self.attempts - 2)}")
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
