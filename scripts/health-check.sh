#!/bin/bash

# Raspberry Pi System Health Monitor

MODE="normal"
SCENARIO=""

if [ "$1" = "--test" ]; then
    MODE="test"
    SCENARIO="${2:-all}"

    if [ "$SCENARIO" = "all" ]; then
        for TEST in ok warning critical; do
            "$0" --test "$TEST"
        done
        exit 0
    fi
fi

if [ "$MODE" = "test" ]; then
    case "$SCENARIO" in
        ok)
            RAM_PERCENT=30
            DISK_PERCENT=20
            CPU_TEMP=50
            FAILED_SERVICES=0
            ;;
        warning)
            RAM_PERCENT=85
            DISK_PERCENT=20
            CPU_TEMP=50
            FAILED_SERVICES=0
            ;;
        critical)
            RAM_PERCENT=95
            DISK_PERCENT=20
            CPU_TEMP=50
            FAILED_SERVICES=0
            ;;
        all)
            ;;
        *)
            echo "Usage: $0 --test [ok|warning|critical|all]"
            exit 1
            ;;
    esac
fi

HOSTNAME=$(hostname)
DATE=$(date '+%Y-%m-%d %H:%M:%S')
CPU_LOAD=$(awk '{print $1}' /proc/loadavg)
UPTIME=$(uptime -p)

if [ "$MODE" = "normal" ]; then
    RAM_TOTAL=$(free -m | awk '/^Mem:/ {print $2}')
    RAM_USED=$(free -m | awk '/^Mem:/ {print $3}')
    RAM_PERCENT=$((RAM_USED * 100 / RAM_TOTAL))

    DISK_PERCENT=$(df -P / | awk 'NR==2 {gsub("%","",$5); print $5}')

    if [ -r /sys/class/thermal/thermal_zone0/temp ]; then
        TEMP_RAW=$(cat /sys/class/thermal/thermal_zone0/temp)
        CPU_TEMP=$(awk "BEGIN {printf \"%.1f\", $TEMP_RAW / 1000}")
    else
        CPU_TEMP="N/A"
    fi

    FAILED_SERVICES=$(systemctl --failed --no-legend --plain | wc -l)
fi

check_threshold() {
    local value=$1
    local warning=$2
    local critical=$3

    if [ "$value" -ge "$critical" ]; then
        echo "CRITICAL"
    elif [ "$value" -ge "$warning" ]; then
        echo "WARNING"
    else
        echo "OK"
    fi
}

RAM_STATUS=$(check_threshold "$RAM_PERCENT" 80 90)
DISK_STATUS=$(check_threshold "$DISK_PERCENT" 85 95)
SERVICE_STATUS=$(check_threshold "$FAILED_SERVICES" 1 3)

if [ "$CPU_TEMP" != "N/A" ]; then
    TEMP_STATUS=$(awk -v temp="$CPU_TEMP" '
        BEGIN {
            if (temp >= 85) print "CRITICAL"
            else if (temp >= 75) print "WARNING"
            else print "OK"
        }')
else
    TEMP_STATUS="UNKNOWN"
fi

STATUS="OK"

for result in "$RAM_STATUS" "$DISK_STATUS" "$SERVICE_STATUS" "$TEMP_STATUS"; do
    if [ "$result" = "CRITICAL" ]; then
        STATUS="CRITICAL"
        break
    elif [ "$result" = "WARNING" ]; then
        STATUS="WARNING"
    fi
done

echo "======================================"
echo " RASPBERRY PI HEALTH MONITOR"
echo "======================================"
echo "Mode:             $MODE"
echo "Hostname:         $HOSTNAME"
echo "Date:             $DATE"
echo "CPU Load:         $CPU_LOAD"
echo "RAM Usage:        ${RAM_PERCENT}% [$RAM_STATUS]"
echo "Disk Usage:       ${DISK_PERCENT}% [$DISK_STATUS]"
echo "CPU Temperature:  ${CPU_TEMP} C [$TEMP_STATUS]"
echo "Failed Services:  $FAILED_SERVICES [$SERVICE_STATUS]"
echo "Uptime:           $UPTIME"
echo "======================================"
echo "OVERALL STATUS:   $STATUS"
echo "======================================"

# Test mode does not generate reports
if [ "$MODE" = "test" ]; then
    exit 0
fi

REPORT_DIR="$HOME/raspberry-pi-health-monitor/reports"
REPORT_FILE="$REPORT_DIR/health-$(date '+%Y-%m-%d_%H%M%S').md"

mkdir -p "$REPORT_DIR"

{
    echo "# Raspberry Pi Health Report"
    echo ""
    echo "- Hostname: $HOSTNAME"
    echo "- Date: $DATE"
    echo "- CPU Load: $CPU_LOAD"
    echo "- RAM Usage: ${RAM_PERCENT}% [$RAM_STATUS]"
    echo "- Disk Usage: ${DISK_PERCENT}% [$DISK_STATUS]"
    echo "- CPU Temperature: ${CPU_TEMP} C [$TEMP_STATUS]"
    echo "- Failed Services: $FAILED_SERVICES [$SERVICE_STATUS]"
    echo "- Uptime: $UPTIME"
    echo "- Overall Status: $STATUS"
} > "$REPORT_FILE"

echo "Report saved: $REPORT_FILE"

find "$REPORT_DIR" -type f -name 'health-*.md' -mtime +30 -delete
