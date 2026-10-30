#!/bin/bash

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

run_test() {
    local description=$1
    local value=$2
    local warning=$3
    local critical=$4
    local expected=$5

    local result
    result=$(check_threshold "$value" "$warning" "$critical")

    if [ "$result" = "$expected" ]; then
        echo "[PASS] $description: $result"
    else
        echo "[FAIL] $description: expected $expected, got $result"
        return 1
    fi
}

echo "=== Threshold Tests ==="

run_test "Normal usage" 50 80 90 "OK"
run_test "Warning threshold" 80 80 90 "WARNING"
run_test "Critical threshold" 90 80 90 "CRITICAL"
run_test "Between thresholds" 85 80 90 "WARNING"
run_test "Below warning" 79 80 90 "OK"
