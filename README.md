# Open CV OAKD Streaming from Raspberry Pi


## Install Steps:

1. Setup virtualenv within desired project folder
2. Activate virtual env:
	`$ source venv/bin/activate`
3. Clone the `depthai` repo:
	`$ git clone https://github.com/luxonis/depthai.git`
4. Install system dependencies (for Raspbian Bullseye, ARM7L) (Undocumented on DepthAI website?):
	`$ sudo apt-get python3-h5py libatlas-base-dev`
5. Install `depthai`:
	`$ cd depthai && python3 install_requirements.py`
6. Potentially need to add udev rule to access device:
	`$ echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules`
	`$ sudo udevadm control --reload-rules && sudo udevadm trigger`
7. Run demo to confirm:
	`$ python3 depthai_demo.py`
