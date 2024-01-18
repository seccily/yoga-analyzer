from ultralytics import YOLO
import streamlit as st
import cv2
import datetime
import settings
import traceback

predictions = []

def load_model(model_path):
    model = YOLO(model_path)
    classes = model.names
    return model, classes

def _create_table_view(main_header, header_1, header_2, header_3, header_4, expander=False):
    """
    Create a table view for detection results.
    """    
    if expander:
        with st.expander(main_header):
            col0, col1, col2, col3 = st.columns((0.5, 1, 1, 1))
            col0.header(header_1)
            col1.header(header_2)
            col2.header(header_3)
            col3.header(header_4)
    else:

        st.markdown(f"<h1 style='text-align: center; color: white;'>{main_header}</h1>", unsafe_allow_html=True)
        col0, col1, col2, col3 = st.columns(4)
        col0.header(header_1)
        col1.header(header_2)
        col2.header(header_3)
        col3.header(header_4)
    st.divider() 
    
    return (col0, col1, col2, col3)

def fill_table(cols, value_1, value_2, value_3, value_4):
    col0, col1, col2, col3 = cols
    # visualize results 
    col0.write(value_1)
    col1.write(value_2)
    col2.write(value_3)
    col3.write(value_4)

def while_video(vid_cap, model, model_thresh, frame_window=None):
    # predictions = [] # store predictions
    global predictions
    classes = model.names # get poses
    
    # start video analysis
    while (vid_cap.isOpened()):
        success, frame = vid_cap.read()
        if success:
            
            # settings for live stream
            if frame_window:    
                frame_window.image(frame, channels="BGR", width=1280)

            # get timestamp and results
            timestamp = vid_cap.get(cv2.CAP_PROP_POS_MSEC)                

            results = model(frame, verbose=False)

            for r in results:
                cls = classes[r.probs.top1]
                score = float(r.probs.top1conf.cpu())

                if score >= model_thresh:

                    # check whether there is a new movement or the initial condition
                    if not predictions or predictions[-1]["class"] != cls:
                        
                        # finalize previous movement if exists
                        if predictions:
                            predictions[-1]["final_timestamp"] = timestamp
                            predictions[-1]["duration"] = datetime.timedelta(milliseconds=predictions[-1]["final_timestamp"] - predictions[-1]["start_timestamp"])
                            predictions[-1]["avg_score"] = sum(predictions[-1]["scores"])/len(predictions[-1]["scores"])

                            if predictions[-1]["duration"].total_seconds() < 1:
                                predictions = predictions[:-1]

                        predictions.append(
                            {
                                "class": cls,
                                "scores": [score],
                                "avg_score": None,
                                "final_timestamp": None,
                                "start_timestamp": timestamp,
                                "duration": None
                            }
                        )

                    else:
                        predictions[-1]["scores"].append(score)
                    
        else:
            vid_cap.release()
            break

    if predictions:
        predictions[-1]["final_timestamp"] = timestamp
        predictions[-1]["duration"] = datetime.timedelta(milliseconds=predictions[-1]["final_timestamp"] - predictions[-1]["start_timestamp"])
        predictions[-1]["avg_score"] = sum(predictions[-1]["scores"])/len(predictions[-1]["scores"])

def post_process_predictions(live=False):
    global predictions
    
    if live:
        # since the last prediction would be probably for stopping the video, we remove it
        predictions = predictions[:-1]
    
    cols = _create_table_view("Click here for the detected poses during your routine!", "ID", "Detected Pose", "Duration", "How Confident Are We?", True)

    cleaned_predictions = []

    for i in range(len(predictions)):
        if cleaned_predictions and predictions[i]["class"] == cleaned_predictions[-1]["class"]:
            cleaned_predictions[-1]["final_timestamp"] = predictions[i]["final_timestamp"]
            cleaned_predictions[-1]["scores"].extend(predictions[i]["scores"])
        else:
            cleaned_predictions.append(predictions[i])

    for i in range(len(cleaned_predictions)):
        cleaned_predictions[i]["duration"] = datetime.timedelta(milliseconds=cleaned_predictions[i]["final_timestamp"] - cleaned_predictions[i]["start_timestamp"])
        cleaned_predictions[i]["avg_score"] = sum(cleaned_predictions[i]["scores"])/len(cleaned_predictions[i]["scores"])

        # visualize detection results 
        reference_date = datetime.datetime(1900, 1, 1) # convert timedelta to datetime for visualization
        duration_in_min_sec = reference_date + cleaned_predictions[i]["duration"]
        duration_in_min_sec = duration_in_min_sec.strftime("%M:%S.%f")[:-3]

        fill_table(cols, i, cleaned_predictions[i]["class"], duration_in_min_sec, round(cleaned_predictions[i]["avg_score"], 2))
    
    predictions = [] # clear global parameter for upcoming predictions
    
    return cleaned_predictions

def play_stored_video(model, model_thresh):
    source_vid = "video_1" 

    with open(settings.VIDEOS_DICT.get(source_vid), 'rb') as video_file:
        video_bytes = video_file.read()
    
    if video_bytes:
        width = 50
        side = max((100 - width) / 2, 0.01)

        _, container, _ = st.columns([side, width, side])
        container.markdown("<h5 style='text-align: center; color: white;'>You can see our demo video here!</h5>", unsafe_allow_html=True)
        container.video(data=video_bytes)
         
    # if st.sidebar.button('Detect poses'):
    if st.session_state['DETECT_POSES_BUTTON'] and st.session_state['TABLE_FILLED']:

        with st.spinner("Detecting poses on the demo video..."):
            st.markdown(
                """
                <style>
                    .stSpinner div {
                        text-align:center;
                        align-items: center;
                        justify-content: center;
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )
            try:
                captured_video = cv2.VideoCapture(str(settings.VIDEOS_DICT.get(source_vid)))

                # process the video with YOLO
                while_video(captured_video, model, model_thresh)

                # postprocess and return the final predictions
                return post_process_predictions()
                
            except Exception as e:
                st.sidebar.error("Error during prediction on stored video: " + str(e))
                if settings.DEBUG:
                    st.sidebar.error(traceback.format_exc())

def play_livevideo(model, model_thresh):

    FRAME_WINDOW = st.image([], width=1280)

    stop = st.button("Stop")
    
    if not st.session_state["TABLE_FILLED"]: 
        st.error("Please enter at least one pose before the start!")
        st.stop()
    
    else:
        try: 
            while not stop: # st.session_state['ROUTINE']:
                # start live video
                live_cam = cv2.VideoCapture(settings.WEBCAM_PATH)
                # process the video with YOLO
                while_video(live_cam, model, model_thresh, FRAME_WINDOW)
            
            # postprocess and return the final predictions
            return post_process_predictions(live=True)

        except Exception as e:
            st.sidebar.error("Error during prediction on webcam video: " + str(e))