"""
Sensor Calibration Utility
"""

import time
import json
import logging
from config.settings import Settings
from sensors.tds_sensor import TDSSensor
from sensors.ph_sensor import PHSensor

logger = logging.getLogger(__name__)

def calibrate_tds():
    """Calibrate TDS sensor with known solution"""
    print("=== TDS Sensor Calibration ===")
    print("1. Prepare a known TDS solution (e.g., 1000ppm)")
    print("2. Place sensor in solution and wait for stabilization")
    input("Press Enter when ready...")

    tds_sensor = TDSSensor()
    settings = Settings()

    # Take multiple readings
    readings = []
    for i in range(10):
        reading = tds_sensor.read()
        readings.append(reading)
        print(f"Reading {i+1}: {reading:.0f} ppm")
        time.sleep(1)

    avg_reading = sum(readings) / len(readings)
    known_value = float(input("Enter known TDS value (ppm): "))

    # Calculate new calibration factor
    new_factor = settings.tds_calibration_factor * (known_value / avg_reading)
    print(f"New calibration factor: {new_factor:.4f}")

    # Save to settings?
    if input("Apply this factor? (y/n): ").lower() == 'y':
        settings.tds_calibration_factor = new_factor
        # Note: In a real system, we'd save to a persistent config file
        print("Calibration factor updated (restart system to apply)")
    else:
        print("Calibration aborted")

def calibrate_ph():
    """Calibrate pH sensor using two-point calibration"""
    print("=== pH Sensor Calibration ===")
    print("We will perform two-point calibration using pH 4.0 and 7.0 solutions")

    ph_sensor = PHSensor()
    settings = Settings()

    # Calibrate low point (pH 4.0)
    print("\nStep 1: pH 4.0 Calibration")
    input("Place sensor in pH 4.0 solution and press Enter...")
    low_readings = []
    for i in range(10):
        reading = ph_sensor.read()
        low_readings.append(reading)
        print(f"Reading {i+1}: {reading:.2f} pH")
        time.sleep(1)
    low_avg = sum(low_readings) / len(low_readings)

    # Calibrate high point (pH 7.0)
    print("\nStep 2: pH 7.0 Calibration")
    input("Rinse sensor and place in pH 7.0 solution. Press Enter...")
    high_readings = []
    for i in range(10):
        reading = ph_sensor.read()
        high_readings.append(reading)
        print(f"Reading {i+1}: {reading:.2f} pH")
        time.sleep(1)
    high_avg = sum(high_readings) / len(high_readings)

    # Calculate slope and offset
    # Formula: pH = (raw * slope) + offset
    slope = (7.0 - 4.0) / (high_avg - low_avg)
    offset = 4.0 - (slope * low_avg)

    print(f"\nCalculated slope: {slope:.4f}")
    print(f"Calculated offset: {offset:.4f}")

    if input("Apply these values? (y/n): ").lower() == 'y':
        settings.ph_calibration_slope = slope
        settings.ph_calibration_offset = offset
        # Note: In a real system, we'd save to a persistent config file
        print("Calibration values updated (restart system to apply)")
    else:
        print("Calibration aborted")

if __name__ == "__main__":
    print("Hydroponic Sensor Calibration\n")
    print("1. Calibrate TDS Sensor")
    print("2. Calibrate pH Sensor")
    choice = input("Select option: ")

    if choice == '1':
        calibrate_tds()
    elif choice == '2':
        calibrate_ph()
    else:
        print("Invalid choice")