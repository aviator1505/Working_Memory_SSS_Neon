from mbientlab.metawear import MetaWear

mac_address = "EA:2B:2B:1A:83:0D"  # Replace with your IMU MAC address

try:
    device = MetaWear(mac_address)
    device.connect()
    print(f"Connected to IMU: {device.address}")
    device.disconnect()
    print("Disconnected from IMU.")
except Exception as ex:
    print(f"Failed to connect to IMU: {ex}")