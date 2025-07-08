                            """
                            pH Sensor Interface
                            Uses analog input via MCP3008 ADC
                            """

                            import spidev
                            import time
                            import logging
                            from config.settings import Settings

                            logger = logging.getLogger(__name__)

                            class PHSensor:
                                def __init__(self, channel=1, spi_bus=0, spi_device=0):
                                    self.channel = channel
                                    self.spi = spidev.SpiDev()
                                    self.spi.open(spi_bus, spi_device)
                                    self.spi.max_speed_hz = 1350000

                                    # Load calibration from settings
                                    settings = Settings()
                                    self.calibration_offset = settings.ph_calibration_offset
                                    self.calibration_slope = settings.ph_calibration_slope
                                    self.reference_voltage = 3.3

                                def read_adc(self):
                                    """Read raw value from MCP3008"""
                                    adc = self.spi.xfer2([1, (8 + self.channel) << 4, 0])
                                    data = ((adc[1] & 3) << 8) + adc[2]
                                    return data

                                def read(self):
                                    """Read pH value"""
                                    try:
                                        # Take multiple readings for stability
                                        readings = []
                                        for _ in range(10):
                                            readings.append(self.read_adc())
                                            time.sleep(0.01)

                                        # Average the readings
                                        avg_reading = sum(readings) / len(readings)

                                        # Convert to voltage
                                        voltage = (avg_reading / 1023.0) * self.reference_voltage

                                        # Convert voltage to pH
                                        # Typical pH probe outputs ~2.5V at pH 7.0
                                        # Changes by ~0.18V per pH unit
                                        ph = 7.0 + ((2.5 - voltage) / 0.18)

                                        # Apply calibration
                                        ph = (ph * self.calibration_slope) + self.calibration_offset

                                        # Constrain to valid pH range
                                        return max(0, min(14, ph))

                                    except Exception as e:
                                        logger.error(f"Error reading pH sensor: {e}")
                                        return 7.0

                                def cleanup(self):
                                    """Clean up SPI connection"""
                                    self.spi.close()