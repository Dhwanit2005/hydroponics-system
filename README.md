# Hydroponic System Controller

An automated hydroponic monitoring and control system built for Raspberry Pi. This system monitors water parameters (TDS, pH, temperature, water level) and automatically adjusts nutrients and pH to maintain optimal growing conditions for leafy greens.

## Features

- **Real-time Monitoring**: Continuous monitoring of TDS, pH, temperature, and water level
- **Automated Control**: Automatic nutrient and pH adjustment based on configurable thresholds
- **Web Dashboard**: Real-time web interface for monitoring and manual control
- **Data Logging**: Comprehensive logging of all sensor readings and system actions
- **Sensor Calibration**: Built-in calibration utilities for accurate measurements
- **Safety Alerts**: Automated alerts for critical conditions (low water, temperature extremes)

## Hardware Requirements

### Raspberry Pi Setup
- Raspberry Pi 4 (recommended) or Pi 3B+
- MicroSD card (32GB+ recommended)
- Power supply (5V 3A)

### Sensors
- **TDS Sensor**: Analog TDS probe connected via MCP3008 ADC (Channel 0)
- **pH Sensor**: Analog pH probe connected via MCP3008 ADC (Channel 1)
- **Temperature Sensor**: DS18B20 1-Wire temperature sensor
- **Water Level Sensor**: HC-SR04 ultrasonic sensor (Trig: GPIO 15, Echo: GPIO 18)

### Controllers
- **MCP3008**: 8-channel 10-bit ADC for analog sensors
- **Raspberry Pi Pico**: Two units for pump control via UART
- **Peristaltic Pumps**: Two pumps for nutrient and pH solutions

### Wiring
```
MCP3008 Connections:
- VDD/VREF → 3.3V
- AGND/DGND → GND
- CLK → GPIO 11 (SCLK)
- DOUT → GPIO 9 (MISO)
- DIN → GPIO 10 (MOSI)
- CS → GPIO 8 (CE0)

DS18B20 Temperature Sensor:
- VDD → 3.3V
- GND → GND
- Data → GPIO 4
- 4.7kΩ pullup resistor between VDD and Data

HC-SR04 Ultrasonic Sensor:
- VCC → 5V
- GND → GND
- Trig → GPIO 15
- Echo → GPIO 18

Pump Controllers:
- Nutrient Pump Pico → /dev/ttyACM0 (USB)
- pH Pump Pico → /dev/ttyACM1 (USB)
```

## Software Installation

### 1. Prepare Raspberry Pi
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Enable SPI and 1-Wire
sudo raspi-config
# Navigate to Interface Options → SPI → Enable
# Navigate to Interface Options → 1-Wire → Enable
```

### 2. Clone and Install
```bash
# Download the project files to your Pi
# Place all files in /home/pi/hydroponic/

# Make install script executable
chmod +x install.sh

# Run installation script
sudo ./install.sh
```

### 3. Manual Installation (Alternative)
```bash
# Create directory structure
mkdir -p /home/pi/hydroponic/{config,sensors,controllers,static,templates,logs}

# Install Python dependencies
cd /home/pi/hydroponic
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Enable services
sudo systemctl enable hydroponic.service
sudo systemctl enable hydroponic-web.service
```

## Configuration

### System Settings
Edit `settings.py` to configure your system parameters:

```python
# Target values for leafy greens
target_tds_min = 800          # ppm
target_tds_max = 1200         # ppm
target_ph_min = 5.5           # pH
target_ph_max = 6.5           # pH

# Dosing parameters
nutrient_dose_ml = 10         # ml per dose
ph_dose_ml = 5                # ml per dose

# Update interval
update_interval = 60          # seconds between readings
```

### Sensor Calibration
Before first use, calibrate your sensors:

```bash
# Activate virtual environment
source /home/pi/hydroponic/venv/bin/activate

# Run calibration utility
python calibration.py

# Follow prompts for TDS and pH calibration
```

#### TDS Calibration
1. Prepare a known TDS solution (e.g., 1000ppm)
2. Place sensor in solution
3. Follow calibration prompts
4. System will calculate and apply new calibration factor

#### pH Calibration
1. Prepare pH 4.0 and pH 7.0 buffer solutions
2. Two-point calibration process
3. System calculates slope and offset values

## Usage

### Starting the System
```bash
# Start main controller
sudo systemctl start hydroponic.service

