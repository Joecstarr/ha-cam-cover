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

from requests import post,get
from pyzbar.pyzbar import decode
from PIL import Image
import io

import cv2

CONFIG_PATH = "/data/options.json"
API_URL = "http://supervisor/core/api/"
AUTH_TOKEN = os.environ['SUPERVISOR_TOKEN']
DEBOUNCE_PERIOD = timedelta(seconds=5)

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
log = logging.getLogger()

def send_tag_event(state, entity_id):
    endpoint = f"{API_URL}states/{entity_id}"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}", "content-type": "application/json"}
    data = {"state": state, "attributes": {"unit_of_measurement": "%"}}
    requests.post(endpoint, headers=headers, json=data)


def main():
    with open(CONFIG_PATH, "r") as fh:
        config = json.load(fh)
    while True:
        data = None
        percent = 100
        response = get(config["camera_rtsp_stream"])
        img = Image.open(io.BytesIO(response.content))
        data = decode(img)
        if data != None and config["tag_match"].match(data):
            percent = 0
            send_tag_event(percent, config["entity_id"])
        log.debug("loop")
        time.sleep(config["loop_time"])
    return 0


if __name__ == "__main__":
    main()
