# spotify_client.py
import os
from dotenv import load_dotenv
import spotipy
import spotipy.util as util

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

REDIRECT_URI = 'http://localhost:3000'
USERNAME = 'Test name'

def get_spotify_client():
    token = util.prompt_for_user_token(USERNAME, scope='user-library-read,user-top-read,user-read-private', client_id=client_id, client_secret=client_secret, redirect_uri=REDIRECT_URI)
    return spotipy.Spotify(auth=token)

sp = get_spotify_client()

def get_top_tracks(limit=20):
    return sp.current_user_top_tracks(limit=limit)

def fetch_user_profile():
    try:
        user_profile = sp.current_user()
        user_name = user_profile.get('display_name', 'Unknown User')
        user_images = user_profile.get('images', [])
        user_image_url = user_images[0]['url'] if user_images else None
        return user_name, user_image_url
    except spotipy.exceptions.SpotifyException as e:
        print(f"Error: {e}")
        if e.http_status == 403:
            print("Access denied. Please check your permissions and ensure the user is registered.")
        return None, None