import streamlit as st
import pandas as pd
import numpy as np
import os
import gdown

# --- Google Drive settings (replace with your file ID) ---
file_id = "1UTtldKXYK7HO5a-WXfRhxKu9bl9r6tUl"  # e.g. "1abcXYZ123..."
url = f"https://drive.google.com/uc?id={file_id}"
file_name = "movies.npz"

# --- Download the file if not present ---
if not os.path.exists(file_name):
    with st.spinner("Downloading data..."):
        gdown.download(url, file_name, quiet=False)

# --- Load movies and similarity matrix from .npz ---
data = np.load(file_name, allow_pickle=True)
movies = pd.DataFrame(data['movies'], columns=['movie_id', 'title', 'tags'])
similarity = data['similarity']


# --- Page Configuration ---
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Core Recommendation Logic ---
def recommend(movie):
    """
    Returns top 5 most similar movie titles.
    """
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        recommended_titles = [movies.iloc[i[0]].title for i in movies_list]
        return recommended_titles
    except IndexError:
        st.error("The selected movie was not found. Try another.")
        return []
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return []

# --- UI Styling ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

html, body, [class*="st-"] { font-family: 'Roboto', sans-serif; }
.stApp { background-color: #0d1117; color: #c9d1d9; }
.stSelectbox div[data-baseweb="select"] > div { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; color: #c9d1d9; }
.stButton > button { background-color: #238636; color: white; border: 1px solid #30363d; border-radius: 8px; padding: 12px 28px; font-size: 16px; font-weight: 700; transition: all 0.2s ease; }
.stButton > button:hover { border-color: #2ea043; background-color: #2ea043; }
.header { text-align: center; padding: 2rem 0 3rem 0; }
.header h1 { font-size: 3.5rem; font-weight: 700; color: #ffffff; }
.recommendation-box { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem; text-align: center; font-size: 1.1rem; font-weight: 400; height: 100px; display: flex; justify-content: center; align-items: center; transition: all 0.3s ease; }
.recommendation-box:hover { transform: translateY(-5px); border-color: #2ea043; background-color: #21262d; }
</style>
""", unsafe_allow_html=True)

# --- Application Layout ---
st.markdown("<div class='header'><h1>Movie Recommender System</h1></div>", unsafe_allow_html=True)

recommend_pressed = False
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_movie_name = st.selectbox(
        'Select a movie you like:',
        movies['title'].values,
        index=None,
        placeholder="Choose a movie..."
    )
    st.markdown("<div><br></div>", unsafe_allow_html=True)
    recommend_pressed = st.button('Get Recommendations', use_container_width=True)

if recommend_pressed:
    if selected_movie_name:
        with st.spinner('Finding recommendations...'):
            recommended_movies = recommend(selected_movie_name)
            if recommended_movies:
                st.markdown("---")
                st.subheader("Based on your choice, you might also like:")
                cols = st.columns(5, gap="large")
                for i, movie in enumerate(recommended_movies):
                    with cols[i]:
                        st.markdown(f"<div class='recommendation-box'>{movie}</div>", unsafe_allow_html=True)
    else:
        st.warning('Please select a movie first.')
