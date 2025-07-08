"""
Ultrasonic Water Level Sensor (HC-SR04)
Measures distance to water surface in cm
"""

import time
import logging
import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)

class LevelSensor:
    def __init__(self, trig_pin=15, echo_pin=18):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.speed_of_sound = 34300  # cm/s at 20°C

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        GPIO.output(self.trig_pin, False)
        time.sleep(0.5)  # Initial settling time

    def read(self):
        """Measure distance to water surface in cm"""
        try:
            # Send trigger pulse
            GPIO.output(self.trig_pin, True)
            time.sleep(0.00001)  # 10 µs pulse
            GPIO.output(self.trig_pin, False)

            # Wait for echo start
            pulse_start = time.time()
            timeout = pulse_start + 0.04  # Max 40ms wait (about 6.8m)
            while GPIO.input(self.echo_pin) == 0 and pulse_start < timeout:
                pulse_start = time.time()

            # Wait for echo end
            pulse_end = time.time()
            while GPIO.input(self.echo_pin) == 1 and pulse_end < timeout:
                pulse_end = time.time()

            # Calculate pulse duration
            pulse_duration = pulse_end - pulse_start

            # Calculate distance (cm)
            distance = pulse_duration * self.speed_of_sound / 2

            # Log and return
            logger.debug(f"Water level distance: {distance:.1f} cm")
            return distance

        except Exception as e:
            logger.error(f"Error reading water level: {e}")
            return 0.0

    def cleanup(self):
        """Clean up GPIO pins"""
        GPIO.cleanup([self.trig_pin, self.echo_pin])