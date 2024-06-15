import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

with open(CONFIG_FILE, 'r') as file:
    config = json.load(file)

# Path to LDPlayer executable
LDPLAYER_PATH = config.get("ldplayer_path")

# Local base path for video files
LOCAL_BASE_PATH = config.get("local_base_path")

# TikTok package name
TIKTOK_PACKAGE = "com.ss.android.ugc.trill"

# Remote base path on the device
REMOTE_BASE_PATH = "/sdcard/Movies"

# Time to wait for LDPlayer to start (in seconds)
LDPLAYER_START_WAIT = 30

# Delay settings for typing each character (in seconds)
TYPE_DELAY_MIN = 0.1
TYPE_DELAY_MAX = 0.4

# TikTok UI element paths and resource IDs
TIKTOK_UI = {
    'tiktok_icon': {'text': 'TikTok'},
    'first_element': '//*[@resource-id="com.ss.android.ugc.trill:id/hv9"]/android.widget.ImageView[1]',
    'second_element': '//*[@resource-id="com.ss.android.ugc.trill:id/krz"]/android.widget.RelativeLayout[1]/android.widget.FrameLayout[2]',
    'third_element': '//*[@resource-id="com.ss.android.ugc.trill:id/f25"]/android.widget.FrameLayout[1]',
    'fourth_element': '//*[@resource-id="com.ss.android.ugc.trill:id/ncv"]/android.widget.LinearLayout[1]/android.view.ViewGroup[2]',
    'input_box': {'resourceId': 'com.ss.android.ugc.trill:id/io_'},
    'submit_button': {'resourceId': 'com.ss.android.ugc.trill:id/dk4'},
}
