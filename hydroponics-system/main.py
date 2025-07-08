#!/usr/bin/env python3
"""
Hydroponic System Main Controller
Monitors sensors and controls pumps to maintain optimal growing conditions
"""

import time
import json
import logging
from datetime import datetime
import sys
import signal

from config.settings import Settings
from sensors.tds_sensor import TDSSensor
from sensors.ph_sensor import PHSensor
from sensors.temp_sensor import TempSensor
from sensors.level_sensor import LevelSensor
from controllers.pump_controller import PumpController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/pi/hydroponic/logs/hydroponic.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HydroponicController:
    def __init__(self):
        self.settings = Settings()
        self.running = False
        self.data = {
            'tds': 0,
            'ph': 0,
            'temperature': 0,
            'water_level': 0,
            'timestamp': '',
            'nutrient_pump_active': False,
            'ph_pump_active': False
        }

        # Initialize sensors
        logger.info("Initializing sensors...")
        self.tds_sensor = TDSSensor(channel=0)
        self.ph_sensor = PHSensor(channel=1)
        self.temp_sensor = TempSensor()
        self.level_sensor = LevelSensor(trig_pin=15, echo_pin=18)

        # Initialize pump controllers
        logger.info("Initializing pump controllers...")
        self.nutrient_pump = PumpController('/dev/ttyACM0', 'nutrient')
        self.ph_pump = PumpController('/dev/ttyACM1', 'ph')

        # Data file for web interface
        self.data_file = '/home/pi/hydroponic/logs/current_data.json'

    def read_sensors(self):
        """Read all sensor values"""
        try:
            # Read temperature first (needed for TDS compensation)
            self.data['temperature'] = self.temp_sensor.read()

            # Read other sensors
            self.data['tds'] = self.tds_sensor.read(self.data['temperature'])
            self.data['ph'] = self.ph_sensor.read()
            self.data['water_level'] = self.level_sensor.read()
            self.data['timestamp'] = datetime.now().isoformat()

            # Log readings
            logger.info(f"Sensor readings - TDS: {self.data['tds']:.0f} ppm, "
                       f"pH: {self.data['ph']:.2f}, "
                       f"Temp: {self.data['temperature']:.1f}°C, "
                       f"Level: {self.data['water_level']:.1f}cm")

            # Save data for web interface
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f)

        except Exception as e:
            logger.error(f"Error reading sensors: {e}")

    def control_nutrients(self):
        """Control nutrient dosing based on TDS levels"""
        tds = self.data['tds']

        if tds < self.settings.target_tds_min and not self.data['nutrient_pump_active']:
            logger.info(f"TDS low ({tds} ppm), starting nutrient pump")
            self.nutrient_pump.dose(self.settings.nutrient_dose_ml)
            self.data['nutrient_pump_active'] = True

        elif tds >= self.settings.target_tds_min and self.data['nutrient_pump_active']:
            logger.info(f"TDS recovered ({tds} ppm), stopping nutrient pump")
            self.data['nutrient_pump_active'] = False

    def control_ph(self):
        """Control pH adjustment based on pH levels"""
        ph = self.data['ph']

        if ph > self.settings.target_ph_max and not self.data['ph_pump_active']:
            logger.info(f"pH high ({ph}), dosing pH down")
            self.ph_pump.dose(self.settings.ph_dose_ml)
            self.data['ph_pump_active'] = True

        elif ph >= self.settings.target_ph_min and ph <= self.settings.target_ph_max:
            if self.data['ph_pump_active']:
                logger.info(f"pH normalized ({ph})")
                self.data['ph_pump_active'] = False

    def check_alerts(self):
        """Check for conditions requiring alerts"""
        # Low water level alert
        if self.data['water_level'] < self.settings.min_water_level:
            logger.warning(f"LOW WATER LEVEL: {self.data['water_level']}cm")

        # Temperature alerts
        if self.data['temperature'] > self.settings.max_temp:
            logger.warning(f"HIGH TEMPERATURE: {self.data['temperature']}°C")
        elif self.data['temperature'] < self.settings.min_temp:
            logger.warning(f"LOW TEMPERATURE: {self.data['temperature']}°C")

    def run(self):
        """Main control loop"""
        logger.info("Starting hydroponic control system")
        self.running = True

        while self.running:
            try:
                # Read sensors
                self.read_sensors()

                # Control systems
                self.control_nutrients()
                self.control_ph()

                # Check alerts
                self.check_alerts()

                # Wait before next cycle
                time.sleep(self.settings.update_interval)

            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.stop()
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(10)  # Wait before retrying

    def stop(self):
        """Gracefully stop the system"""
        logger.info("Stopping hydroponic controller")
        self.running = False

        # Ensure pumps are stopped
        self.nutrient_pump.stop()
        self.ph_pump.stop()

        # Cleanup
        self.tds_sensor.cleanup()
        self.ph_sensor.cleanup()
        self.temp_sensor.cleanup()
        self.level_sensor.cleanup()

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Received signal to terminate")
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and run controller
    controller = HydroponicController()

    try:
        controller.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        controller.stop()