# calibration.py
# utils/calibration.py
import numpy as np
import time
from collections import deque
from scipy.spatial.transform import Rotation


class IMUCalibrator:
    def __init__(self, trackers, calibration_duration=5.0, stillness_threshold=0.05):
        """
        Handles IMU calibration to align coordinate systems and establish reference frames.

        Args:
            trackers: Dictionary of tracker objects (eye_tracker, chest_imu, mobile_imu)
            calibration_duration: Duration in seconds to collect calibration data
            stillness_threshold: Maximum allowed angular velocity for "still" state
        """
        self.trackers = trackers
        self.calibration_duration = calibration_duration
        self.stillness_threshold = stillness_threshold
        self.reference_orientations = {}
        self.alignment_matrices = {}

    def collect_reference_pose(self):
        """
        Collects reference pose data while participant maintains neutral position:
        - Standing straight
        - Head level and forward
        - Arms at sides
        """
        print("\nBeginning reference pose collection")
        print("Please maintain neutral position:")
        print("- Stand straight")
        print("- Head level, facing forward")
        print("- Arms at sides")
        time.sleep(3)  # Give time to assume position

        # Initialize data collection
        ref_data = {name: [] for name in self.trackers.keys()}
        start_time = time.time()

        # Collect data for specified duration
        while time.time() - start_time < self.calibration_duration:
            for name, tracker in self.trackers.items():
                if not tracker.data_queue.empty():
                    data = tracker.data_queue.get()
                    ref_data[name].append({
                        'quat_w': data['quat_w'],
                        'quat_x': data['quat_x'],
                        'quat_y': data['quat_y'],
                        'quat_z': data['quat_z']
                    })

        # Calculate reference orientations
        for name, data_list in ref_data.items():
            if data_list:
                mean_quat = np.mean([[d['quat_w'], d['quat_x'], d['quat_y'], d['quat_z']]
                                     for d in data_list], axis=0)
                mean_quat /= np.linalg.norm(mean_quat)  # Normalize
                self.reference_orientations[name] = mean_quat

        return self.reference_orientations

    def compute_alignment_matrices(self):
        """
        Computes transformation matrices to align all IMUs to common reference frame.
        Uses head IMU (Neon) as reference coordinate system.
        """
        head_ref = self.reference_orientations['head']
        head_rot = Rotation.from_quat([head_ref[1], head_ref[2], head_ref[3], head_ref[0]])

        for name, ref_quat in self.reference_orientations.items():
            if name != 'head':
                sensor_rot = Rotation.from_quat([ref_quat[1], ref_quat[2], ref_quat[3], ref_quat[0]])
                # Compute alignment matrix to transform sensor frame to head frame
                self.alignment_matrices[name] = (head_rot.inv() * sensor_rot).as_matrix()

        return self.alignment_matrices

    def check_stillness(self, angular_velocities, window_size=10):
        """
        Verifies participant is sufficiently still during calibration.

        Args:
            angular_velocities: List of angular velocity measurements
            window_size: Number of samples to check

        Returns:
            bool: True if angular velocities are below threshold
        """
        if len(angular_velocities) < window_size:
            return False

        recent_velocities = angular_velocities[-window_size:]
        max_velocity = np.max(np.abs(recent_velocities))
        return max_velocity < self.stillness_threshold

    def apply_calibration(self, imu_data, sensor_name):
        """
        Applies calibration to align IMU data to reference frame.

        Args:
            imu_data: Dictionary containing quaternion data
            sensor_name: Name of the sensor ('chest' or 'mobile')

        Returns:
            numpy.ndarray: Aligned rotation matrix
        """
        if sensor_name not in self.alignment_matrices:
            raise ValueError(f"No calibration data for sensor: {sensor_name}")

        quat = [imu_data['quat_w'], imu_data['quat_x'],
                imu_data['quat_y'], imu_data['quat_z']]
        current_rot = Rotation.from_quat([quat[1], quat[2], quat[3], quat[0]])

        # Apply alignment transformation
        aligned_rot = current_rot.as_matrix() @ self.alignment_matrices[sensor_name]
        return aligned_rot