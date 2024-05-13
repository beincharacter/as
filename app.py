from flask import Flask, request
from flask_cors import CORS
import threading
import time
import socket
import pychromecast

app = Flask(__name__)
CORS(app)

devices = []

def start_casting(device):
    try:
        chromecast_ip = device['device_ip']
        url_to_cast = device['url']

        print(f"Casting to device: {device['device_name']}")

        # Check if the device is reachable
        alive = ping_device(chromecast_ip)
        if not alive:
            print("Device not found on network")
            return "Device not found on network"

        # Establish connection to the Chromecast
        chromecast = pychromecast.Chromecast(chromecast_ip)
        chromecast.wait()

        # Cast the URL
        chromecast.media_controller.play_media(url_to_cast, 'video/mp4')
        time.sleep(5)  # Wait for a few seconds to ensure casting starts

        print(f"Casting success to device: {device['device_name']}")
        return "Casting success"
    except Exception as e:
        print(f"Error in casting: {e}")
        return f"Error in casting: {e}"

def stop_casting(device):
    try:
        chromecast_ip = device['device_ip']

        print(f"Stopping casting to device: {device['device_name']}")

        # Check if the device is reachable
        alive = ping_device(chromecast_ip)
        if not alive:
            print("Device not found on network")
            return "Device not found on network"

        # Close the connection
        chromecast = pychromecast.Chromecast(chromecast_ip)
        chromecast.quit_app()

        print(f"Stopped casting to device: {device['device_name']}")
        return "Stopped casting"
    except Exception as e:
        print(f"Error in stopping casting: {e}")
        return f"Error in stopping casting: {e}"

def ping_device(ip):
    try:
        return socket.create_connection((ip, 80), timeout=1)
    except OSError:
        return None

@app.route('/receive-data', methods=['POST'])
def receive_data():
    try:
        data = request.json
        global devices
        devices = data
        print("Received data:")
        print(devices)

        # Start casting or stop casting based on received data
        for device in devices:
            if device.get('isStop'):
                stop_casting(device)
            else:
                threading.Thread(target=start_casting, args=(device,)).start()

        return "SUCCESS"
    except Exception as e:
        print(f"Error: {e}")
        return "ERROR"

if __name__ == '__main__':
    app.run(port=4000, debug=True)
