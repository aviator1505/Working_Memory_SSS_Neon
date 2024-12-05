from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import SensorFusionData, SensorFusionMode, FnVoid_VoidP_DataP
from mbientlab.warble import WarbleException
from threading import Event
import sys
from time import time

count = 0
e = Event()

# imu_mac_addresses = [
#     "EA:2B:2B:1A:83:0D",  # Replace with actual MAC address
#     "F2:B7:E2:CC:2E:40"  # Replace with actual MAC address
# ]
imu_id = 1
addr = 'EA:2B:2B:1A:83:0D'

if len(sys.argv) > 1:
    addr = "F2:B7:E2:CC:2E:40"
    imu_id = 2
print(addr)

start_time = None

def handle_notification(ctx, data):
    global count, imu_id, start_time
    # print(count)
    if not start_time:
        start_time = time()

    count += 1

    if count % 50 == 0:
        dt = time()-start_time
        print("%.1f FPS" % (count/dt))
        # start_time = None

    if count > 500:
        e.set()


data_source = SensorFusionData.QUATERNION

max_connect_attempts = 5

try:
    device = MetaWear(addr, hci_mac='hci0')
    device.connect()
    libmetawear.mbl_mw_settings_set_connection_parameters(device.board, 7.5, 7.5, 0, 6000)
except WarbleException as err:
    print('reattempting after warble exception: {}'.format(err))
    exit(1)

try:
    libmetawear.mbl_mw_sensor_fusion_set_mode(device.board, SensorFusionMode.NDOF)
    libmetawear.mbl_mw_sensor_fusion_write_config(device.board)
    processor = libmetawear.mbl_mw_sensor_fusion_get_data_signal(device.board, data_source)
    wrapped_handler = FnVoid_VoidP_DataP(handle_notification)
    libmetawear.mbl_mw_datasignal_subscribe(processor, None, wrapped_handler)
    libmetawear.mbl_mw_sensor_fusion_enable_data(device.board, data_source)
    libmetawear.mbl_mw_sensor_fusion_start(device.board)  # Line that causes segfault

    e.wait()

except RuntimeError as err:
    print(err)

finally:
    libmetawear.mbl_mw_sensor_fusion_stop(device.board)
    libmetawear.mbl_mw_sensor_fusion_clear_enabled_mask(device.board)
    libmetawear.mbl_mw_datasignal_unsubscribe(processor)
    libmetawear.mbl_mw_debug_disconnect(device.board)