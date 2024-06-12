import json
import os
import random
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter

list_of_defaults = {
    "top_50": "37i9dQZEVXbMDoHDwVN2tF",
    "top_today": "37i9dQZF1DXcBWIGoYBM5M",
    "rock_classic": "37i9dQZF1DWXRqgorJj26U",
    "viva_latino": "37i9dQZF1DX10zKzsJ2jva",
    "all_out_2000": "37i9dQZF1DX4o1oenSJRJd",
    "all_out_80s": "37i9dQZF1DX4UtSsGT1Sbe",
    "under_ground_dance_&_electronica": "3gW3MRRNkjlnbrwC8LVE9H",
    "2024_classroom_songs": "31ymdYCITDnZRtkKzP3Itp",
    "kitsune_musique_essential": "0cc8YMQWsSzODyTpdVB6mI",
    "warehouse_party":"37i9dQZF1DX5hHfOi73rY3",
    "altar":"37i9dQZF1DXa71eg5j9dKZ",
    "new_music_weekly_monstercar":"4kw9kdjzx1UmyWvpysl0y2"
}

def open_window(current_window, window_class, *args):
    new_window = window_class(*args)
    new_window.show()
    current_window.close()

def close_window(window):
    if window is not None:
        window.close()

def load_settings(filename='settings.json'):
    if not os.path.exists(filename):
        return {"volume": 50}

    with open(filename, 'r') as file:
        return json.load(file)

def save_settings(settings, filename='settings.json'):
    with open(filename, 'w') as file:
        json.dump(settings, file, indent=4)

def censor_image(img, uncensored_parts):
    width, height = img.size
    censored_img = img.copy()
    draw = ImageDraw.Draw(censored_img)
    
    parts = [
        (0, 0, width // 2, height // 2),  # Top-left
        (width // 2, 0, width, height // 2),  # Top-right
        (0, height // 2, width // 2, height),  # Bottom-left
        (width // 2, height // 2, width, height)  # Bottom-right
    ]
    random.shuffle(parts)
    average_color = get_average_color(censored_img)
    
    for i in range(4):
        if i >= uncensored_parts:
            draw.rectangle(parts[i], fill=average_color)
    
    return censored_img

def get_average_color(img):
    img_array = np.array(img)
    # Compute the average color across all channels
    average_color = np.mean(img_array, axis=(0, 1))
    # lo pasamos a int
    average_color = tuple(average_color.astype(int))
    return average_color

def mute_player(self):
    if(self.mute_state):
        self.audioOutput.setVolume(self.previous_volume)
    else:
        self.previous_volume = self.audioOutput.volume()
        self.audioOutput.setVolume(0)