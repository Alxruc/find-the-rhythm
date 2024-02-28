from build.gui import *
from tkinter import StringVar

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
import random
import requests
import pygame
import tempfile
import essentia.standard as es
import math
from urllib.parse import urlparse

playlist = None
current_audio_file = None
artistAndTitle = " - "

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
        print(f'Grabbing playlist id {playlistId}')
        try:
            playlist = spotify.playlist_tracks(playlistId)
            print("Playlist loaded")
        except:
            playlist = None
            print("Couldn't load playlist, make sure the URL is correct and the playlist is public")

def getRandomTrack():
    global playlist
    global current_audio_file
    global artistAndTitle

    if(playlist is None):
        print("No playlist loaded")
        return
    
    if(len(playlist['items']) == 0):
        print("No tracks left in playlist, either load a new one or refresh the current one")
        return
    
    # Hide label in case it is still visible from last guess
    check_label.config(fg=backgroundColor)
    
    # If there's a currently playing track, delete its file
    if current_audio_file is not None:
        os.unlink(current_audio_file)
        current_audio_file = None

    tracks = playlist['items']
    random_track = random.choice(tracks)
    playlist['items'].remove(random_track)
    preview_url = random_track['track']['preview_url']

    # Getting the artist(s) and song title to display, truncating it to a max of 35 characters
    songPlayingString = ""
    for i in range(0,len(random_track['track']['artists'])):
        songPlayingString = songPlayingString + random_track['track']['artists'][i]['name'] + ", "

    songPlayingString = songPlayingString[:-2] + " - "  # Remove the last comma and space
    songPlayingString = songPlayingString + random_track['track']['name']

    if len(songPlayingString) > 35:
        songPlayingString = songPlayingString[:35] + '...'
    songPlaying_label.config(text=songPlayingString)
    
    if preview_url is not None:
        # Download the audio file
        response = requests.get(preview_url)
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(response.content)
        temp_file.close()

        current_audio_file = temp_file.name

        # Play the audio file
        pygame.mixer.music.load(current_audio_file)
        pygame.mixer.music.play()
    else:
        print(songPlayingString + " has no preview available, trying a different song" + "\n")
        getRandomTrack()
    

def getTempo():
    global current_audio_file
    if(current_audio_file is None):
        return 0
    
    audio = es.MonoLoader(filename=current_audio_file)()
    rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
    bpm, _, _, _, _ = rhythm_extractor(audio)
    return bpm

def checkTempo():
    guess = bpmGuess.get()

    if(len(guess) == 0):
        print("Please enter a (whole) number")
        return
    
    try:
        guess = int(guess)
    except (TypeError, ValueError):
        print("Please enter a (whole) number")
        return
    
    guess = int(guess)
    tempo = math.ceil(getTempo())
    
    if(tempo == guess):
        check_label.config(fg='#1DB954', text=f'Correct, the bpm was: {tempo}')
        return
    
    if(guess - 1 <= tempo <= guess + 1):
        check_label.config(fg='#FFFF00', text=f'Almost, the bpm was: {tempo}')
        return

    if(guess - 2 <= tempo <= guess + 2):
        check_label.config(fg='#FFA500', text=f'Close, the bpm was: {tempo}')
        return
    
    check_label.config(fg='#FF0000', text=f'Wrong, the bpm was: {tempo}')
    return


def cleanup():
    global current_audio_file

    # If there's a currently playing track, delete its file
    if current_audio_file is not None:
        os.unlink(current_audio_file)
        current_audio_file = None


if __name__ == '__main__':
    try:
        spotify = initSpotify()
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.05)
        playlistURL = StringVar()
        bpmGuess = StringVar()
        playlistEntry.config(textvariable=playlistURL)
        bpmEntry.config(textvariable=bpmGuess)

        playlistButton.config(command=lambda: loadPlaylist(spotify))
        randomSongButton.config(command=lambda: getRandomTrack())
        submitButton.config(command=lambda: checkTempo())
        window.mainloop()
    finally:
        cleanup()