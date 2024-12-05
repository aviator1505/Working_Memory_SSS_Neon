# trial_manager.py
# experiment/trial_manager.py
from itertools import permutations
import numpy as np
import time
import csv
from datetime import datetime
from hardware.eye_tracker import NeonEyeTracker
from hardware.motion_tracker import MotionTracker
from hardware.synchronizer import DataSynchronizer


class BlockCopyExperiment:
    def __init__(self, participant_id, output_dir="data/"):
        self.participant_id = participant_id
        self.output_dir = output_dir
        self.setup_experimental_conditions()
        self.setup_data_collection()

    def setup_experimental_conditions(self):
        self.postures = ['sit', 'stand', 'swivel']
        self.angles = ['low', 'medium', 'high']
        self.n_trials = 3
        self.trial_sequence = self.generate_trial_sequence()

    def setup_data_collection(self):
        self.eye_tracker = NeonEyeTracker()
        self.chest_imu = MotionTracker("CHEST_MAC_ADDRESS", "chest")
        self.mobile_imu = MotionTracker("MOBILE_MAC_ADDRESS", "mobile")
        self.synchronizer = DataSynchronizer()

    def generate_trial_sequence(self):
        sequence = []
        posture_order = list(permutations(self.postures))[
            self.participant_id % len(list(permutations(self.postures)))]

        for posture in posture_order:
            angle_order = list(permutations(self.angles))[
                self.participant_id % len(list(permutations(self.angles)))]
            for angle in angle_order:
                for trial in range(self.n_trials):
                    sequence.append({
                        'posture': posture,
                        'angle': angle,
                        'trial_num': trial + 1
                    })
        return sequence

    def run(self):
        for trial in self.trial_sequence:
            self.run_trial(trial)

    def run_trial(self, trial):
        print(f"\nPreparing trial: {trial}")
        input("Press Enter when ready...")

        self.eye_tracker.start_recording(
            f"P{self.participant_id}_{trial['posture']}_{trial['angle']}_{trial['trial_num']}")
        self.chest_imu.start_streaming()
        self.mobile_imu.start_streaming()

        input("Press Enter to end trial...")

        self.eye_tracker.stop_recording()
        self.chest_imu.stop_streaming()
        self.mobile_imu.stop_streaming()

    def cleanup(self):
        self.eye_tracker.cleanup()
        self.chest_imu.cleanup()
        self.mobile_imu.cleanup()