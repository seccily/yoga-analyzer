# importing packages
from pathlib import Path
import PIL
import streamlit as st 

# local Modules
import settings
import helper
import analyzer

# setting page layout
st.set_page_config(
    page_title="Personal Yoga Routine Analyzer",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# main page heading
st.markdown("<h1 style='text-align: center; color: white;'>Welcome to Your Personal Yoga Routine Analyzer!</h1>", unsafe_allow_html=True)
st.divider()  

################################################## sidebar configurations ##################################################

st.sidebar.header("Analysis Configurations")

# yoga level config & select the apropriate model for the user
yogi_radio = st.sidebar.radio(
    "What kind of a yogi are you?", 
    settings.YOGI_LIST
    )

if yogi_radio == settings.ADVANCED:
    model_path = Path(settings.ADVANCED_MODEL)
    model_thresh = 0.5
elif yogi_radio == settings.BEGINNER:
    model_path = Path(settings.BEGINNER_MODEL)
    model_thresh = 0.7

with st.sidebar.expander("Learn more about how do we use yogi level information."):
    st.write("There are two AI models to detect your poses. If you are a beginner, we will take it slow and our AI model will \
            detect only 5-main yoga poses for you. If you're an advanced yogi, then we have a more capable model for your needs, \
            which can detect 47 poses for you!")

# analysis level config
analysis_radio = st.sidebar.radio(
    "What kind of a analysis do you want?", 
    settings.ANALYSIS_LIST
    )

duration_tolerance = None

if analysis_radio == settings.BASIC:
    analysis = "basic"
    duration_tolerance = st.sidebar.slider("Please select a tolerance (%) for the duration of the poses.", min_value=0, max_value=100, value=0, step=10)

elif analysis_radio == settings.DETAILED:
    analysis = "detailed"

with st.sidebar.expander("Learn more about how do we use analysis level information."):
    st.write("If all you need is just a basic analysis, we will just detect your poses and record the durations, then simply compare your whole \
             routine to see if you did the poses you entered and for specified durations in total. If you need a more detailed analysis, we'll need a  \
             detailed version of your routine to compare your training step-by-step! In detailed analysis, our AI model will score your poses as well...")

# input config
source_radio = st.sidebar.radio(
    "Select Source", 
    settings.SOURCES_LIST
    )

# loading the model
try:
    model, classes = helper.load_model(model_path)
except Exception as ex:
    st.error(f"Unable to load model. Check the specified path: {model_path}")
    st.error(ex)

# store the class names in a list for visualization
class_names = list(classes.values())
formatted_class_names = '\n'.join(', '.join(class_names[i:i+5]) for i in range(0, len(class_names), 5))


# Create lists to store user inputs
selected_items = []
minutes_values = []
seconds_values = []


################################################## yoga routine planner ##################################################

if 'selected_items' not in st.session_state:
    st.session_state.selected_items = []
if 'minutes_values' not in st.session_state:
    st.session_state.minutes_values = []
if 'seconds_values' not in st.session_state:
    st.session_state.seconds_values = []

# # Function to add more inputs
# def add_input():
#     st.session_state.selected_items.append(None)
#     st.session_state.minutes_values.append(0)
#     st.session_state.seconds_values.append(0)


st.markdown('##')
st.markdown("<h3 style='text-align: center; color: white;'>Add planned poses of your yoga routine to be analyzed</h3>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: center; color: gray;'>(Select your poses and the planned durations of your yoga routine.)</h6>", unsafe_allow_html=True)
st.markdown('###')

# Display inputs in columns
col1, col2, col3, col4, col5 = st.columns((3, 1, 1, 0.5, 0.5))

with col1:
    selected_item = st.selectbox("Select Pose", class_names, index=0)

with col2:
    minutes = st.selectbox("Enter minutes", list(range(16)), index=0)
    
with col3:
    seconds = st.selectbox("Enter seconds", list(range(60)), index=0)


with col4:
    if st.button("Enter"):
        st.session_state.selected_items.append(selected_item)
        st.session_state.minutes_values.append(minutes)
        st.session_state.seconds_values.append(seconds)

with col5:
    if st.button("Delete Last Input") and len(st.session_state.selected_items) > 0:
        st.session_state.selected_items.pop()
        st.session_state.minutes_values.pop()
        st.session_state.seconds_values.pop()
with col5:
    if st.button("Clear all") and len(st.session_state.selected_items) > 0:
        st.session_state.selected_items = []
        st.session_state.minutes_values = []
        st.session_state.seconds_values = []

data = {'Pose': st.session_state.selected_items, 'Minutes': st.session_state.minutes_values, 'Seconds': st.session_state.seconds_values}
st.table(data)

st.divider()  

st.session_state['DETECT_POSES_BUTTON'] = False # initial state

if source_radio == settings.VIDEO: # detect poses button to show only during prediction on demo video
    with col1:
        if st.button("Detect Poses"):
            st.session_state['DETECT_POSES_BUTTON'] = True
        else:
            st.session_state['DETECT_POSES_BUTTON'] = False


if len(data['Pose']) == 0:
    st.session_state['TABLE_FILLED'] =  False
else:
    st.session_state['TABLE_FILLED'] =  True

if st.session_state['DETECT_POSES_BUTTON'] and not st.session_state['TABLE_FILLED']:
    st.error("Please enter at least one pose!")
    st.stop()


################################################## analysis ##################################################

source_img = None
detected_poses = None

# conditions for different input options

if source_radio == settings.VIDEO:
    detected_poses = helper.play_stored_video(model, model_thresh)

elif source_radio == settings.LIVE:
    detected_poses = helper.play_livevideo(model, model_thresh)

else:
    st.error("Please select a valid source type!")

# visualize the analysis results at the end of the session
if detected_poses is not None:
    routine_check = analyzer.analyze_routine(analysis_radio, detected_poses, data, duration_tolerance)
