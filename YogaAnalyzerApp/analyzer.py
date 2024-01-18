import settings
import streamlit as st
from helper import _create_table_view, fill_table


def analyze_routine(analysis_level, detected_poses, user_routine, duration_tolerance):
    if analysis_level == settings.BASIC:
        basic_analyzer(detected_poses, user_routine, duration_tolerance)
    elif analysis_level == settings.DETAILED:
        converted_data = convert_user_input(user_routine)
        detailed_analyzer(converted_data, detected_poses)

def convert_user_input(data):
    poses = data['Pose']
    minutes_list = data['Minutes']
    seconds_list = data['Seconds']

    result = []

    for i in range(len(poses)):
        minutes = minutes_list[i]
        seconds = seconds_list[i]

        total_seconds = minutes * 60 + seconds

        result.append({"class": poses[i], "duration": total_seconds})

    return result

def basic_analyzer(detected_poses, user_routine, duration_tolerance):
    """
    Check whether the detected poses are in the user's routine, and
    if in the routine compare the planned & actual durations.
    Input:
        detected_poses: list of detected poses
        user_routine: list of user's routine
    Output:
        routine_check: dictionary of detected poses and their 
        presence in the user's routine
    """
    cols = _create_table_view("Yoga Routine Basic Analysis Results", "Pose in the routine", "Is detected?", "Duration for the pose", "Is fulfilled?")

    if settings.DEBUG:
        print(detected_poses)
        print(user_routine)

    detected, routine = get_merged_poses(detected_poses, user_routine)

    if settings.DEBUG:
        print(detected_poses)
        print(user_routine)

    routine_check = {}

    for pose, duration in routine.items():
        pose_detected = "❌"
        duration_fulfilled = "❌"
        if pose in detected:
            pose_detected = "✅"
            if duration*(100-duration_tolerance)/100 <= duration <= duration*(100+duration_tolerance)/100:
                duration_fulfilled = "✅"

        minutes, remaining_seconds = divmod(duration, 60)

        fill_table(cols, pose, pose_detected, f"{minutes:02}:{remaining_seconds:02} ± {duration_tolerance}%", duration_fulfilled)
        
        routine_check[pose] = pose in detected

def get_merged_poses(detected_poses, user_routine):
    detected = {}
    routine = {}

    for pose in detected_poses:
        if pose["class"] not in detected:
            detected[pose["class"]] = pose["duration"]
        else:
            detected[pose["class"]] += pose["duration"]

    for i in range(len(user_routine["Pose"])):
        planned_duration = (user_routine["Minutes"][i])*60 + user_routine["Seconds"][i]
        if user_routine["Pose"][i] not in routine:
            routine[user_routine["Pose"][i]] = planned_duration
        else:
            routine[user_routine["Pose"][i]] += planned_duration

    return detected, routine

def calculate_overall_score_detailed(duration_diff, confidence_scores, duration_weight=0.70, confidence_weight=0.3):
    overall_data = {
        "duration": {},
        "confidence": {}
        }
    overall_score = {}

    for pose_n_duration in duration_diff:
        pose, duration = pose_n_duration["class"], pose_n_duration["difference"]
        if pose not in overall_data["duration"]:
            overall_data["duration"][pose] = duration
        else:
            overall_data["duration"][pose] += duration
    
    for pose_n_conf in confidence_scores:
        pose, conf = pose_n_conf["class"], pose_n_conf["score"]
        if pose not in overall_data["confidence"]:
            overall_data["confidence"][pose] = conf
        else:
            overall_data["confidence"][pose] += conf
    
    for pose in set(overall_data["duration"].keys()) | set(overall_data["confidence"].keys()):
        # Use 0 if not present in one of the dictionaries
        duration_difference = overall_data["duration"].get(pose, 0)
        confidence_score = overall_data["confidence"].get(pose, 0)

        # Combine duration and confidence scores using specified weights
        overall_score[pose] = duration_weight * duration_difference + confidence_weight * confidence_score
    
    return overall_score

def detailed_analyzer(user_poses, actual_poses):
    duration_diff = []
    confidence_scores = []

    user_pose_names = {pose["class"] for pose in user_poses}

    for user_pose in user_poses:
        user_pose_name, user_duration = user_pose["class"], user_pose["duration"]

        matching_poses = [pose for pose in actual_poses if pose["class"] == user_pose_name]

        # if there is a missing pose in the actual routine 
        if not matching_poses:
            # consider it as a negative effect
            duration_diff.append({"class": user_pose_name, "difference": -user_duration})
            continue

        for actual_pose in matching_poses:
            actual_duration, actual_score = actual_pose["duration"].total_seconds(), actual_pose["avg_score"]

            # calculate duration difference
            duration_diff.append({"class": user_pose_name, "difference": abs(user_duration - actual_duration)})

            # collect confidence scores
            confidence_scores.append({"class": user_pose_name, "score": actual_score})

    # if there is an additional pose in the actual routine, but it's not in the inputs
    for actual_pose in actual_poses:
        actual_pose_name = actual_pose["class"]
        if actual_pose_name not in user_pose_names:
            # consider it as a negative effect
            duration_diff.append({"class": actual_pose_name, "difference": -actual_pose["duration"].total_seconds()})
            confidence_scores.append({"class": actual_pose_name, "score": -actual_pose["avg_score"]})

    classes_duration = [pose["class"] for pose in duration_diff]
    differences_duration = [pose["difference"] for pose in duration_diff]

    classes_confidence = [pose["class"] for pose in confidence_scores]
    confidence_values = [pose["score"] for pose in confidence_scores]

    st.markdown("<h1 style='text-align: center; color: white;'>Yoga Routine Detailed Analysis Results</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # chart for duration differences
    with col1:
        st.subheader("Duration Difference")
        chart_data_duration = {pose: diff for pose, diff in zip(classes_duration, differences_duration)}
        st.bar_chart(chart_data_duration, use_container_width=True)

    # chart for confidence scores
    with col2:
        st.subheader("Confidence Scores")
        chart_data_confidence = {pose: score for pose, score in zip(classes_confidence, confidence_values)}
        st.bar_chart(chart_data_confidence, use_container_width=True)

    with col3:
        # overall score of the whole routine
        overall_score = calculate_overall_score_detailed(duration_diff, confidence_scores)
        st.subheader("Overall Score of Your Routine")
        st.bar_chart(overall_score, use_container_width=True)