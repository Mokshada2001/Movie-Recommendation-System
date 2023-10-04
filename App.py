import streamlit as st
from PIL import Image
import json
from Classifier import KNearestNeighbours
from bs4 import BeautifulSoup
import requests, io
import PIL.Image
from urllib.request import urlopen


with open('./Data/movie_data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open('./Data/movie_titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)
hdr = {'User-Agent': 'Mozilla/5.0'}


def movie_poster_fetcher(imdb_link):
    # request.get() gets the required imdb link and responses in text format
    # hdr is  a dictionary object that contains headers to be included in the request
    url_data = requests.get(imdb_link, headers=hdr).text
    # BeautifulSoup library parses the HTML content obtained from url_data
    s_data = BeautifulSoup(url_data, 'html.parser')
    imdb_dp = s_data.find("meta", property="og:image")
    # attrs attribute is used to access the attributes of the imdb_dp element
    movie_poster_link = imdb_dp.attrs['content']
    u = urlopen(movie_poster_link)
    raw_data = u.read()
    # instead of downloading, the image is opened using bytes
    image = PIL.Image.open(io.BytesIO(raw_data))
    image = image.resize((158, 301), )
    st.image(image, use_column_width=False)


def get_movie_info(imdb_link):
    url_data = requests.get(imdb_link, headers=hdr).text
    s_data = BeautifulSoup(url_data, 'html.parser')
    imdb_content = s_data.find("meta", property="og:description")
    # attrs attribute is used to access the attributes of the imdb_content element
    movie_descr = imdb_content.attrs['content']
    movie_descr = str(movie_descr).split('.')
    movie_director = movie_descr[0]
    movie_cast = str(movie_descr[1]).replace('With', 'Cast: ').strip()
    movie_story = 'Story: ' + str(movie_descr[2]).strip() + '.'
    rating = s_data.find("span", class_="sc-bde20123-1 iZlgcd").text
    movie_rating = 'Total Rating count: ' + str(rating)
    return movie_director, movie_cast, movie_story, movie_rating


def KNN_Movie_Recommender(test_point, k):
    # An empty list named target is created with the same length as the movie_titles list.
    # This list will be used as the target variable for the KNN algorithm.
    # Each element in the target list is initially set to 0.
    target = [0 for item in movie_titles]
    # KNearestNeighbours class is instantiated as model
    model = KNearestNeighbours(data, target, test_point, k=k)
    model.fit()
    table = []
    for i in model.indices:
        # movie_titles[i][0]:- movie title
        # movie_titles[i][2]:- additional description
        table.append([movie_titles[i][0], movie_titles[i][2], data[i][-1]])
    print(table)
    return table


st.set_page_config(
    page_title="Movie Recommendation System"
)


def run():
    st.markdown('''<h4 style='text-align: left; font-size: 40px; color: green'>
                    <b>Movie Recommendation System<b></h4>''', unsafe_allow_html=True)
    # st.title("Movie Recommendation System")
    st.markdown('''<h4 style='text-align: left; color: #32CD32'>
                "Enchanting Movie Recommendations at Your Fingertips"</h4>''', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']
    movies = [title[0] for title in movie_titles]
    category = ['--Select--', 'Movie Similar To', 'Genre Based']
    cat_op = st.selectbox('Select Recommendation Type', category)

    if cat_op == category[0]:
        st.warning('!!!Recommendation Type Must be Selected!!!')
    elif cat_op == category[1]:
        select_movie = st.selectbox('Select movie: (You will be recommended movies based on this selection)',
                                    ['--Select--'] + movies)
        dec = st.radio("Do you want to fetch the movie poster?", ('Yes', 'No'))

        if dec == 'No':
            if select_movie == '--Select--':
                st.warning('!!!Select the movie!!!')
            else:
                no_of_reco = st.slider('Choose the number of movies that you would like to be recommended:'
                                       , min_value=5, max_value=10, step=1)
                # 'genres' is assigned the value of the 'data' list at the
                # index corresponding to 'select_movie' from the 'movies' list
                genres = data[movies.index(select_movie)]
                test_points = genres
                table = KNN_Movie_Recommender(test_points, no_of_reco + 1)
                table.pop(0)
                c = 0
                st.success('The Recommendations are given below')
                for movie, link, ratings in table:
                    c += 1
                    director, cast, story, total_rat = get_movie_info(link)
                    st.markdown(f"({c})[ {movie}]({link})")
                    st.markdown(director)
                    st.markdown(cast)
                    st.markdown(story)
                    # st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')
        else:
            if select_movie == '--Select--':
                st.warning('!!!Select the movie!!!')
            else:
                # imdb_score = st.slider('Choose IMDb score:', 1, 10, 8)
                no_of_reco = st.slider('Choose the number of movies that you would like to be recommended:',
                                       min_value=5, max_value=10, step=1)
                genres = data[movies.index(select_movie)]
                test_points = genres
                # test_points.append(imdb_score)
                table = KNN_Movie_Recommender(test_points, no_of_reco + 1)
                table.pop(0)
                c = 0
                st.success('The Recommendations are given below')
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    movie_poster_fetcher(link)
                    director, cast, story, total_rat = get_movie_info(link)

                    st.markdown(director)
                    st.markdown(cast)
                    st.markdown(story)
                    # st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')

    elif cat_op == category[2]:
        sel_gen = st.multiselect('Select Genres:', genres)
        dec = st.radio("Do you want to fetch the movie poster?", ('Yes', 'No'))
        if dec == 'No':
            if sel_gen:
                imdb_score = st.slider('Choose your preferred IMDb score:', 1, 10, 8)
                no_of_reco = st.number_input('Choose the number of movies that you would like to be recommended:',
                                             min_value=5, max_value=10, step=1)
                test_point = [1 if genre in sel_gen else 0 for genre in genres]
                test_point.append(imdb_score)
                table = KNN_Movie_Recommender(test_point, no_of_reco)
                c = 0
                st.success('The Recommendations are given below')
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    director, cast, story, total_rat = get_movie_info(link)
                    st.markdown(director)
                    st.markdown(cast)
                    st.markdown(story)
                    # st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')
        else:
            if sel_gen:
                imdb_score = st.slider('Choose your preferred IMDb score:', 1, 10, 8)
                no_of_reco = st.number_input('Choose the number of movies that you would like to be recommended:',
                                             min_value=5, max_value=10, step=1)
                test_point = [1 if genre in sel_gen else 0 for genre in genres]
                test_point.append(imdb_score)
                table = KNN_Movie_Recommender(test_point, no_of_reco)
                c = 0
                st.success('The Recommendations are given below')
                for movie, link, ratings in table:
                    c += 1
                    st.markdown(f"({c})[ {movie}]({link})")
                    movie_poster_fetcher(link)
                    director, cast, story, total_rat = get_movie_info(link)

                    st.markdown(director)
                    st.markdown(cast)
                    st.markdown(story)
                    # st.markdown(total_rat)
                    st.markdown('IMDB Rating: ' + str(ratings) + '⭐')


run()

