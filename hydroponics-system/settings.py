        """
        System configuration and settings
        """

        class Settings:
            # Sensor calibration values
            tds_calibration_factor = 0.5  # Adjust based on calibration
            ph_calibration_offset = 0.0   # Adjust based on calibration
            ph_calibration_slope = 1.0    # Adjust based on calibration

            # Target values for leafy greens
            target_tds_min = 800          # ppm
            target_tds_max = 1200         # ppm
            target_ph_min = 5.5           # pH
            target_ph_max = 6.5           # pH

            # Temperature limits
            min_temp = 18.0               # °C
            max_temp = 26.0               # °C

            # Water level
            min_water_level = 10.0        # cm from sensor

            # Dosing parameters
            nutrient_dose_ml = 10         # ml per dose
            ph_dose_ml = 5                # ml per dose

            # Timing
            update_interval = 60          # seconds between readings

            # Hardware pins (for reference)
            mcp3008_clk = 11
            mcp3008_dout = 9
            mcp3008_din = 10
            mcp3008_cs = 8
            temp_sensor_pin = 4
            ultrasonic_trig = 15
            ultrasonic_echo = 18