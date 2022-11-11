import pandas as pd
import streamlit as st

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

cid = st.secrets("CLIENT_ID")
secret = st.secrets("CLIENT_SECRET")

def spotify_login(cid, secret):
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret) 
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=10, retries=5)


sp = spotify_login(cid, secret)

from urllib.parse import urlparse

def get_id(input_url):
    parts = urlparse(input_url)
    directories = parts.path.strip('/').split('/')
    _id_ = directories[1]
    return _id_


def get_tracks(_id_):
    playlist_id = 'spotify:playlist:' + _id_

    def get_all_tracks_from_playlist(playlist_id):
        tracks_response = sp.playlist_tracks(playlist_id)
        tracks = tracks_response["items"]
        while tracks_response["next"]:
            tracks_response = sp.next(tracks_response)
            tracks.extend(tracks_response["items"])
        return tracks

    track_list = get_all_tracks_from_playlist(playlist_id)

    track_names = [] 
    track_ids = []
    artist_names = []

    for track in track_list:
        track_names.append(track['track']['name'])
        track_ids.append(track['track']['id'])
        artist_names.append(track["track"]["artists"][0]["name"])

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
    audiof_df["Artist_Name"] = artist_names
    audiof_df = audiof_df[["Track_Name","Track_ID","Artist_Name","acousticness", "danceability", "liveness", "loudness", "speechiness"]]

    return audiof_df