# Start web interface
sudo systemctl start hydroponic-web.service

# Check status
sudo systemctl status hydroponic.service
sudo systemctl status hydroponic-web.service
```

### Web Dashboard
Access the web interface at: `http://[PI_IP_ADDRESS]:5000`

Features:
- Real-time sensor readings
- System status indicators
- Manual pump controls
- System logs

### Manual Operation
```bash
# View logs
tail -f /home/pi/hydroponic/logs/hydroponic.log

# Manual calibration
python calibration.py

# Stop services
sudo systemctl stop hydroponic.service
sudo systemctl stop hydroponic-web.service
```

## System Operation

### Automatic Control Logic

**Nutrient Control (TDS)**:
- Monitors TDS levels continuously
- Doses nutrients when TDS falls below minimum threshold
- Stops dosing when TDS reaches target range

**pH Control**:
- Monitors pH levels continuously
- Doses pH down solution when pH exceeds maximum threshold
- Maintains pH within optimal range for nutrient uptake

**Safety Monitoring**:
- Low water level alerts
- Temperature extreme warnings
- Sensor failure detection

### Data Logging
All sensor readings and system actions are logged to:
- `/home/pi/hydroponic/logs/hydroponic.log` - Main system log
- `/home/pi/hydroponic/logs/current_data.json` - Current sensor data for web interface

## Troubleshooting

### Common Issues

**Sensors not reading correctly**:
- Check wiring connections
- Verify SPI is enabled: `lsmod | grep spi`
- Run calibration utility
- Check sensor probe condition

**Pumps not responding**:
- Verify USB connections to Pico controllers
- Check serial port assignments: `ls /dev/ttyACM*`
- Ensure Pico firmware is properly flashed

**Web interface not accessible**:
- Check service status: `sudo systemctl status hydroponic-web.service`
- Verify Flask is installed: `pip list | grep Flask`
- Check firewall settings

**1-Wire temperature sensor issues**:
- Verify 1-Wire is enabled: `sudo raspi-config`
- Check device detection: `ls /sys/bus/w1/devices/`
- Verify pullup resistor (4.7kΩ)

### Log Analysis
```bash
# View recent logs
sudo journalctl -u hydroponic.service -f

# Check system errors
grep ERROR /home/pi/hydroponic/logs/hydroponic.log

# Monitor sensor readings
grep "Sensor readings" /home/pi/hydroponic/logs/hydroponic.log | tail -20
```

## Growing Guidelines

### Optimal Ranges (Leafy Greens)
- **TDS**: 800-1200 ppm
- **pH**: 5.5-6.5
- **Temperature**: 18-26°C
- **Water Level**: Maintain above minimum threshold

### Maintenance Schedule
- **Daily**: Check web dashboard, verify pump operation
- **Weekly**: Clean sensors, check solution levels
- **Monthly**: Recalibrate sensors, system health check
- **Quarterly**: Deep clean system, replace solutions

## Safety Considerations

- Always disconnect power before handling electrical components
- Use food-grade materials for nutrient solutions
- Ensure proper ventilation in growing area
- Regular water quality testing
- Keep backup power supply for critical systems

## File Structure

```
hydroponic/
├── main.py                     # Main controller application
├── web_interface.py           # Flask web dashboard
├── calibration.py             # Sensor calibration utility
├── settings.py                # System configuration
├── install.sh                 # Installation script
├── requirements.txt           # Python dependencies
├── modules/
│   ├── sensors/               # Sensor interface modules
│   │   ├── tds_sensor.py
│   │   ├── ph_sensor.py
│   │   ├── temp_sensor.py
│   │   └── level_sensor.py
│   └── controllers/           # Hardware control modules
│       └── pump_controller.py
├── static/                    # Web interface assets
│   ├── styles.css
│   └── dashboard.js
├── templates/                 # HTML templates
│   └── index.html
└── logs/                      # System logs and data
    ├── hydroponic.log
    └── current_data.json
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with actual hardware
5. Submit a pull request

## License

This project is open source. Please ensure compliance with local regulations for hydroponic systems and food production.

## Support

For technical support:
1. Check the troubleshooting section
2. Review system logs
3. Verify hardware connections
4. Test individual components

---

**Note**: This system is designed for educational and hobbyist use. For commercial food production, additional safety certifications and monitoring may be required.
