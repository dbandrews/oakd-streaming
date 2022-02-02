#!/usr/bin/env python3

import json
import contextlib
import socketserver
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from pathlib import Path
import sys
from socketserver import ThreadingMixIn
from time import sleep
import depthai as dai
import numpy as np
import cv2
from PIL import Image
import blobconverter

HTTP_SERVER_PORT = 8090

# HTTPServer MJPEG
class VideoStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
        self.end_headers()
        while True:
            sleep(0.1)
            if hasattr(self.server, 'frametosend'):
                image = Image.fromarray(cv2.cvtColor(self.server.frametosend, cv2.COLOR_BGR2RGB))
                stream_file = BytesIO()
                image.save(stream_file, 'JPEG')
                self.wfile.write("--jpgboundary".encode())

                self.send_header('Content-type', 'image/jpeg')
                self.send_header('Content-length', str(stream_file.getbuffer().nbytes))
                self.end_headers()
                image.save(self.wfile, 'JPEG')


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass


# start MJPEG HTTP Server
server_HTTP = ThreadedHTTPServer(('0.0.0.0', HTTP_SERVER_PORT), VideoStreamHandler)
th2 = threading.Thread(target=server_HTTP.serve_forever)
th2.daemon = True
th2.start()

labelMap = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
            "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

# This can be customized to pass multiple parameters
def getPipeline():
    # Start defining a pipeline
    pipeline = dai.Pipeline()

    # Define a source - color camera
    cam_rgb = pipeline.createColorCamera()
    # For the demo, just set a larger RGB preview size for OAK-D
    cam_rgb.setPreviewSize(300, 300)
    cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
    cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    cam_rgb.setInterleaved(False)

    detector = pipeline.createMobileNetDetectionNetwork()
    detector.setConfidenceThreshold(0.5)
    detector.setBlobPath(blobconverter.from_zoo(name="mobilenet-ssd", shaves=6))
    cam_rgb.preview.link(detector.input)

    # Create output
    xout_rgb = pipeline.createXLinkOut()
    xout_rgb.setStreamName("rgb")
    detector.passthrough.link(xout_rgb.input)

    xout_nn = pipeline.createXLinkOut()
    xout_nn.setStreamName("nn")
    detector.out.link(xout_nn.input)

    return pipeline


# https://docs.python.org/3/library/contextlib.html#contextlib.ExitStack
with contextlib.ExitStack() as stack:
    device_infos = dai.Device.getAllAvailableDevices()
    if len(device_infos) == 0:
        raise RuntimeError("No devices found!")
    else:
        print("Found", len(device_infos), "devices")
    devices = {}

    for device_info in device_infos:
        # Note: the pipeline isn't set here, as we don't know yet what device it is.
        # The extra arguments passed are required by the existing overload variants
        openvino_version = dai.OpenVINO.Version.VERSION_2021_4
        usb2_mode = False
        device = stack.enter_context(dai.Device(openvino_version, device_info, usb2_mode))

        # Note: currently on POE, DeviceInfo.getMxId() and Device.getMxId() are different!
        print("=== Connected to " + device_info.getMxId())
        mxid = device.getMxId()
        cameras = device.getConnectedCameras()
        usb_speed = device.getUsbSpeed()

        # Get a customized pipeline based on identified device type
        pipeline = getPipeline()
        device.startPipeline(pipeline)

        # Output queue will be used to get the rgb frames from the output defined above
        devices[mxid] = {
            'rgb': device.getOutputQueue(name="rgb"),
            'nn': device.getOutputQueue(name="nn"),
        }


    while True:
        for mxid, q in devices.items():
            frames =[]
            if q['nn'].has():
            # if True:
                dets = q['nn'].get().detections
                frame = q['rgb'].get().getCvFrame()

                for detection in dets:
                    ymin = int(300*detection.ymin)
                    xmin = int(300*detection.xmin)
                    cv2.putText(frame, mxid, (xmin + 30, ymin + 20), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255))
                    cv2.putText(frame, labelMap[detection.label], (xmin + 10, ymin + 20), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255))
                    cv2.putText(frame, f"{int(detection.confidence * 100)}%", (xmin + 10, ymin + 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255))
                    cv2.rectangle(frame, (xmin, ymin), (int(300*detection.xmax), int(300*detection.ymax)), (255,255,255), 2)
                # Show the frame
                # print(frame.shape)
                frames.append(frame)


            ## Need to somehow sync frames, and draw 2x wide. Maybe mask array and only draw to specific parts?
            if frames:
                if len(frames) == 2:
                    stacked = np.hstack((frames[0],frames[1]))
                else:
                    stacked = frames[0]

                cv2.imshow("Preview of multi device output",stacked)
                server_HTTP.frametosend = stacked

        if cv2.waitKey(1) == ord('q'):
            break