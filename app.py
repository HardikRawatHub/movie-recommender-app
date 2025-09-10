import streamlit as st
import pandas as pd
import pickle
import os
import gdown
import numpy as np

# Download & load similarity.pkl
file_name = "similarity.pkl"
file_id = "13cIHoClTp8ABUiB_aeTXxE6Zk07AsxMl"
url = f"https://drive.google.com/file/d/13cIHoClTp8ABUiB_aeTXxE6Zk07AsxMl/view?usp=drive_link={file_id}"

if not os.path.exists(file_name):
    gdown.download(url, file_name, quiet=False)

with open(file_name, "rb") as f:
    similarity = pickle.load(f)

# Your existing model load (small file, can stay local or same trick if needed)
movies_dict = pickle.load(open("movies.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

# rest of your app code...

# --- Page Configuration ---
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    # Changed to wide for a more spacious and modern feel
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --- Core Recommendation Logic ---
def recommend(movie):
    """
    Finds and returns the top 5 most similar movie titles.
    This version is purely text-based and does not fetch posters.
    """
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        # Get the top 5 most similar movies, excluding the movie itself (which is at index 0)
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_titles = [movies.iloc[i[0]].title for i in movies_list]
        return recommended_titles

    except IndexError:
        st.error("The selected movie was not found in our database. Please try another.")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return []


# --- Data Loading (with critical encoding fix) ---
@st.cache_data
def load_data():
    """
    Loads the movie data and similarity matrix from pickle files.
    This function is cached for performance.
    """
    try:
        # The 'latin1' encoding is crucial for loading this specific pickle file
        with open('movies.pkl', 'rb') as f:
            movies_df = pd.DataFrame(pickle.load(f, encoding='latin1'))

        with open('similarity.pkl', 'rb') as f:
            similarity_matrix = pickle.load(f)

        return movies_df, similarity_matrix
    except FileNotFoundError as e:
        st.error(f"ERROR: A required data file was not found. Please place '{e.filename}' in the project folder.")
        st.stop()
    except Exception as e:
        st.error(f"A fatal error occurred while loading data files: {e}")
        st.stop()


movies, similarity = load_data()

# --- UI Styling (Clean & Modern CSS) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Roboto', sans-serif;
}
.stApp {
    background-color: #0d1117;
    color: #c9d1d9;
}
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    color: #c9d1d9;
}
.stButton > button {
    background-color: #238636;
    color: white;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px 28px;
    font-size: 16px;
    font-weight: 700;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    border-color: #2ea043;
    background-color: #2ea043;
}
.header {
    text-align: center;
    padding: 2rem 0 3rem 0;
}
.header h1 {
    font-size: 3.5rem;
    font-weight: 700;
    color: #ffffff;
}
.recommendation-box {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    text-align: center;
    font-size: 1.1rem;
    font-weight: 400;
    height: 100px; /* Give a fixed height for alignment */
    display: flex;
    justify-content: center;
    align-items: center;
    transition: all 0.3s ease; /* Add transition for hover effect */
}
.recommendation-box:hover {
    transform: translateY(-5px); /* Add a lift effect on hover */
    border-color: #2ea043;
    background-color: #21262d;
}
</style>
""", unsafe_allow_html=True)

# --- Application Layout ---
st.markdown("<div class='header'><h1>Movie Recommender System</h1></div>", unsafe_allow_html=True)

recommend_pressed = False
# Use columns to center the selection box
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_movie_name = st.selectbox(
        'Select a movie you like from the list below:',
        movies['title'].values,
        index=None,
        placeholder="Choose a movie..."
    )
    # Add a little vertical space before the button
    st.markdown("<div><br></div>", unsafe_allow_html=True)
    # Place button in the same column and make it fill the column width
    recommend_pressed = st.button('Get Recommendations', use_container_width=True)

if recommend_pressed:
    if selected_movie_name:
        with st.spinner('Finding recommendations...'):
            recommended_movies = recommend(selected_movie_name)

            if recommended_movies:
                st.markdown("---")
                st.subheader("Based on your choice, you might also like:")

                # Create 5 columns for the 5 recommendations
                cols = st.columns(5, gap="large")
                for i, movie in enumerate(recommended_movies):
                    with cols[i]:
                        st.markdown(f"<div class='recommendation-box'>{movie}</div>", unsafe_allow_html=True)
            else:
                # Error messages are handled inside the recommend function
                pass
    else:
        st.warning('Please select a movie first.')

