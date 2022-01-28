# Open CV OAKD Streaming from Raspberry Pi


## Install Steps:

1. Setup virtualenv within desired project folder
	`$python3 virtualenv venv`
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
	`(venv)$python3 main.py`
	
7. Access the HTTP server at `localhost:8090` in a browser (if the Pi has a static IP address, can access over local network from another machine)
	Access the TCP server with `nc localhost:8070` from another terminal to see streaming predictions.

