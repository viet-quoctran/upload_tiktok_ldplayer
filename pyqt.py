import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QTimeEdit, QPushButton, QVBoxLayout, 
                             QMessageBox, QLineEdit, QGroupBox, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QComboBox, QGridLayout, QSpinBox, QFileDialog, QScrollArea)
from PyQt5.QtCore import QTime, Qt
import json
import os
import subprocess

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
SCHEDULER_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scheduler.py")

class SchedulerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_config()

    def initUI(self):
        self.setWindowTitle('Scheduler GUI')
        self.setGeometry(100, 100, 600, 500)

        main_layout = QVBoxLayout()

        # System Group
        system_group = QGroupBox('System Settings')
        system_layout = QGridLayout()

        self.ldplayer_path_label = QLabel('LDPlayer Path:')
        system_layout.addWidget(self.ldplayer_path_label, 0, 0)
        self.ldplayer_path_input = QLineEdit()
        system_layout.addWidget(self.ldplayer_path_input, 0, 1, 1, 2)
        self.browse_ldplayer_button = QPushButton('Browse')
        self.browse_ldplayer_button.clicked.connect(self.browse_ldplayer_path)
        system_layout.addWidget(self.browse_ldplayer_button, 0, 3)

        self.local_base_path_label = QLabel('Video Path:')
        system_layout.addWidget(self.local_base_path_label, 1, 0)
        self.local_base_path_input = QLineEdit()
        system_layout.addWidget(self.local_base_path_input, 1, 1, 1, 2)
        self.browse_local_base_button = QPushButton('Browse')
        self.browse_local_base_button.clicked.connect(self.browse_local_base_path)
        system_layout.addWidget(self.browse_local_base_button, 1, 3)

        self.save_paths_button = QPushButton('Save/Refresh Paths')
        self.save_paths_button.clicked.connect(self.save_paths)
        self.save_paths_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        system_layout.addWidget(self.save_paths_button, 2, 3)

        system_group.setLayout(system_layout)
        main_layout.addWidget(system_group)

        # Group Settings
        group_group = QGroupBox('Group Settings')
        group_layout = QGridLayout()

        self.group_select_label = QLabel('Select Group:')
        group_layout.addWidget(self.group_select_label, 0, 0)

        self.group_select_combo = QComboBox()
        self.group_select_combo.currentIndexChanged.connect(self.load_group_data)
        group_layout.addWidget(self.group_select_combo, 0, 1, 1, 2)

        self.add_group_button = QPushButton('New Group')
        self.add_group_button.clicked.connect(self.add_group)
        self.add_group_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        group_layout.addWidget(self.add_group_button, 0, 3)

        self.save_group_button = QPushButton('Save Group')
        self.save_group_button.clicked.connect(self.save_group)
        self.save_group_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        group_layout.addWidget(self.save_group_button, 1, 3)

        self.delete_group_button = QPushButton('Delete Group')
        self.delete_group_button.clicked.connect(self.delete_group)
        self.delete_group_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        group_layout.addWidget(self.delete_group_button, 2, 3)

        self.group_name_label = QLabel('Group Name:')
        group_layout.addWidget(self.group_name_label, 1, 0)

        self.group_name_input = QLineEdit()
        group_layout.addWidget(self.group_name_input, 1, 1, 1, 2)

        self.time_label = QLabel('Set Schedule Time (HH:MM):')
        group_layout.addWidget(self.time_label, 2, 0)

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat('HH:mm')
        self.time_edit.setTime(QTime.currentTime())
        group_layout.addWidget(self.time_edit, 2, 1, 1, 2)

        self.max_threads_label = QLabel('Max Threads:')
        group_layout.addWidget(self.max_threads_label, 3, 0)

        self.max_threads_spinbox = QSpinBox()
        self.max_threads_spinbox.setRange(1, 100)
        self.max_threads_spinbox.setValue(2)
        group_layout.addWidget(self.max_threads_spinbox, 3, 1, 1, 2)

        self.devices_label = QLabel('Devices (ID:Name):')
        group_layout.addWidget(self.devices_label, 4, 0, 1, 4)

        self.devices_list = QListWidget()
        self.devices_list.itemClicked.connect(self.load_device_data)

        # Add a scroll area for devices list
        devices_scroll_area = QScrollArea()
        devices_scroll_area.setWidgetResizable(True)
        devices_scroll_area.setWidget(self.devices_list)
        group_layout.addWidget(devices_scroll_area, 5, 0, 1, 4)

        self.device_index_input = QLineEdit()
        self.device_index_input.setPlaceholderText("ID")
        group_layout.addWidget(self.device_index_input, 6, 0)

        self.device_serial_input = QLineEdit()
        self.device_serial_input.setPlaceholderText("Name")
        group_layout.addWidget(self.device_serial_input, 6, 1)

        self.video_count_label = QLabel('Video Count:')
        group_layout.addWidget(self.video_count_label, 6, 2)

        self.video_count_input = QSpinBox()
        self.video_count_input.setRange(1, 100)  # Số lượng video tối đa có thể đăng lên
        group_layout.addWidget(self.video_count_input, 6, 3)

        button_layout = QHBoxLayout()

        self.add_device_button = QPushButton('Add Device')
        self.add_device_button.clicked.connect(self.add_device)
        self.add_device_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        button_layout.addWidget(self.add_device_button)

        self.update_device_button = QPushButton('Update Device')
        self.update_device_button.clicked.connect(self.update_device)
        self.update_device_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        button_layout.addWidget(self.update_device_button)

        self.delete_device_button = QPushButton('Delete Device')
        self.delete_device_button.clicked.connect(self.delete_device)
        self.delete_device_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        button_layout.addWidget(self.delete_device_button)

        group_layout.addLayout(button_layout, 7, 0, 1, 4)

        self.groups_list = QListWidget()
        self.groups_list.itemClicked.connect(self.select_group_from_list)

        # Add a scroll area for groups list
        groups_scroll_area = QScrollArea()
        groups_scroll_area.setWidgetResizable(True)
        groups_scroll_area.setWidget(self.groups_list)
        group_layout.addWidget(groups_scroll_area, 8, 0, 1, 4)

        group_group.setLayout(group_layout)
        main_layout.addWidget(group_group)

        # Scheduler Controls
        control_layout = QHBoxLayout()
        self.start_button = QPushButton('Start Scheduler')
        self.start_button.clicked.connect(self.start_scheduler)
        self.start_button.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop Scheduler')
        self.stop_button.clicked.connect(self.stop_scheduler)
        self.stop_button.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        control_layout.addWidget(self.stop_button)

        main_layout.addLayout(control_layout)
        self.setLayout(main_layout)

        # Load configuration after initializing UI elements
        self.load_config()
        self.update_groups_list()  # Ensure the groups are listed when UI is initialized

    def browse_ldplayer_path(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select LDPlayer Path', '', 'Executable Files (*.exe)')
        if path:
            self.ldplayer_path_input.setText(path)

    def browse_local_base_path(self):
        path = QFileDialog.getExistingDirectory(self, 'Select Local Base Path')
        if path:
            self.local_base_path_input.setText(path)
            self.update_video_counts()  # Update video counts when the base path is changed

    def save_paths(self):
        ldplayer_path = self.ldplayer_path_input.text().replace("/", "\\\\")
        local_base_path = self.local_base_path_input.text().replace("/", "\\\\")

        if not ldplayer_path or not local_base_path:
            QMessageBox.warning(self, 'Error', 'Please provide both LDPlayer Path and Local Base Path.')
            return

        self.config["ldplayer_path"] = ldplayer_path
        self.config["local_base_path"] = local_base_path

        self.save_config()
        self.update_video_counts()  # Update video counts after saving paths
        QMessageBox.information(self, 'Settings Saved', 'Paths have been saved successfully.')

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as file:
                self.config = json.load(file)
                self.groups = self.config.get('groups', [])
                
                # Replace double backslashes with single backslashes for UI display
                ldplayer_path = self.config.get('ldplayer_path', '').replace("\\\\", "\\")
                local_base_path = self.config.get('local_base_path', '').replace("\\\\", "\\")

                self.ldplayer_path_input.setText(ldplayer_path)
                self.local_base_path_input.setText(local_base_path)
                
                self.update_group_select_combo()
                self.update_groups_list()
                if self.groups:
                    self.group_select_combo.setCurrentIndex(0)
                    self.load_group_data()
                else:
                    self.max_threads_spinbox.setValue(0)  # Set max_threads to 0 when there are no groups
                    self.update_input_fields(False)  # Disable input fields when no groups exist
        else:
            self.config = {"groups": []}
            self.max_threads_spinbox.setValue(0)  # Set max_threads to 0 when there are no groups
            self.update_input_fields(False)  # Disable input fields when no groups exist

    def update_input_fields(self, enable):
        self.group_name_input.setEnabled(enable)
        self.time_edit.setEnabled(enable)
        self.max_threads_spinbox.setEnabled(enable)
        self.device_index_input.setEnabled(enable)
        self.device_serial_input.setEnabled(enable)
        self.video_count_input.setEnabled(enable)
        self.add_device_button.setEnabled(enable)
        self.update_device_button.setEnabled(enable)
        self.delete_device_button.setEnabled(enable)
        self.save_group_button.setEnabled(enable)
        self.delete_group_button.setEnabled(enable)
        
    def save_config(self):
        self.config["groups"] = self.groups
        self.config["ldplayer_path"] = self.ldplayer_path_input.text().replace("/", "\\\\")
        self.config["local_base_path"] = self.local_base_path_input.text().replace("/", "\\\\")
        with open(CONFIG_FILE, 'w') as file:
            json.dump(self.config, file, indent=4)

    def update_group_select_combo(self):
        self.group_select_combo.blockSignals(True)
        self.group_select_combo.clear()
        for group in self.groups:
            self.group_select_combo.addItem(group["name"])
        self.group_select_combo.blockSignals(False)
        print(f"Number of groups loaded: {len(self.groups)}")  # Debugging line to check number of groups

    def update_video_counts(self):
        local_base_path = self.local_base_path_input.text()
        for group in self.groups:
            for device in group["devices"]:
                device_path = os.path.join(local_base_path, str(device["index"]))
                if os.path.exists(device_path):
                    video_files = [f for f in os.listdir(device_path) if os.path.isfile(os.path.join(device_path, f))]
                    device["video_not_post"] = len(video_files)
                    if device["video_not_post"] == 0:
                        device["video_count"] = 0
                else:
                    device["video_not_post"] = 0
                    device["video_count"] = 0
        self.save_config()
        self.update_groups_list()
        self.load_group_data()


    def load_group_data(self):
        index = self.group_select_combo.currentIndex()
        if 0 <= index < len(self.groups):
            group = self.groups[index]
            self.group_name_input.setText(group["name"])
            self.time_edit.setTime(QTime.fromString(group["schedule_time"], "HH:mm"))
            self.max_threads_spinbox.setValue(group.get("max_threads", 2))
            self.max_threads_spinbox.setMaximum(len(group["devices"]))  # Set maximum value based on the number of devices
            self.devices_list.clear()
            for device in group["devices"]:
                item_text = f'{device["index"]}:{device["serial"]} - {device["video_count"]} videos - {device["video_not_post"]} not posted'
                item = QListWidgetItem(item_text)
                self.devices_list.addItem(item)
            self.update_scheduler_buttons()


    def select_group_from_list(self, item):
        group_name = item.text().split(' - ')[0]
        for index, group in enumerate(self.groups):
            if group["name"] == group_name:
                self.group_select_combo.setCurrentIndex(index)
                break

    def clear_group_data(self):
        self.group_select_combo.setCurrentIndex(-1)
        self.group_name_input.clear()
        self.time_edit.setTime(QTime.currentTime())
        self.max_threads_spinbox.setValue(2)
        self.max_threads_spinbox.setMaximum(1)  # Default maximum to 1 when no devices are present
        self.devices_list.clear()
        self.update_scheduler_buttons()

    def save_group(self):
        group_name = self.group_name_input.text()
        schedule_time = self.time_edit.time().toString('HH:mm')
        max_threads = self.max_threads_spinbox.value()

        if not group_name:
            QMessageBox.warning(self, 'Error', 'Group name cannot be empty.')
            return

        if max_threads == 0:
            QMessageBox.warning(self, 'Error', 'Max threads must be greater than 0.')
            return

        devices = []
        for i in range(self.devices_list.count()):
            item = self.devices_list.item(i)
            device_str = item.text()
            try:
                device_info = device_str.split(" - ")
                index_serial = device_info[0].split(":")
                device_index = index_serial[0]
                device_serial = index_serial[1]
                video_count = int(device_info[1].split(" ")[0])
                video_not_post = int(device_info[2].split(" ")[0])

                if video_not_post == 0:
                    video_count = 0

                devices.append({"index": int(device_index), "serial": device_serial, "video_count": video_count, "video_not_post": video_not_post})
            except ValueError as e:
                QMessageBox.warning(self, 'Error', f'Invalid device format: {e}. Please use the format index:serial - video_count videos - video_not_post not posted.')
                return

        group_data = {
            "name": group_name,
            "schedule_time": schedule_time,
            "devices": devices,
            "is_scheduler": self.groups[self.group_select_combo.currentIndex()]["is_scheduler"] if self.group_select_combo.currentIndex() != -1 else False,
            "max_threads": max_threads
        }

        index = self.group_select_combo.currentIndex()

        if index == -1:  # Adding a new group
            if any(group["name"] == group_name for group in self.groups):
                QMessageBox.warning(self, 'Error', 'Group name already exists. Please choose a different name.')
                return
            self.groups.append(group_data)
        else:  # Updating an existing group
            if any(group["name"] == group_name for i, group in enumerate(self.groups) if i != index):
                QMessageBox.warning(self, 'Error', 'Group name already exists. Please choose a different name.')
                return
            self.groups[index] = group_data

        self.save_config()
        self.update_group_select_combo()
        self.update_groups_list()
        self.update_input_fields(True)  # Enable input fields when a group is saved

        if self.groups[index]["is_scheduler"]:
            self.schedule_group(index)

        # Reset the current index to the saved index to keep the selection
        self.group_select_combo.setCurrentIndex(index)


    def schedule_group(self, index):
        group = self.groups[index]
        schedule_time = group["schedule_time"]
        subprocess.Popen(["python", SCHEDULER_SCRIPT_PATH, schedule_time])

    def add_group(self):
        self.group_select_combo.setCurrentIndex(-1)
        self.group_name_input.clear()
        self.time_edit.setTime(QTime.currentTime())
        self.max_threads_spinbox.setValue(2)
        self.max_threads_spinbox.setMaximum(1)  # Default maximum to 1 when no devices are present
        self.devices_list.clear()
        self.update_scheduler_buttons()
        self.update_input_fields(True)  # Enable input fields when adding a new group

    def add_device(self):
        device_index = self.device_index_input.text()
        device_serial = self.device_serial_input.text()
        video_count = self.video_count_input.value()
        video_not_post = 0

        if self.local_base_path_input.text():
            device_path = os.path.join(self.local_base_path_input.text(), device_index)
            if os.path.exists(device_path):
                video_files = [f for f in os.listdir(device_path) if os.path.isfile(os.path.join(device_path, f))]
                video_not_post = len(video_files)

        for i in range(self.devices_list.count()):
            item = self.devices_list.item(i)
            if item.text().split(":")[0] == device_index or item.text().split(":")[1].split(" - ")[0] == device_serial:
                QMessageBox.warning(self, 'Error', 'ID hoặc tên thiết bị đã tồn tại trong danh sách.')
                return

        if not device_index or not device_serial:
            QMessageBox.warning(self, 'Error', 'Vui lòng cung cấp cả ID và tên cho thiết bị.')
            return

        self.video_count_input.setMaximum(video_not_post)  # Cập nhật giới hạn tối đa cho video_count

        item_text = f'{device_index}:{device_serial} - {video_count} videos - {video_not_post} not posted'
        item = QListWidgetItem(item_text)
        self.devices_list.addItem(item)
        self.device_index_input.clear()
        self.device_serial_input.clear()
        self.video_count_input.setValue(0)
        self.update_group_devices()

    def load_device_data(self, item):
        try:
            device_text = item.text()
            device_index, remaining = device_text.split(":")
            device_serial, video_count_text, video_not_post_text = remaining.split(" - ")
            video_count = int(video_count_text.split(" ")[0])
            video_not_post = int(video_not_post_text.split(" ")[0])

            self.device_index_input.setText(device_index)
            self.device_serial_input.setText(device_serial)
            self.video_count_input.setMaximum(video_not_post)  # Cập nhật giới hạn tối đa cho video_count
            self.video_count_input.setValue(video_count)
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Định dạng thiết bị không hợp lệ.')

    def update_device(self):
        current_item = self.devices_list.currentItem()
        if current_item:
            device_index = self.device_index_input.text()
            device_serial = self.device_serial_input.text()
            video_count = self.video_count_input.value()  # Đảm bảo sử dụng đúng tên thuộc tính
            video_not_post = 0

            if self.local_base_path_input.text():
                device_path = os.path.join(self.local_base_path_input.text(), device_index)
                if os.path.exists(device_path):
                    video_files = [f for f in os.listdir(device_path) if os.path.isfile(os.path.join(device_path, f))]
                    video_not_post = len(video_files)

            if not device_index or not device_serial:
                QMessageBox.warning(self, 'Error', 'Vui lòng cung cấp cả ID và tên cho thiết bị.')
                return

            self.video_count_input.setMaximum(video_not_post)  # Cập nhật giới hạn tối đa cho video_count

            item_text = f'{device_index}:{device_serial} - {video_count} videos - {video_not_post} not posted'
            current_item.setText(item_text)
            self.device_index_input.clear()
            self.device_serial_input.clear()
            self.video_count_input.setValue(0)
            self.update_group_devices()
        else:
            QMessageBox.warning(self, 'Error', 'Vui lòng chọn một thiết bị để cập nhật.')

    def delete_device(self):
        current_row = self.devices_list.currentRow()
        if current_row >= 0:
            self.devices_list.takeItem(current_row)
            self.update_group_devices()
        else:
            QMessageBox.warning(self, 'Error', 'Please select a device to delete.')

    def update_group_devices(self):
        index = self.group_select_combo.currentIndex()
        if 0 <= index < len(self.groups):
            devices = []
            for i in range(self.devices_list.count()):
                item = self.devices_list.item(i)
                device_index, remaining = item.text().split(":")
                device_serial, video_count_text, video_not_post_text = remaining.split(" - ")
                video_count = int(video_count_text.split(" ")[0])
                video_not_post = int(video_not_post_text.split(" ")[0])
                devices.append({"index": int(device_index), "serial": device_serial, "video_count": video_count, "video_not_post": video_not_post})
            self.groups[index]["devices"] = devices
            self.max_threads_spinbox.setMaximum(len(devices))  # Set maximum value based on the number of devices
            self.save_config()
            self.update_groups_list()
            if self.groups[index]["is_scheduler"]:
                self.schedule_group(index)

    def delete_group(self):
        index = self.group_select_combo.currentIndex()
        if 0 <= index < len(self.groups):
            del self.groups[index]
            self.save_config()
            self.update_group_select_combo()
            self.update_groups_list()
            QMessageBox.information(self, 'Scheduler', 'Group deleted successfully.')
        else:
            QMessageBox.warning(self, 'Scheduler', 'Please select a group to delete.')

    def update_groups_list(self):
        self.groups_list.clear()
        for group in self.groups:
            item_text = f'{group["name"]} - {group["schedule_time"]} - {len(group["devices"])} devices'
            item = QListWidgetItem(item_text)

            if group.get("is_scheduler", False):
                item.setBackground(Qt.green)
                item.setForeground(Qt.black)
                item.setToolTip("Scheduled")
            else:
                item.setBackground(Qt.red)
                item.setForeground(Qt.white)
                item.setToolTip("Not Scheduled")

            self.groups_list.addItem(item)
            print(f'Added group: {item_text}')  # Debugging line
        self.update_scheduler_buttons()

    def start_scheduler(self):
        index = self.group_select_combo.currentIndex()
        if 0 <= index < len(self.groups):
            group_name = self.group_name_input.text()
            max_threads = self.max_threads_spinbox.value()
            
            if not group_name:
                QMessageBox.warning(self, 'Error', 'Group name cannot be empty.')
                return
            
            if max_threads == 0:
                QMessageBox.warning(self, 'Error', 'Max threads must be greater than 0.')
                return
            
            if len(self.groups[index]["devices"]) == 0:
                QMessageBox.warning(self, 'Scheduler', 'No devices in the selected group. Please add devices before starting the scheduler.')
                return
            
            self.groups[index]["is_scheduler"] = True
            self.save_config()
            self.update_groups_list()
            self.update_scheduler_buttons()
            self.schedule_group(index)
            QMessageBox.information(self, 'Scheduler', f'Scheduler started for {self.groups[index]["name"]}')
        else:
            QMessageBox.warning(self, 'Scheduler', 'Please select a group to start scheduler.')

    def stop_scheduler(self):
        index = self.group_select_combo.currentIndex()
        if 0 <= index < len(self.groups):
            self.groups[index]["is_scheduler"] = False
            self.save_config()
            self.update_groups_list()
            self.update_scheduler_buttons()
            QMessageBox.information(self, 'Scheduler', f'Scheduler stopped for {self.groups[index]["name"]}')
        else:
            QMessageBox.warning(self, 'Scheduler', 'Please select a group to stop scheduler.')

    def update_scheduler_buttons(self):
        index = self.group_select_combo.currentIndex()
        if 0 <= index < len(self.groups):
            is_scheduler = self.groups[index].get("is_scheduler", False)
            if is_scheduler:
                self.start_button.setEnabled(False)
                self.start_button.setStyleSheet("background-color: #D3D3D3; color: white; font-weight: bold;")
                self.stop_button.setEnabled(True)
                self.stop_button.setStyleSheet("background-color: red; color: white; font-weight: bold;")
            else:
                self.start_button.setEnabled(True)
                self.start_button.setStyleSheet("background-color: green; color: white; font-weight: bold;")
                self.stop_button.setEnabled(False)
                self.stop_button.setStyleSheet("background-color: #D3D3D3; color: white; font-weight: bold;")
        else:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.start_button.setStyleSheet("background-color: #D3D3D3; color: white; font-weight: bold;")
            self.stop_button.setStyleSheet("background-color: #D3D3D3; color: white; font-weight: bold;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SchedulerApp()
    ex.show()
    sys.exit(app.exec_())

