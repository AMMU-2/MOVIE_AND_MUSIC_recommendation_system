import streamlit as st
import pickle
import pandas as pd
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Set up the Spotify client credentials
CLIENT_ID = "70a9fb89662f4dac8d07321b259eaad7"
CLIENT_SECRET = "4d6710460d764fbbb8d8753dc094d131"

# Initialize the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load movie data
movies_dict = pickle.load(open('C:\Desktop\movie and song folder\Data\movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Load movie similarity data
movie_similarity = pickle.load(open('C:\Desktop\movie and song folder\Data\similarity.pkl', 'rb'))

# Load music data
music = pickle.load(open('C:\Desktop\movie and song folder\Data\df.pkl', 'rb'))
music_similarity = pickle.load(open('C:\Desktop\movie and song folder\Data\similar.pkl', 'rb'))

# Define functions for movie and music recommendation
def fetch_movie_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=124ce641403f1df8749e9dbaec0c5748&language=en-US'.format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500" + data['poster_path']

def recommend_movie(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = movie_similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:10]

    recommend_movies = []
    recommend_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommend_movies.append(movies.iloc[i[0]].title)
        recommend_movies_posters.append(fetch_movie_poster(movie_id))
    return recommend_movies, recommend_movies_posters

def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track")

    if results and results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        album_cover_url = track["album"]["images"][0]["url"]
        return album_cover_url
    else:
        return "https://i.postimg.cc/0QNxYz4V/social.png"

def recommend_music(song):
    index = music[music['song'] == song].index[0]
    distances = sorted(list(enumerate(music_similarity[index])), key=lambda x: x[1], reverse=True)

    recommended_music_names = []
    recommended_music_posters = []
    for i in distances[1:6]:
        artist = music.iloc[i[0]].artist
        recommended_music_posters.append(get_song_album_cover_url(music.iloc[i[0]].song, artist))
        recommended_music_names.append(music.iloc[i[0]].song)
    return recommended_music_names, recommended_music_posters

# Create a Streamlit app
st.set_page_config(page_title="Movie and Music Recommendation App", layout="wide")
st.title('Recommendation System')

# Create a page selector in the sidebar
page = st.sidebar.selectbox("Select a page", ["Movie Recommendation", "Music Recommendation"])

if page == "Movie Recommendation":
    # Movie Recommendation Page
    st.header("Movie Recommendation")

    selected_movie_name = st.selectbox('Select a movie or type its name', movies['title'].values)

    if st.button('Recommend'):
        recommendation = recommend_movie(selected_movie_name)

    if 'recommendation' in locals():
        col1, col2, col3, col4, col5 = st.columns(5)

        for i in range(5):
            with col1:
                st.header(recommendation[0][i])
                st.image(recommendation[1][i])

if page == "Music Recommendation":
    # Music Recommendation Page
    st.header('Music Recommendation')

    music_list = music['song'].values
    selected_song = st.selectbox("Type or select a song from the dropdown", music_list)

    if st.button('Show Recommendation'):
        recommended_music_names, recommended_music_posters = recommend_music(selected_song)

        col1, col2, col3, col4, col5 = st.columns(5)

        for i in range(5):
            with col1:
                st.text(recommended_music_names[i])
                st.image(recommended_music_posters[i])
