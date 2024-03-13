# Import statements
import streamlit as st
import pandas as pd
import os
import requests
from PIL import Image
from io import BytesIO


###################
# LOADING DATASET #
###################

#file_path = "https://storage.cloud.google.com/cine_ethics/data/summarized_data.csv"
#file_path = os.getenv("CINE_PICK_TABLE")
file_path = "raw_data/cine_pick_table.csv"
df = pd.read_csv(file_path, sep=',')


                        ####################
                        # STREAMLIT LAYOUT #
                        ####################

############################
# DEFINING JAVASCRIPT CODE #
############################

# Javascript as python string
javascript_code = """
<script>
var input = document.getElementById('textfield');
var datalist = document.getElementById('suggestions');

input.addEventListener('input', function(e) {
    var query = input.value;
    fetch('/suggest?query=' + query)
        .then(response => response.json())
        .then(data => {
            datalist.innerHTML = '';
            data.forEach(function(suggestion) {
                var option = document.createElement('option');
                option.value = suggestion;
                datalist.appendChild(option);
            });
        });
});
</script>
"""

# Render the JavaScript code using st.markdown
st.markdown(javascript_code, unsafe_allow_html=True)

# Set the background image
background_image = """
<style>
[data-testid="stAppViewContainer"] > .main {
    background-image: url("https://kb.positivekeyword.com/wp-content/uploads/2024/03/CinePickSmall_15.png");
    background-size: 75vw 100vh;  # This sets the size to cover 100% of the viewport width and height
    background-position: center;
    background-repeat: no-repeat;
}
</style>
"""

st.markdown(background_image, unsafe_allow_html=True)


################################
# INITIALIZING STATE VARIABLES #
################################

if 'movies' not in st.session_state:
    st.session_state.movies = []
    st.session_state._movies = st.session_state.movies

if 'gen_movie' not in st.session_state:
    st.session_state.gen_movie = ''
    st.session_state.gen_synopsis = ''

if 'faces_title_1' not in st.session_state:
    st.session_state.faces_title_1 = []
    st.session_state.imread_faces_title_1 = []
    st.session_state.faces_bounds_title_1 = []

if 'faces_title_2' not in st.session_state:
    st.session_state.faces_title_2 = []
    st.session_state.imread_faces_title_2 = []
    st.session_state.faces_bounds_title_2 = []

if 'title_1_char' not in st.session_state:
    st.session_state.title_1_char = []

if 'title_2_char' not in st.session_state:
    st.session_state.title_2_char = []

if 'char_1' not in st.session_state:
    st.session_state.char_1 = ''

if 'char_2' not in st.session_state:
    st.session_state.char_2 = ''

st.session_state.movies = st.session_state._movies


######################
# DEFINING FUNCTIONS #
######################

def key_protect():
    st.session_state._movies = st.session_state.movies


def get_genres():
    genres = []
    if crime:
        genres.append('crime')
    if thriller:
        genres.append('thriller')
    if fantasy:
        genres.append('fantasy')
    if scifi:
        genres.append('scifi')
    if romance:
        genres.append('romance')
    if family:
        genres.append('family')
    if action:
        genres.append('action')
    if adventure:
        genres.append('adventure')
    if horror:
        genres.append('horror')
    if mistery:
        genres.append('mistery')
    return genres


def display_characters(faces_title):
    # Create a list of images
    char_list = []
    for image_char in faces_title:
        # Extract the NumPy array representing the image data
        image_data = image_char[0]

        # Convert the NumPy array to a PIL image object
        pil_image = Image.fromarray(image_data, 'RGB')
        char_list.append(pil_image)

    return char_list


###################################
# MOVIE SELECTION SIDEBAR SECTION #
###################################

# Sidebar Title
st.sidebar.title('Movie Synopsis Merger 🍿🎬')  # Title
st.sidebar.caption("Discover your own innovative plot!")  # Description


# Genre Selection splitted in 2 columns
st.sidebar.write('Select Genres:')
col1, col2 = st.sidebar.columns(2)

with col1:
    crime = st.checkbox('crime', value=False)
    thriller = st.checkbox('thriller', value=False)
    fantasy = st.checkbox('fantasy', value=False)
    scifi = st.checkbox('scifi', value=False)
    romance = st.checkbox('romance', value=False)

with col2:
    family = st.checkbox('family', value=False)
    action = st.checkbox('action', value=False)
    adventure = st.checkbox('adventure', value=False)
    horror = st.checkbox('horror', value=False)
    mistery = st.checkbox('mistery', value=False)


# Getting selected Genres
genres = get_genres()

# Getting Database with only selected genres
data = df.loc[df['genre'].isin(genres)]

try:
    # Multiselect field for selecting movies
    st.sidebar.write('')
    st.sidebar.write('Select Movies:')
    st.sidebar.multiselect('movies', data.index,
                        format_func=lambda x: data['title'].loc[x].title(),
                        key='movies',
                        on_change=key_protect,
                        label_visibility="collapsed")
except Exception as e:
    st.sidebar.warning('Cannot remove Genre that already has a selected movie.')


# getting session variable
selected_indices = st.session_state.movies


# Check if more than two movies are selected
if len(selected_indices) > 2:
    st.sidebar.warning('Please select at most two movies.')
    # Limit the selected indices to the first two selected indices
    selected_indices = selected_indices[:2]





                            #######################
                            # RUNNING APPLICATION #
                            #######################

url = "https://image-5e4uq44i6a-ez.a.run.app"
#url = "http://127.0.0.1:8000"


