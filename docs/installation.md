
# Installation Guide

## 1. Requirements

Before installing the project, make sure you have:

- A Raspberry Pi or compatible Linux system.
- Ubuntu Server 24.04 LTS or another compatible Linux distribution.
- An active internet connection.
- Git installed.
- Bash and systemd.

## 2. Clone the Repository

Clone the project from GitHub:

```bash
git clone https://github.com/caaseey/raspberry-pi-health-monitor.git
```

Navigate to the project directory:

```bash
cd raspberry-pi-health-monitor
```

## 3. Set Script Permissions

Give execution permissions to the monitoring script:

```bash
chmod +x scripts/health-check.sh
```

## 4. Run the Script Manually

Execute the script:

```bash
./scripts/health-check.sh
```

The script will display the system health information and generate a Markdown report inside the `reports/` directory.

## 5. Configure Systemd Automation

Copy the service and timer files into the systemd directory:

```bash
sudo cp systemd-health-check.service /etc/systemd/system/
sudo cp systemd-health-check.timer /etc/systemd/system/
```

Reload the systemd configuration:

```bash
sudo systemctl daemon-reload
```

Enable and start the timer:

```bash
sudo systemctl enable --now systemd-health-check.timer
```

## 6. Verify the Timer

Check whether the timer is active:

```bash
systemctl status systemd-health-check.timer
```

Display the scheduled executions:

```bash
systemctl list-timers
```

## 7. Execute a Manual Test

Run the monitoring service manually:

```bash
sudo systemctl start systemd-health-check.service
```

Check its execution result:

```bash
systemctl status systemd-health-check.service
```

A successful execution should show `status=0/SUCCESS`.

## 8. View Generated Reports

List the generated reports:

```bash
ls -lh reports/
```

Read the latest report:

```bash
cat reports/health-*.md
```
