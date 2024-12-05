# motion_tracker.py
# hardware/motion_tracker.py
from mbientlab.metawear import MetaWear, libmetawear
from mbientlab.metawear.cbindings import *
import queue
import time


class MotionTracker:
    def __init__(self, mac_address, location):
        self.device = MetaWear(mac_address)
        self.device.connect()
        self.location = location
        self.data_queue = queue.Queue()

        libmetawear.mbl_mw_settings_set_connection_parameters(
            self.device.board, 100, 100, 0, 6000)

        libmetawear.mbl_mw_sensor_fusion_enable_data(
            self.device.board,
            SensorFusionData.EULER_ANGLE)
        libmetawear.mbl_mw_sensor_fusion_enable_data(
            self.device.board,
            SensorFusionData.QUATERNION)

        self.callback = FnVoid_VoidP_DataP(self._handle_data)

    def _handle_data(self, ctx, data):
        euler_angles = cast(data.contents.value, POINTER(EulerAngles)).contents
        quaternion = cast(data.contents.value, POINTER(Quaternion)).contents

        motion_data = {
            'timestamp': time.time(),
            'location': self.location,
            'pitch': euler_angles.pitch,
            'roll': euler_angles.roll,
            'yaw': euler_angles.yaw,
            'quat_w': quaternion.w,
            'quat_x': quaternion.x,
            'quat_y': quaternion.y,
            'quat_z': quaternion.z
        }
        self.data_queue.put(motion_data)

    def start_streaming(self):
        libmetawear.mbl_mw_sensor_fusion_start(self.device.board)

    def stop_streaming(self):
        libmetawear.mbl_mw_sensor_fusion_stop(self.device.board)

    def cleanup(self):
        self.stop_streaming()
        self.device.disconnect()