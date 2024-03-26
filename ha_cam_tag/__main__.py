import logging
import re
import signal
import sys
import threading
import time
import json
import os
import requests
from datetime import datetime, timedelta

import cv2

CONFIG_PATH = "/data/options.json"
API_URL = "http://supervisor/core/api/"
AUTH_TOKEN = os.environ['SUPERVISOR_TOKEN']
DEBOUNCE_PERIOD = timedelta(seconds=5)


def send_tag_event(state, entity_id):
    endpoint = f"{API_URL}states/{entity_id}"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}", "content-type": "application/json"}
    data = {"state": state, "attributes": {"unit_of_measurement": "%"}}
    requests.post(endpoint, headers=headers, json=data)


def main():
    with open(CONFIG_PATH, "r") as fh:
        config = json.load(fh)

    exiting = False
    frame = None
    cv = threading.Event()

    def detector_loop():
        detector = cv2.QRCodeDetector()
        while not exiting:
            cv.wait()
            percent = 100
            try:
                if (
                    not exiting
                    and (data := detector.detectAndDecode(frame)[0])
                    and (m := config["tag_match"].match(data))
                ):
                   percent = 0
                send_tag_event(percent, config["entity_id"])
            except Exception as e:
                logging.exception(e)

    detector_thread = threading.Thread(target=detector_loop)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    detector_thread.start()
    signal.signal(signal.SIGINT, signal.default_int_handler)

    try:
        while True:
            stream = cv2.VideoCapture(config["camera_rtsp_stream"])
            while stream.isOpened():
                if (frame := stream.read()[1]) is not None:
                    cv.set()
            stream.release()
            time.sleep(config["loop_time"])
    except KeyboardInterrupt:
        exiting = True
        cv.set()

    detector_thread.join()
    return 0


if __name__ == "__main__":
    main()