# When 'Merge Synopsis' button is pushed
if st.sidebar.button('Merge Movies') and len(selected_indices) == 2:
    title_1, title_2 = df['title'].loc[selected_indices].values
    title_1, title_2 = title_1.title(), title_2.title()

    # Getting original synopsis of the selected movies.
    syn_1, syn_2 = df['summarized_synopsis'].loc[selected_indices].values


    ##################################
    # GENERATING SYNOPSIS AND POSTER #
    ##################################
    if st.session_state.gen_movie == '' or st.session_state.gen_synopsis == '':
        with st.spinner('Generating New Movie'): # Spinner to show that it's loading
            # API Endpoints
            syn_url = url + '/synopsis'
            poster_url = url + '/poster'
            params={'title_1': title_1, 'title_2': title_2}

            # Call OpenAI API for synopsis
            response = requests.get(syn_url, params=params).json()
            st.session_state.gen_synopsis = response

            # Call OpenAI API for poster
            poster_response = requests.get(poster_url, params=params)
            new_image = BytesIO(poster_response.content)
            img = Image.open(new_image)
            st.session_state.gen_movie = img



    # Displaying generated Poster
    st.title('Generated Movie Poster')
    st.image(st.session_state.gen_movie)

    # Displaying Generated Synopsis
    st.title('Generated Synopsis')
    st.write(st.session_state.gen_synopsis)



    # ##########################################################
    # # LOADING FIRST MOVIE CHARACTER PICTURES, IMREAD OBJECTS #
    # ##########################################################

    # if st.session_state.faces_title_1 == []:
    #     with st.spinner(f'Loading Characters from {title_1}'): # Spinner to show that it's loading
    #         display_url = url + '/display'
    #         # Call  API for Title 1 Character Display
    #         params={'title': title_1}
    #         response = requests.get(display_url, params=params)
    #         print(response.content)
    #         faces_title_1 = response['faces_title']
    #         imread_faces_title_1 = response['imread_faces_title']

    #         st.session_state.faces_title_1 = faces_title_1
    #         st.session_state.imread_faces_title_1 = imread_faces_title_1


    # #################################
    # # DISPLAYING FIRST MOVIE IMAGES #
    # #################################

    # st.title(f"{title_1}")
    # st.session_state.title_1_char = display_characters(st.session_state.faces_title_1)

    # # Displaying images
    # for i, img in enumerate(st.session_state.title_1_char):
    #     if i <= 1:
    #         st.image(img)


    # ###################################
    # # DISPLAYING FIRST MOVIE SYNOPSIS #
    # ###################################

    # with st.expander(f"Show/hide {title_1} synopsis"): # Dropdown to hide or show sinopsis
    #     st.markdown(f"""{syn_1}""")


    # ###########################################################
    # # LOADING SECOND MOVIE CHARACTER PICTURES, IMREAD OBJECTS #
    # ###########################################################

    # if st.session_state.faces_title_2 == []:
    #     with st.spinner(f'Loading Characters from {title_2}'): # Spinner to show that it's loading
    #         display_url = url + '/display'
    #         # Call  API for Title 1 Character Display
    #         params={'title': title_2}
    #         response = requests.get(display_url, params=params).json()

    #         faces_title_2 = response['faces_title']
    #         imread_faces_title_2 = response['imread_faces_title']

    #         st.session_state.faces_title_2 = faces_title_2
    #         st.session_state.imread_faces_title_2 = imread_faces_title_2


    # ##################################
    # # DISPLAYING SECOND MOVIE IMAGES #
    # ##################################

    # st.title(f"{title_2}")
    # st.session_state.title_2_char = display_characters(st.session_state.faces_title_2)

    # # Displaying images
    # for i, img in enumerate(st.session_state.title_2_char):
    #     if i <= 1:
    #         st.image(img)


    # ####################################
    # # DISPLAYING SECOND MOVIE SYNOPSIS #
    # ####################################

    # with st.expander(f"Show/hide {title_2} synopsis"): # Dropdown to hide or show sinopsis
    #     st.markdown(f"""{syn_2}""")


    # #################
    # # SAVING IMAGES #
    # #################

    # for i, img_i in enumerate(st.session_state.imread_faces_title_1):
    #     if i <= 1:
    #         image = cv2.cvtColor(img_i, cv2.COLOR_BGR2RGB)
    #         cv2.imwrite(f"raw_data/morph/title_1_image{i}.png", image)

    # for j, img_j in enumerate(st.session_state.imread_faces_title_2):
    #     if j <= 1:
    #         image = cv2.cvtColor(img_j, cv2.COLOR_BGR2RGB)
    #         cv2.imwrite(f"raw_data/morph/title_2_image{j}.png", image)


    # ####################
    # # MORPH THE IMAGES #
    # ####################

    # with st.spinner('Generating New Character'): # Spinner to show that it's loading
    #     # Get the list of files in the directory
    #     files = os.listdir("raw_data/morph/")

    #     # Get the full paths of the files
    #     file_paths = [os.path.join("raw_data/morph/", file) for file in files]


    #     # API Endpoints
    #     char_url = url + '/morph'
    #     params={'path_1': file_paths[0], 'path_2': file_paths[1], 'path_3': file_paths[2], 'path_4': file_paths[3]}

    #     # Call OpenAI API for poster
    #     character_response = requests.get(char_url, params=params)
    #     new_image = BytesIO(character_response.content)
    #     morphed_image = Image.open(new_image)

    #     st.title('Generated Character')

    #     # Display the image in Streamlit
    #     st.image(morphed_image)
