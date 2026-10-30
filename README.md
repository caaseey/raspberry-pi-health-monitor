
# Raspberry Pi System Health Monitor

A lightweight Linux system monitoring tool developed in Bash for Raspberry Pi.

## Overview

This project monitors the health of a Raspberry Pi running Ubuntu Server.

It collects system metrics, detects potential issues, generates Markdown reports and automates execution using systemd timers.

## Features

- CPU load monitoring
- RAM usage monitoring
- Disk usage monitoring
- CPU temperature monitoring
- System uptime monitoring
- Failed systemd services detection
- Configurable warning and critical thresholds
- Automatic Markdown report generation
- Automatic cleanup of reports older than 30 days
- Scheduled execution using systemd

## Technologies

- Ubuntu Server 24.04 LTS
- GNU Bash
- systemd
- Git

## Project Structure

```text
raspberry-pi-health-monitor/
├── scripts/
│   └── health-check.sh
├── reports/
│   └── .gitkeep
├── docs/
├── systemd-health-check.service
├── systemd-health-check.timer
├── .gitignore
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/raspberry-pi-health-monitor.git
cd raspberry-pi-health-monitor
```

Make the script executable:

```bash
chmod +x scripts/health-check.sh
```

Run the monitor:

```bash
./scripts/health-check.sh
```

## Automated Execution

The project uses systemd service and timer units to execute the monitoring script automatically every 30 minutes.

## Example Output

```text
RASPBERRY PI HEALTH MONITOR

CPU Load:         0.10
RAM Usage:        30% [OK]
Disk Usage:       5% [OK]
CPU Temperature:  51.5 C [OK]
Failed Services:  0 [OK]

OVERALL STATUS:   OK
```

## Hardware

Developed and tested on:

- Raspberry Pi 3 Model B Rev 1.2
- Ubuntu Server 24.04.5 LTS
- ARM64 architecture

## License

MIT License
