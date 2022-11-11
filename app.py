import time
from urllib.parse import urlparse
import streamlit as st
import pandas as pd

from getPlaylistTracks import get_tracks
from getPlaylistTracks import get_id

st.set_page_config(layout="wide")

st.title("MoodMixer")

input_url = ""
input_url = st.text_input("Enter Artist/Playlist URL")

import spotipy
from spotipy.oauth2 import SpotifyOAuth

cid = st.secrets.spotify_creds.CLIENT_ID
secret = st.secrets.spotify_creds.CLIENT_SECRET
red_url = st.secrets.spotify_creds.REDIRECT_URL

def get_link(tracklist):
    url = "spotify:track:"
    url_list = []
    for id in tracklist:
        final_url = url + id
        url_list.append(final_url)

    return url_list

def make_clickable(url, text):
    return f'<a target="_blank" href="{url}">{text}</a>'


def add_Playlist(username, playlist_name, playlist_desc, track_list):
    scope = 'playlist-modify-public'

    token = SpotifyOAuth(scope=scope, redirect_uri=red_url, client_id = cid, client_secret=secret)
    sp = spotipy.Spotify(auth_manager=token)

    #create playlist
    sp.user_playlist_create(user=username, name=playlist_name, public=True, collaborative= False,description=playlist_desc)

    prePlaylist = sp.user_playlists(user=username)
    playlist = prePlaylist['items'][0]['id']

    #add songs to playlist
    sp.user_playlist_add_tracks(user=username, playlist_id=playlist, tracks = track_list)

def get_type(input_url):
    parts = urlparse(input_url)
    directories = parts.path.strip('/').split('/')
    _id_ = directories[0]
    return _id_

@st.cache()
def Model(df):
    X = df[["acousticness", "danceability", "liveness", "loudness", "speechiness"]]

    from sklearn.preprocessing import MinMaxScaler
    scaler= MinMaxScaler()

    loudness=X["loudness"].values
    loudness_scaled=scaler.fit_transform(loudness.reshape(-1, 1))

    X["loudness"]=loudness_scaled

    features=X.values
    from sklearn.cluster import KMeans
    model = KMeans(n_clusters=5)
    model = model.fit(features)

    predictions=model.predict(features)

    df['cluster']=predictions

    df_classify=df[["acousticness", "danceability", "liveness","loudness", "speechiness","cluster"]]
    X=df_classify.iloc[:,:-1].values
    Y=df_classify.iloc[:,-1].values

    from sklearn.metrics import confusion_matrix
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test=train_test_split(X,Y,test_size=0.2)
    X_train[:,4]=scaler.fit_transform(X_train[:,4].reshape(-1, 1)).reshape(-1,)
    X_test[:,4]=scaler.transform(X_test[:,4].reshape(-1, 1)).reshape(-1,)

    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.33)

    rfc = RandomForestClassifier(n_estimators=100,criterion='gini')
    rfc.fit(X_train,y_train)

    y_pred = rfc.predict(X_test)

    cm = confusion_matrix(y_test, y_pred)

    sorted_df = df.sort_values('cluster')
    sorted_df.drop(["acousticness", "danceability", "liveness", "loudness", "speechiness"], axis=1, inplace=True)
    sorted_df = sorted_df[~sorted_df.index.duplicated(keep='first')]

    moodmix_0 = sorted_df[sorted_df.cluster.eq(0)]
    moodmix_1 = sorted_df[sorted_df.cluster.eq(1)]
    moodmix_2 = sorted_df[sorted_df.cluster.eq(2)]
    moodmix_3 = sorted_df[sorted_df.cluster.eq(3)]
    moodmix_4 = sorted_df[sorted_df.cluster.eq(4)]

    moodmix_0 = moodmix_0.sample(frac=1)
    moodmix_1 = moodmix_1.sample(frac=1)
    moodmix_2 = moodmix_2.sample(frac=1)
    moodmix_3 = moodmix_3.sample(frac=1)
    moodmix_4 = moodmix_4.sample(frac=1)

    moodmix_0.drop('cluster', axis=1, inplace=True)
    moodmix_1.drop('cluster', axis=1, inplace=True)
    moodmix_2.drop('cluster', axis=1, inplace=True)
    moodmix_3.drop('cluster', axis=1, inplace=True)
    moodmix_4.drop('cluster', axis=1, inplace=True)

    tracklist_1 = moodmix_0['Track_ID'].tolist()
    tracklist_2 = moodmix_1['Track_ID'].tolist()
    tracklist_3 = moodmix_2['Track_ID'].tolist()
    tracklist_4 = moodmix_3['Track_ID'].tolist()
    tracklist_5 = moodmix_4['Track_ID'].tolist()
    
    url_1 = get_link(tracklist_1)
    url_2 = get_link(tracklist_2)
    url_3= get_link(tracklist_3)
    url_4 = get_link(tracklist_4)
    url_5 = get_link(tracklist_5)

    moodmix_0["Link"] = url_1
    moodmix_1["Link"] = url_2
    moodmix_2["Link"] = url_3
    moodmix_3["Link"] = url_4
    moodmix_4["Link"] = url_5

    moodmix_0.reset_index(inplace = True, drop = True)
    moodmix_0.index += 1

    moodmix_1.reset_index(inplace = True, drop = True)
    moodmix_1.index += 1

    moodmix_2.reset_index(inplace = True, drop = True)
    moodmix_2.index += 1

    moodmix_3.reset_index(inplace = True, drop = True)
    moodmix_3.index += 1

    moodmix_4.reset_index(inplace = True, drop = True)
    moodmix_4.index += 1

    moodmix_0['Link'] = moodmix_0['Link'].apply(make_clickable, args = ('Listen',))
    moodmix_1['Link'] = moodmix_1['Link'].apply(make_clickable, args = ('Listen',))
    moodmix_2['Link'] = moodmix_2['Link'].apply(make_clickable, args = ('Listen',))
    moodmix_3['Link'] = moodmix_3['Link'].apply(make_clickable, args = ('Listen',))
    moodmix_4['Link'] = moodmix_4['Link'].apply(make_clickable, args = ('Listen',))

    return moodmix_0, moodmix_1, moodmix_2, moodmix_3, moodmix_4

