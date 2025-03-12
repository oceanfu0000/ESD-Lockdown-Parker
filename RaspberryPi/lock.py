import RPi.GPIO as GPIO
import logging
import os
from flask import Blueprint, request

# Create a Blueprint for Lock Control routes
lock_blueprint = Blueprint("lock", __name__)

relay_pin = 18

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file_path = os.path.join(os.path.dirname(__file__), "logs/lock.log")
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.IN)

@lock_blueprint.route("/open", methods=["GET"])
def open_lock():
    GPIO.setup(relay_pin, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.output(relay_pin, False)
    logger.info("lock opening")
    return "Lock opened"

@lock_blueprint.route("/close", methods=["GET"])
def close_lock():
    GPIO.setup(relay_pin, GPIO.IN)
    GPIO.input(relay_pin)
    logger.info("lock closing")
    return "Lock closed"
