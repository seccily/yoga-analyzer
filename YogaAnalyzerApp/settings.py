from pathlib import Path
import sys

# Get the absolute path of the current file
file_path = Path(__file__).resolve()

# Get the parent directory of the current file
root_path = file_path.parent

# Add the root path to the sys.path list if it is not already there
if root_path not in sys.path:
    sys.path.append(str(root_path))

# Get the relative path of the root directory with respect to the current working directory
ROOT = root_path.relative_to(Path.cwd())

# Sources
VIDEO = 'Demo Video'
LIVE = 'Webcam'
SOURCES_LIST = [
    VIDEO, 
    LIVE
] 

# Yogi level
BEGINNER = "Beginner"
ADVANCED = "Advanced"
YOGI_LIST = [
    BEGINNER,
    ADVANCED,
]

# Analysis level
BASIC = "Basic"
DETAILED = "Detailed"
ANALYSIS_LIST = [
    BASIC,
    DETAILED
]

# Videos config
VIDEO_DIR = ROOT / 'videos'
VIDEO_1_PATH = VIDEO_DIR / 'video_1_trimmed.mp4'
VIDEOS_DICT = {
    'video_1': VIDEO_1_PATH
}

YES_NO_LIST = [
    "Yes",
    "No"
]

# Webcam config
WEBCAM_PATH = 0

# ML Model config
MODEL_DIR = ROOT / 'weights'
BEGINNER_MODEL = MODEL_DIR / 'beginner.pt'  # 5-CLASS
ADVANCED_MODEL = MODEL_DIR / 'advanced.pt'  # 47-CLASS

DEBUG = False 