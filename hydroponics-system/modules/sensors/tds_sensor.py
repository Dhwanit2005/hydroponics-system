                    """
                    TDS (Total Dissolved Solids) Sensor Interface
                    Uses analog input via MCP3008 ADC
                    """

                    import spidev
                    import time
                    import logging

                    logger = logging.getLogger(__name__)

                    class TDSSensor:
                        def __init__(self, channel=0, spi_bus=0, spi_device=0):
                            self.channel = channel
                            self.spi = spidev.SpiDev()
                            self.spi.open(spi_bus, spi_device)
                            self.spi.max_speed_hz = 1350000

                            # Calibration values
                            self.calibration_factor = 0.5
                            self.reference_voltage = 3.3

                        def read_adc(self):
                            """Read raw value from MCP3008"""
                            adc = self.spi.xfer2([1, (8 + self.channel) << 4, 0])
                            data = ((adc[1] & 3) << 8) + adc[2]
                            return data

                        def read(self, temperature=25.0):
                            """Read TDS value with temperature compensation"""
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

                                # Convert to TDS (ppm)
                                # Temperature compensation formula
                                compensation_coefficient = 1.0 + 0.02 * (temperature - 25.0)
                                compensated_voltage = voltage / compensation_coefficient

                                # TDS calculation
                                tds = (133.42 * compensated_voltage**3 - 
                                       255.86 * compensated_voltage**2 + 
                                       857.39 * compensated_voltage) * self.calibration_factor

                                return max(0, tds)  # Ensure non-negative

                            except Exception as e:
                                logger.error(f"Error reading TDS sensor: {e}")
                                return 0

                        def cleanup(self):
                            """Clean up SPI connection"""
                            self.spi.close()