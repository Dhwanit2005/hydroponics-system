"""
Controls peristaltic pumps via Raspberry Pi Pico
Uses UART communication to send pump commands
"""

import serial
import time
import logging

logger = logging.getLogger(__name__)

class PumpController:
    def __init__(self, port, pump_type, baudrate=9600, timeout=1):
        self.port = port
        self.pump_type = pump_type  # 'nutrient' or 'ph'
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            time.sleep(2)  # Wait for serial connection to establish
            logger.info(f"Connected to {pump_type} pump controller at {port}")
        except Exception as e:
            logger.error(f"Failed to connect to pump controller at {port}: {e}")

    def dose(self, ml_amount):
        """Dose a specific amount in milliliters"""
        if self.ser is None:
            logger.error(f"Pump controller not connected for {self.pump_type} pump")
            return False

        try:
            # Format: "DOSE <type> <amount>\n"
            command = f"DOSE {self.pump_type} {ml_amount}\n".encode()
            self.ser.write(command)

            # Wait for acknowledgment
            response = self.ser.readline().decode().strip()
            if response == "ACK":
                logger.info(f"Dosed {ml_amount}ml of {self.pump_type}")
                return True
            else:
                logger.warning(f"Unexpected response from pump: {response}")
                return False
        except Exception as e:
            logger.error(f"Error sending dose command: {e}")
            return False

    def stop(self):
        """Emergency stop the pump"""
        if self.ser is None:
            return

        try:
            self.ser.write(b"STOP\n")
        except Exception as e:
            logger.error(f"Error sending stop command: {e}")

    def close(self):
        """Close serial connection"""
        if self.ser is not None:
            self.ser.close()