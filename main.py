from build.gui import window, playlistButton, randomSongButton, submitButton, bpmEntry, playlistEntry
from tkinter import StringVar

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
import random
import requests
import pygame
import tempfile
from urllib.parse import urlparse

playlist = None

def get_playlist_id(url):
    result = urlparse(url)
    if 'open.spotify.com' in result.netloc:
        path_parts = result.path.split('/')
        if 'playlist' in path_parts:
            playlist_id_index = path_parts.index('playlist') + 1
            if playlist_id_index < len(path_parts):
                return path_parts[playlist_id_index]
    return None

def initSpotify():
    load_dotenv()
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                                                           client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")))

    return spotify


def loadPlaylist(spotify):
    global playlist
    playlistId = get_playlist_id(playlistURL.get())
    if(playlistId != None):
        print(playlistId)
        playlist = spotify.playlist_tracks(playlistId)
    print("Couldn't load playlist")
    return None 

def getRandomTrack():
    global playlist
    if(playlist == None):
        return

    tracks = playlist['items']
    random_track = random.choice(tracks)
    preview_url = random_track['track']['preview_url']
    
    if preview_url is not None:
        # Download the audio file
        response = requests.get(preview_url)
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(response.content)
        temp_file.close()

        # Play the audio file
        pygame.mixer.music.load(temp_file.name)
        pygame.mixer.music.play()
    else:
        print("No preview available for this track")


if __name__ == '__main__':
    spotify = initSpotify()
    pygame.mixer.init()
    pygame.mixer.music.set_volume(0.05)
    playlistURL = StringVar()
    playlistEntry.config(textvariable=playlistURL)

    playlistButton.config(command=lambda: loadPlaylist(spotify))
    randomSongButton.config(command=lambda: getRandomTrack())
    window.mainloop()