# eye_tracker.py
# hardware/eye_tracker.py
from pupil_labs.realtime_api import Device
import queue
import numpy as np
import time


class NeonEyeTracker:
    def __init__(self, address="127.0.0.1", port=8080):
        self.device = Device(address=address, port=port)
        self.gaze_queue = queue.Queue()
        self.imu_queue = queue.Queue()

        if not self.device.connected:
            raise ConnectionError("Failed to connect to Neon eye tracker")

        self.device.streaming.subscribe('gaze', self._handle_gaze)
        self.device.streaming.subscribe('imu', self._handle_imu)

    def _handle_gaze(self, timestamp, gaze):
        gaze_data = {
            'timestamp': timestamp,
            'gaze_x': gaze[0],
            'gaze_y': gaze[1],
            'gaze_3d_x': gaze[2],
            'gaze_3d_y': gaze[3],
            'gaze_3d_z': gaze[4]
        }
        self.gaze_queue.put(gaze_data)

    def _handle_imu(self, timestamp, imu_data):
        head_motion = {
            'timestamp': timestamp,
            'rotation_x': imu_data.rotation_x,
            'rotation_y': imu_data.rotation_y,
            'rotation_z': imu_data.rotation_z,
            'quaternion_w': imu_data.quaternion_w,
            'quaternion_x': imu_data.quaternion_x,
            'quaternion_y': imu_data.quaternion_y,
            'quaternion_z': imu_data.quaternion_z
        }
        self.imu_queue.put(head_motion)

    def start_recording(self, recording_name):
        self.device.recording.start(recording_name)

    def stop_recording(self):
        self.device.recording.stop()

    def cleanup(self):
        self.device.streaming.unsubscribe('gaze')
        self.device.streaming.unsubscribe('imu')