import sys
import requests
from PySide6.QtWidgets import QListWidget, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QListWidgetItem
from PySide6.QtGui import QPixmap, QIcon

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

class LogInWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log in")
        self.setGeometry(400, 100, 400, 200)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        
        label = QLabel("Log in window")
        layout.addWidget(label)
        
        button = QPushButton("Show Playlists")
        button.clicked.connect(self.open_second_window)
        layout.addWidget(button)
        
    def open_second_window(self):
        self.second_window = ShowPlayListsWindow()
        self.second_window.show()
        self.close()


class ShowPlayListsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Show playlists")
        self.setGeometry(400, 100, 400, 400)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        #self.central_widget.setStyleSheet("background-color: #333")
        
        layout = QVBoxLayout(self.central_widget)
        
        label = QLabel("Playlists from logged user")
        layout.addWidget(label)

        list_widget = QListWidget()
        layout.addWidget(list_widget)

        button = QPushButton("Play with this PlayList")
        #button.clicked.connect(self.open_second_window)
        layout.addWidget(button)

        button = QPushButton("Go back")
        button.clicked.connect(self.open_second_window)
        layout.addWidget(button)

        for track in top_tracks['items']:
            # Get the URL of the album cover image
            image_url = track['album']['images'][0]['url']
            # Download the image data
            image_data = requests.get(image_url).content
            # Create a QPixmap object from the image data
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            # Create a QIcon object from the QPixmap
            icon = QIcon(pixmap)
            # Create a QListWidgetItem with the icon and track name
            item = QListWidgetItem(icon, track['name'])
            # Set the size hint for the item to give more space for the icon
            #item.setSizeHint(item.sizeHint())  # Increase width by 50 pixels
            list_widget.addItem(item)

        
    def open_second_window(self):
        self.second_window = LogInWindow()
        self.second_window.show()
        self.close()
