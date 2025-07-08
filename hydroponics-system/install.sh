#!/bin/bash
# Hydroponic System Installation Script

# Create directory structure
mkdir -p /home/pi/hydroponic/{config,sensors,controllers,static,templates,logs}

# Install required packages
sudo apt update
sudo apt install -y python3-pip python3-venv

# Create virtual environment
python3 -m venv /home/pi/hydroponic/venv
source /home/pi/hydroponic/venv/bin/activate

# Install Python dependencies
pip install -r /home/pi/hydroponic/requirements.txt

# Enable 1-Wire for temperature sensor
sudo sed -i 's/^#dtoverlay=w1-gpio/dtoverlay=w1-gpio/g' /boot/config.txt
sudo sed -i 's/^#dtoverlay=w1-gpio/dtoverlay=w1-gpio/g' /boot/config.txt || echo "dtoverlay=w1-gpio" | sudo tee -a /boot/config.txt

# Set up systemd service
sudo tee /etc/systemd/system/hydroponic.service > /dev/null <<EOT
[Unit]
Description=Hydroponic Control System
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/hydroponic
ExecStart=/home/pi/hydroponic/venv/bin/python /home/pi/hydroponic/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOT

sudo systemctl daemon-reload
sudo systemctl enable hydroponic.service

# Create web interface service
sudo tee /etc/systemd/system/hydroponic-web.service > /dev/null <<EOT
[Unit]
Description=Hydroponic Web Interface
After=network.target hydroponic.service

[Service]
User=pi
WorkingDirectory=/home/pi/hydroponic
ExecStart=/home/pi/hydroponic/venv/bin/python /home/pi/hydroponic/web_interface.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOT

sudo systemctl daemon-reload
sudo systemctl enable hydroponic-web.service

echo "Installation complete."
echo "Start main controller: sudo systemctl start hydroponic.service"
echo "Start web interface: sudo systemctl start hydroponic-web.service"