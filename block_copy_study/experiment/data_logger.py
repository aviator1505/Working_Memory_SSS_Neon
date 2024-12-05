# data_logger.py
# experiment/data_logger.py
import csv
import json
from datetime import datetime
import os


class DataLogger:
    def __init__(self, output_dir, participant_id):
        self.output_dir = output_dir
        self.participant_id = participant_id
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.setup_files()

    def setup_files(self):
        os.makedirs(self.output_dir, exist_ok=True)
        base_filename = f"P{self.participant_id:03d}_{self.timestamp}"

        self.files = {
            'trial': f"{self.output_dir}/{base_filename}_trials.csv",
            'gaze': f"{self.output_dir}/{base_filename}_gaze.csv",
            'motion': f"{self.output_dir}/{base_filename}_motion.csv",
            'sync': f"{self.output_dir}/{base_filename}_sync.json"
        }

        self._initialize_files()

    def _initialize_files(self):
        headers = {
            'trial': ['participant_id', 'timestamp', 'posture', 'angle',
                      'trial_num', 'duration'],
            'gaze': ['timestamp', 'trial_num', 'gaze_x', 'gaze_y',
                     'gaze_3d_x', 'gaze_3d_y', 'gaze_3d_z'],
            'motion': ['timestamp', 'trial_num', 'location', 'pitch',
                       'roll', 'yaw', 'quat_w', 'quat_x', 'quat_y', 'quat_z']
        }

        for file_type, header in headers.items():
            with open(self.files[file_type], 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)

    def log_trial(self, trial_data):
        with open(self.files['trial'], 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=trial_data.keys())
            writer.writerow(trial_data)

    def log_sync_stats(self, sync_stats):
        with open(self.files['sync'], 'w') as f:
            json.dump(sync_stats, f, indent=2)