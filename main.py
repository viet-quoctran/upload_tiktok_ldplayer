import uiautomator2 as u2
import time
import threading
import subprocess
import random
import os
import re
import sys
import json
from queue import Queue
from icecream import ic
from settings import *
import datetime

sys.stdout.reconfigure(encoding='utf-8')

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

def start_ldplayer(index):
    subprocess.run([LDPLAYER_PATH, "launch", "--index", str(index)])
    time.sleep(LDPLAYER_START_WAIT)

def stop_ldplayer(index):
    subprocess.run([LDPLAYER_PATH, "quit", "--index", str(index)])

def get_lowest_sequence_video(folder_path):
    try:
        videos = [v for v in os.listdir(folder_path) if re.match(r'.+-\d+\.mp4$', v)]
        videos.sort(key=lambda v: int(re.search(r'-(\d+)\.mp4$', v).group(1)))
        return videos[0] if videos else None
    except Exception as e:
        print(f"Failed to get lowest sequence video in {folder_path} with error: {e}")
        return None

def push_video(d, index, local_base_path, remote_base_path=REMOTE_BASE_PATH):
    device_folder_path = os.path.join(local_base_path, str(index))
    
    if not os.path.exists(device_folder_path):
        print(f"Folder {device_folder_path} does not exist.")
        return

    video_file = get_lowest_sequence_video(device_folder_path)
    
    if not video_file:
        print(f"No video files found in {device_folder_path}.")
        return
    
    local_file_path = os.path.join(device_folder_path, video_file)
    try:
        d.push(local_file_path, remote_base_path)
        print(f"File {local_file_path} has been pushed to {remote_base_path} on device {d.serial}")

        d.shell(['am', 'broadcast', '-a', 'android.intent.action.MEDIA_SCANNER_SCAN_FILE', '-d', f'file://{remote_base_path}/{video_file}'])
        
        return video_file, remote_base_path
    except Exception as e:
        print(f"Failed to push video {local_file_path} with error: {e}")
        return None, None

def check_video_exists(d, video_file_name, remote_base_path=REMOTE_BASE_PATH):
    try:
        files = d.shell(['ls', remote_base_path]).output.split('\n')
        return any(video_file_name in file for file in files)
    except Exception as e:
        print(f"Failed to check video exists on {remote_base_path} with error: {e}")
        return False

def delete_video(d, video_file_name, remote_base_path):
    try:
        d.shell(['rm', f'{remote_base_path}/{video_file_name}'])
        print(f"Deleted {video_file_name} from device {d.serial}")
    except Exception as e:
        print(f"Failed to delete {video_file_name} from device {d.serial} with error: {e}")

def delete_local_video(video_file_name, index, local_base_path):
    local_file_path = os.path.join(local_base_path, str(index), video_file_name)
    try:
        os.remove(local_file_path)
        print(f"Deleted {local_file_path} from local storage")
    except Exception as e:
        print(f"Failed to delete {local_file_path} from local storage with error: {e}")

def send_keys_slowly(d, text):
    for char in text:
        d.send_keys(char)
        time.sleep(random.uniform(TYPE_DELAY_MIN, TYPE_DELAY_MAX))

def swipe_up(d):
    # Get the screen size
    size = d.window_size()
    width = size[0]
    height = size[1]

    # Calculate the start and end points for the swipe
    start_x = width // 2
    start_y = height * 3 // 4
    end_x = width // 2
    end_y = height // 4

    # Perform random swipes
    swipe_count = random.randint(3, 5)
    for _ in range(swipe_count):
        d.swipe(start_x, start_y, end_x, end_y, duration=0.1)  # Adjust duration for faster swipe
        sleep_time = random.uniform(1, 2)  # Reduce sleep time for faster action
        time.sleep(sleep_time)  # Add a delay to simulate human interaction



def check_and_restore(d):
    # Check if the "Restore" button is present and click it if so
    if d(text="Restore").exists:
        d(text="Restore").click()
        print("Clicked 'Restore' button")
        time.sleep(5)  # Wait for the restore process to complete

