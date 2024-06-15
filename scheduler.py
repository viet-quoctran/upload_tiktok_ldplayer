import schedule
import time
import subprocess
import os
import json
from datetime import datetime

# Path to your main.py script
MAIN_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

def run_main_script(group_name, devices):
    print(f"Running main script for {group_name} at {datetime.now()} with devices: {devices}")
    subprocess.run(["python", MAIN_SCRIPT_PATH, json.dumps(devices)])

def start_scheduler():
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
        
        groups = config.get("groups", [])
        for group in groups:
            group_name = group["name"]
            schedule_time = group["schedule_time"]
            devices = group["devices"]
            
            schedule.every().day.at(schedule_time).do(run_main_script, group_name, devices)
            print(f"Scheduler set to run daily for {group_name} at {schedule_time}")
        
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        print(f"Failed to start scheduler with error: {e}")

if __name__ == "__main__":
    start_scheduler()
