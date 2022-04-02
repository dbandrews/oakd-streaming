# Open CV OAKD Streaming from Raspberry Pi

Credit: Heavily based on code from [depthai-experiments](https://github.com/luxonis/depthai-experiments/tree/master/gen2-mjpeg-streaming).

Streams video feed of detections + depth mask over HTTP, and the detected objects over a TCP socket. Can be used with [`oakd-streaming-dashboard`](https://github.com/dbandrews/oakd-streaming-dashboard) to allow using a small device (Raspberry Pi Zero etc) to do data capture and then visualize on a different device on the same local network.

## Install Steps:

Prerequisites:
- Clone the repo - follow instructions from root of the repo.

1. Setup virtualenv within cloned repo folder

	`$ python3 -m venv venv`

2. Activate virtual env:

	`$ source venv/bin/activate`

3. Install system dependencies (for Raspbian Bullseye, ARM7L) (Undocumented on DepthAI website?):

	`$ sudo apt-get python3-h5py libatlas-base-dev`

4. Install requirements:

	`$ pip install -r requirements.txt`

5. Potentially need to add udev rule to access OAKD device on USB:

	`$ echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules`

	`$ sudo udevadm control --reload-rules && sudo udevadm trigger`

6. Run HTTP Server and TCP Server within the activated `venv` with:

	`(venv)$ python3 main.py`
	
7. Access the HTTP server at `localhost:8090` in a browser (if the Pi has a static IP address, can access over local network from another machine)
	Access the TCP server with `nc localhost:8070` from another terminal to see streaming predictions.
