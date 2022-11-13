import pandas as pd

from dotenv import load_dotenv
import os

load_dotenv()

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def spotify_login(cid, secret):
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret) 
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

cid = os.getenv("Client_ID")
secret = os.getenv("Client_Secret")

sp = spotify_login(cid, secret)

def get_albums(_id_):
    artists_id = 'spotify:artist:' + _id_
                            
    results = sp.artist_albums(artists_id, album_type='album')

    albums = results['items']
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
        
    album_names = [] 
    album_ids = []
    for album in albums:
        album_names.append(album['name'])
        album_ids.append(album['id'])

    album_df = pd.DataFrame({"Name": album_names,
                            "ID": album_ids},
                        columns = ["Name", "ID"])

    album_df.drop_duplicates(subset="Name", keep = 'first', inplace=True)
    
    return album_df

def get_artist_tracks(album_df):
    def get_tracks_from_album(album_id):
        results = sp.album_tracks(album_id)
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        for track in tracks:
            track_names.append(track['name'])
            track_ids.append(track['id'])
    
    track_names = [] 
    track_ids = []
    for album_id in album_df['ID']:
        get_tracks_from_album(album_id)

    audio_features = []

    for track in track_ids:
        audio_features += sp.audio_features(tracks = track)
        
    features_list = []
    for features in audio_features:
        features_list.append([features['acousticness'], features['danceability'],
                            features['liveness'],features['loudness'],
                            features['speechiness']])
            
    audiof_df = pd.DataFrame(features_list, columns=["acousticness", "danceability", "liveness", "loudness", "speechiness"])

    audiof_df["Track_ID"] = track_ids
    audiof_df["Track_Name"] = track_names
    audiof_df = audiof_df[["Track_Name","Track_ID","acousticness", "danceability", "liveness", "loudness", "speechiness"]]
    audiof_df.drop_duplicates(subset="Track_Name", keep = 'first', inplace=True)

    return audiof_df