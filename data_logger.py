import csv
from datetime import datetime, timezone
from pathlib import Path

logfile = Path("/home/gourav/raspi-app/logs/uav_data.csv")

def init_logger():
    if not logfile.exists():
        with open(logfile, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'latitude', 'longitude', 'speed', 'alt', 'mq135', 'mq2', 'temperature', 'humidity'
            ])

def log_data(lat, lon, speed, alt, mq135, mq2, temp, hum):
    with open(logfile, 'a', newline='') as f:
        writer = csv.writer(f)
        timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
        writer.writerow([
            timestamp,lat, lon, speed, alt, mq135, mq2, temp, hum
        ])