def perform_action(d, action, *args, **kwargs):
    # Perform the action
    action(*args, **kwargs)
    # Check and restore if needed
    check_and_restore(d)

def automate_device(index, serial, local_base_path, video_count):
    while True:
        try:
            d = u2.connect_usb(serial)
            ic(f"Successfully connected to device {serial}")
            break
        except Exception as e:
            ic(f"Failed to connect to device {serial} with error: {e}. Retrying in 10 seconds...")
            time.sleep(10)  # Wait before retrying

    for _ in range(video_count):
        pushed_video_name, remote_base_path = push_video(d, index, local_base_path)

        if not pushed_video_name:
            return

        d.shell(['am', 'broadcast', '-a', 'android.intent.action.MEDIA_MOUNTED', '-d', f'file://{remote_base_path}'])

        if not check_video_exists(d, pushed_video_name, remote_base_path):
            print(f"Video {pushed_video_name} không tồn tại trên thiết bị {serial}.")
            return

        while True:
            try:
                perform_action(d, lambda: d(text=TIKTOK_UI['tiktok_icon']['text']).click())
                time.sleep(60)

                swipe_up(d)
                
                perform_action(d, lambda: d.xpath(TIKTOK_UI['first_element']).click())
                time.sleep(5)

                perform_action(d, lambda: d.xpath(TIKTOK_UI['second_element']).click())
                time.sleep(5)

                perform_action(d, lambda: d.xpath(TIKTOK_UI['third_element']).click())
                time.sleep(5)

                perform_action(d, lambda: d.xpath(TIKTOK_UI['fourth_element']).click())
                time.sleep(5)
                perform_action(d, lambda: d(resourceId=TIKTOK_UI['input_box']['resourceId']).click())
                time.sleep(5)
                perform_action(d, lambda: d(resourceId=TIKTOK_UI['submit_button']['resourceId']).click())
                time.sleep(5)
                send_keys_slowly(d, pushed_video_name.split('.')[0])
                break

            except Exception as e:
                print(f"Lỗi: {e}. Bắt đầu lại quy trình.")
                d.app_stop(TIKTOK_PACKAGE)
                time.sleep(5)

        delete_video(d, pushed_video_name, remote_base_path)
        delete_local_video(pushed_video_name, index, local_base_path)

def start_and_automate(index, serial, local_base_path, video_count, semaphore):
    with semaphore:
        try:
            start_ldplayer(index)
            automate_device(index, serial, local_base_path, video_count)
        except Exception as e:
            print(f"Error in start_and_automate for device {serial} with error: {e}")
        finally:
            stop_ldplayer(index)

def run_automation(group):
    devices_info = group["devices"]
    local_base_path = LOCAL_BASE_PATH
    max_threads = group["max_threads"]
    semaphore = threading.Semaphore(max_threads)
    threads = []
    for device in devices_info:
        if device["video_count"] > 0:
            index = device["index"]
            serial = device["serial"]
            video_count = device["video_count"]
            thread = threading.Thread(target=start_and_automate, args=(index, serial, local_base_path, video_count, semaphore))
            threads.append(thread)
            thread.start()
    for thread in threads:
        thread.join()

def should_run_now(schedule_time):
    current_time = datetime.datetime.now().time()
    scheduled_time = datetime.datetime.strptime(schedule_time, "%H:%M").time()
    return current_time.hour == scheduled_time.hour and current_time.minute == scheduled_time.minute

def run_scheduled_automations():
    while True:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            groups = config.get('groups', [])
            current_time = datetime.datetime.now().time()

            # Find groups that should run now
            groups_to_run = [group for group in groups if group["is_scheduler"] and should_run_now(group["schedule_time"])]

            # Run each group in a separate thread
            threads = []
            for group in groups_to_run:
                thread = threading.Thread(target=run_automation, args=(group,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

        time.sleep(60)  # Check again every minute

if __name__ == "__main__":
    run_scheduled_automations()
