
import time
from pupil_labs.realtime_api import Device
from mbientlab.warble import BleScanner
from mbientlab.metawear import MetaWear, libmetawear
from threading import Event
from mbientlab.metawear.cbindings import *
from ctypes import byref

# Number of IMUs to connect
num_devices = 2
imus = []
connected_devices = []
e = Event()

# LED blink pattern for IMUs
pattern = LedPattern(repeat_count=Const.LED_REPEAT_INDEFINITELY)
libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.BLINK)


def connect_imus(mac_addresses):
    connected_devices = []
    for address in mac_addresses:
        try:
            device = MetaWear(address)
            device.connect()
            connected_devices.append(device)
            print(f"Connected to IMU: {device.address}")

            # Set LED pattern to indicate connection
            libmetawear.mbl_mw_led_write_pattern(device.board, byref(pattern), LedColor.GREEN)
            libmetawear.mbl_mw_led_play(device.board)
        except Exception as ex:
            print(f"Failed to connect to {address}: {ex}")
    return connected_devices
def tracker_recording(ip_address):
    try:
        device = Device(ip_address, "8080")
        print("Starting tracker recording...")
        recording_id = device.recording_start()
        print(f"Started recording with ID: {recording_id}")
        time.sleep(5)  # Simulate recording duration
        device.recording_stop_and_save()
        print("Recording stopped and saved.")
    except Exception as ex:
        print(f"Error with tracker recording: {ex}")


def main():
    # Predefined MAC addresses for MetaWear IMUs
    imu_mac_addresses = [
        "EA:2B:2B:1A:83:0D",  # Replace with actual MAC address
        "F2:B7:E2:CC:2E:40"   # Replace with actual MAC address
    ]

    # Connect to IMUs
    connected_devices = connect_imus(imu_mac_addresses)

    if not connected_devices:
        print("No IMUs connected. Exiting.")
        return

    # Prompt for tracker IP address
    ip_address = input("Enter the Pupil Labs Neon Mobile Eye Tracker IP address: ")
    tracker_recording(ip_address)

    # Disconnect IMUs
    for device in connected_devices:
        libmetawear.mbl_mw_led_stop_and_clear(device.board)
        device.disconnect()
        print(f"Disconnected from IMU: {device.address}")


if __name__ == "__main__":
    main()
