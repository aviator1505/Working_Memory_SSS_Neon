import numpy as np
from itertools import permutations
import time
import csv
from datetime import datetime
from pupil_labs.realtime_api.simple import Device
from mbientlab.metawear import MetaWear, libmetawear
import queue
import threading


class BlockCopyingExperiment:
    def __init__(self, participant_id, output_dir="data/"):
        """
        Initialize the block copying experiment with integrated eye tracking and motion sensing.

        This class manages a complex experimental setup that coordinates:
        - Experimental trial sequencing and counterbalancing
        - Eye tracking with Pupil Labs Neon
        - Motion tracking with multiple MbientLabs IMUs
        - Synchronized data collection across all sensors
        """
        # Core experimental parameters
        self.postures = ['sit', 'stand', 'swivel']
        self.angles = ['low', 'medium', 'high']
        self.n_trials = 3
        self.participant_id = participant_id
        self.output_dir = output_dir

        # Create unique filename with timestamp for data storage
        self.filename = f"{output_dir}P{participant_id:03d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # Effort weights for different postures (used in analysis)
        self.effort_weights = {
            'sit': 3,  # Highest effort due to trunk rotation requirements
            'swivel': 2,  # Medium effort with chair assistance
            'stand': 1  # Lowest effort with full body mobility
        }

        # Initialize data collection systems
        self.data_queues = {
            'eye': queue.Queue(),
            'head': queue.Queue(),
            'chest': queue.Queue(),
            'mobile': queue.Queue()  # For chair/feet IMU
        }

        # Setup experimental sequence
        self._setup_counterbalancing()

        # Initialize data storage
        self.trial_data = []
        self.recording = False

    def _setup_counterbalancing(self):
        """
        Implement Latin Square counterbalancing for experimental conditions.
        This ensures that order effects are controlled across participants.
        """
        # Generate all possible sequences
        self.posture_sequences = list(permutations(self.postures))
        self.angle_sequences = list(permutations(self.angles))

        # Select sequence based on participant ID to distribute conditions
        self.posture_order = self.posture_sequences[self.participant_id % len(self.posture_sequences)]

    def initialize_hardware(self):
        """
        Initialize and configure all sensor hardware.
        Returns False if any critical component fails to initialize.
        """
        try:
            # Initialize Pupil Labs Neon eye tracker
            self.eye_tracker = Device("YOUR_DEVICE_ADDRESS")
            print("Eye tracker initialized successfully")

            # Initialize chest IMU
            self.chest_imu = MetaWear("CHEST_IMU_ADDRESS")
            self._configure_imu(self.chest_imu)

            # Initialize mobile IMU (chair/feet)
            self.mobile_imu = MetaWear("MOBILE_IMU_ADDRESS")
            self._configure_imu(self.mobile_imu)

            print("All IMUs initialized successfully")
            return True

        except Exception as e:
            print(f"Hardware initialization failed: {e}")
            return False

    def _configure_imu(self, imu):
        """
        Configure an IMU with appropriate settings for our experiment.

        Parameters:
            imu: MetaWear device object to configure
        """
        # Set connection parameters for reliable data streaming
        libmetawear.mbl_mw_settings_set_connection_parameters(
            imu.board, 7.5, 7.5, 0, 6000
        )

        # Configure sensors for 100Hz sampling
        libmetawear.mbl_mw_acc_set_odr(imu.board, 100.0)
        libmetawear.mbl_mw_gyro_set_odr(imu.board, 100.0)
        libmetawear.mbl_mw_acc_set_range(imu.board, 16.0)  # ±16g range
        libmetawear.mbl_mw_gyro_set_range(imu.board, 2000.0)  # ±2000°/s range

    def start_recording(self, trial_info):
        """
        Begin synchronized data collection across all sensors.
        """
        self.recording = True
        self.start_time = datetime.now()

        # Start eye tracker recording with trial-specific name
        self.eye_tracker.start_recording(
            recording_name=f"P{self.participant_id}_"
                           f"{trial_info['posture']}_{trial_info['angle']}_"
                           f"trial{trial_info['trial_num']}"
        )

        # Start IMU recordings with appropriate handlers
        self._start_imu_streaming(self.chest_imu, self.data_queues['chest'], "chest")
        self._start_imu_streaming(
            self.mobile_imu,
            self.data_queues['mobile'],
            "chair" if trial_info['posture'] == 'swivel' else "feet"
        )

    def _start_imu_streaming(self, device, data_queue, location):
        """
        Begin streaming data from an IMU to its respective queue.
        """

        def data_handler(data):
            if not self.recording:
                return

            timestamp = (datetime.now() - self.start_time).total_seconds()
            data_queue.put({
                'timestamp': timestamp,
                'location': location,
                'acc_x': data.value.x,
                'acc_y': data.value.y,
                'acc_z': data.value.z,
                'gyro_x': data.value.x,
                'gyro_y': data.value.y,
                'gyro_z': data.value.z
            })

        libmetawear.mbl_mw_acc_start(device.board)
        libmetawear.mbl_mw_gyro_start(device.board)

    def stop_recording(self):
        """
        Stop all sensor recordings and save synchronized data.
        """
        self.recording = False
        self.eye_tracker.stop_recording()

        # Stop IMU recordings
        for imu in [self.chest_imu, self.mobile_imu]:
            libmetawear.mbl_mw_acc_stop(imu.board)
            libmetawear.mbl_mw_gyro_stop(imu.board)

        # Process and save all collected data
        self._save_synchronized_data()

    def run_trial(self, trial_info):
        """
        Execute a single experimental trial with synchronized data collection.
        """
        # Record trial start time
        trial_start = time.time()

        # Initialize trial data structure
        trial_data = {
            'participant_id': self.participant_id,
            'posture': trial_info['posture'],
            'angle': trial_info['angle'],
            'trial_num': trial_info['trial_num'],
            'effort_level': self.effort_weights[trial_info['posture']],
            'start_time': trial_start
        }

        # Start synchronized recording
        self.start_recording(trial_info)

        # Execute block copying task
        print(f"\nTrial Configuration:")
        print(f"Posture: {trial_info['posture']}")
        print(f"Angle: {trial_info['angle']}")
        print(f"Trial {trial_info['trial_num']} of {self.n_trials}")

        input("Press Enter when trial is complete...")

        # Stop recording and save data
        self.stop_recording()

        # Record trial end time
        trial_end = time.time()
        trial_data['end_time'] = trial_end
        trial_data['duration'] = trial_end - trial_start

        return trial_data

    def run_experiment(self):
        """
        Main experimental loop controlling the entire experimental session.
        """
        if not self.initialize_hardware():
            print("Hardware initialization failed. Please check connections.")
            return

        print("\nStarting Block Copying Experiment")
        print(f"Participant ID: {self.participant_id}")

        # Generate and run through trial sequence
        trial_sequence = self.generate_trial_sequence()

        for trial_num, trial in enumerate(trial_sequence, 1):
            # Ensure proper positioning
            input(f"\nPlease ensure participant is in {trial['posture']} position and press Enter...")

            # Execute trial
            trial_data = self.run_trial(trial)
            self.trial_data.append(trial_data)
            self.save_trial_data(trial_data)

            # Inter-trial break
            if trial_num < len(trial_sequence):
                print("\nTaking a short break (10 seconds)...")
                time.sleep(10)

        print("\nExperiment complete!")
        return self.trial_data
