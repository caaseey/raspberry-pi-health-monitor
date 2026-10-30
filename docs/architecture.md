
# System Architecture

## 1. Overview

The Raspberry Pi System Health Monitor is a lightweight monitoring tool developed with Bash.

It runs on Ubuntu Server and periodically checks the Raspberry Pi's system resources. It collects information, evaluates resource usage and generates Markdown reports.

## 2. Project Components

The project consists of the following components:

- **health-check.sh:** Main script responsible for collecting system information, checking thresholds and generating reports.
- **systemd-health-check.service:** Systemd service that executes the monitoring script.
- **systemd-health-check.timer:** Systemd timer that schedules automatic executions.
- **reports/:** Directory where generated health reports are stored.

## 3. Monitoring Metrics

The script collects the following metrics:

| Metric | Source |
|---|---|
| CPU Load | `/proc/loadavg` |
| RAM Usage | `free` |
| Disk Usage | `df` |
| CPU Temperature | `/sys/class/thermal/thermal_zone0/temp` |
| System Uptime | `uptime` |
| Failed Services | `systemctl` |

## 4. Alert Thresholds

The script evaluates the following thresholds:

| Metric | Warning | Critical |
|---|---:|---:|
| RAM Usage | 80% | 90% |
| Disk Usage | 85% | 95% |
| CPU Temperature | 75°C | 85°C |
| Failed Services | 1 | 3 |

CPU load is collected and displayed but does not currently affect the overall health status.

## 5. Execution Workflow

1. The systemd timer triggers the monitoring service.
2. The service executes `health-check.sh` as the `ubuntu` user.
3. The script collects system information.
4. Each monitored metric is evaluated against its thresholds.
5. An overall status is calculated: OK, WARNING or CRITICAL.
6. The results are displayed in the terminal and saved as a Markdown report.
7. Reports older than 30 days are automatically deleted.

## 6. Automation

The systemd timer is configured with:

- `OnBootSec=2min`: First execution two minutes after boot.
- `OnUnitActiveSec=30min`: Subsequent executions every 30 minutes after the previous activation.

## 7. Report Storage

Reports are stored locally in the `reports/` directory.

Generated reports are excluded from Git using `.gitignore` to avoid publishing device-specific monitoring information.

## 8. Deployment Environment

- **Hardware:** Raspberry Pi 3 Model B Rev 1.2
- **Operating System:** Ubuntu Server 24.04.5 LTS
- **Architecture:** ARM64 (aarch64)
- **Language:** Bash
- **Automation:** systemd