if input_url:
    type = get_type(input_url)

    if(type == "playlist"):
        _id_ = get_id(input_url)
        df = get_tracks(_id_)

    
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["MoodMix - 1", "MoodMix - 2", "MoodMix - 3", "MoodMix - 4", "MoodMix - 5"])

        moodmix_0, moodmix_1, moodmix_2, moodmix_3 , moodmix_4 = Model(df)

        tracklist_1 = moodmix_0["Track_ID"]
        tracklist_2 = moodmix_1["Track_ID"]
        tracklist_3 = moodmix_2["Track_ID"]
        tracklist_4 = moodmix_3["Track_ID"]
        tracklist_5 = moodmix_4["Track_ID"]

        df0 = moodmix_0.loc[:, moodmix_0.columns != 'Track_ID']
        df1 = moodmix_1.loc[:, moodmix_1.columns != 'Track_ID']
        df2 = moodmix_2.loc[:, moodmix_2.columns != 'Track_ID']
        df3 = moodmix_3.loc[:, moodmix_0.columns != 'Track_ID']
        df4 = moodmix_4.loc[:, moodmix_0.columns != 'Track_ID']

        df0 = df0.to_html(escape=False)
        df1 = df1.to_html(escape=False)
        df2 = df2.to_html(escape=False)
        df3 = df3.to_html(escape=False)
        df4 = df4.to_html(escape=False)

        with tab1:
            st.subheader("MoodMix - 1")
            with st.form("MoodMix-1 (Playlist)"):
                
                st.write(df0, unsafe_allow_html=True)
                st.subheader("To save this playlist:")
                username = ""
                username = st.text_input("Enter your Profile URL")
                playlist_name = ""
                playlist_name = st.text_input("Enter Playlist Name")
                playlist_desc = ""
                playlist_desc = st.text_input("Enter Playlist Desc")
                submit_button = st.form_submit_button("Save")
            if username:
                user_id = get_id(username)
                if playlist_name:
                    if playlist_desc:
                        add_Playlist(user_id, playlist_name, playlist_desc, tracklist_1)
                        st.success("Done!")

        with tab2: 
            st.subheader("MoodMix - 2")
            with st.form("MoodMix-2 (Playlist)"):
                st.write(df1, unsafe_allow_html=True)
                st.subheader("To save this playlist:")
                username = ""
                username = st.text_input("Enter your Profile URL")
                playlist_name = ""
                playlist_name = st.text_input("Enter Playlist Name")
                playlist_desc = ""
                playlist_desc = st.text_input("Enter Playlist Desc")
                submit_button = st.form_submit_button("Save")
            if username:
                user_id = get_id(username)
                if playlist_name:
                    if playlist_desc:
                        add_Playlist(user_id, playlist_name, playlist_desc, tracklist_2)
                        st.success("Done!")

        with tab3:
            st.subheader("MoodMix - 3")
            with st.form("MoodMix-3 (Playlist)"):
                st.write(df2, unsafe_allow_html=True)
                st.subheader("To save this playlist:")
                username = ""
                username = st.text_input("Enter your Profile URL")
                playlist_name = ""
                playlist_name = st.text_input("Enter Playlist Name")
                playlist_desc = ""
                playlist_desc = st.text_input("Enter Playlist Desc")
                submit_button = st.form_submit_button("Save")
            if username:
                user_id = get_id(username)
                if playlist_name:
                    if playlist_desc:
                        add_Playlist(user_id, playlist_name, playlist_desc, tracklist_3)
                        st.success("Done!")

        with tab4:
            st.subheader("MoodMix - 4")
            with st.form("MoodMix-4 (Playlist)"):
                st.write(df3, unsafe_allow_html=True)
                st.subheader("To save this playlist:")
                username = ""
                username = st.text_input("Enter your Profile URL")
                playlist_name = ""
                playlist_name = st.text_input("Enter Playlist Name")
                playlist_desc = ""
                playlist_desc = st.text_input("Enter Playlist Desc")
                submit_button = st.form_submit_button("Save")
            if username:
                user_id = get_id(username)
                if playlist_name:
                    if playlist_desc:
                        add_Playlist(user_id, playlist_name, playlist_desc, tracklist_4)
                        st.success("Done!")

        with tab5:
            st.subheader("MoodMix - 5")
            with st.form("MoodMix-5 (Playlist)"):
                st.write(df4, unsafe_allow_html=True)
                st.subheader("To save this playlist:")
                username = ""
                username = st.text_input("Enter your Profile URL")
                playlist_name = ""
                playlist_name = st.text_input("Enter Playlist Name")
                playlist_desc = ""
                playlist_desc = st.text_input("Enter Playlist Desc")
                submit_button = st.form_submit_button("Save")
            if username:
                user_id = get_id(username)
                if playlist_name:
                    if playlist_desc:
                        add_Playlist(user_id, playlist_name, playlist_desc, tracklist_5)
                        st.success("Done!")


