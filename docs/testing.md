
# Testing and Validation

## 1. Overview

This document describes the tests performed to verify that the Raspberry Pi System Health Monitor works correctly.

## 2. Manual Execution Test

**Objective:** Verify that the monitoring script runs correctly.

Command:

```bash
./scripts/health-check.sh
```

Expected results:

- System metrics are collected.
- Health status is calculated.
- Results are displayed in the terminal.
- A Markdown report is generated.

**Result:** Passed.

## 3. Report Generation Test

**Objective:** Verify that monitoring reports are generated.

Command:

```bash
ls -lh reports/
```

Expected result:

A Markdown report with a timestamp in its filename is created inside the `reports/` directory.

**Result:** Passed.

## 4. Systemd Service Test

**Objective:** Verify that systemd can execute the monitoring script.

Command:

```bash
sudo systemctl start systemd-health-check.service
```

Expected result:

The service finishes successfully with `status=0/SUCCESS`.

**Result:** Passed.

## 5. Systemd Timer Test

**Objective:** Verify that automatic execution is configured.

Command:

```bash
systemctl status systemd-health-check.timer
```

Expected result:

The timer is active and waiting for its next execution.

**Result:** Passed.

## 6. Monitoring Thresholds

The following thresholds are configured:

| Metric | Warning | Critical |
|---|---:|---:|
| RAM Usage | 80% | 90% |
| Disk Usage | 85% | 95% |
| CPU Temperature | 75°C | 85°C |
| Failed Services | 1 | 3 |

Warning and critical scenarios have not yet been tested.

## 7. Current Test Environment

- Hardware: Raspberry Pi 3 Model B Rev 1.2
- Operating System: Ubuntu Server 24.04.5 LTS
- Architecture: ARM64

## 8. Conclusion

The basic monitoring workflow, report generation and systemd execution have been verified successfully.

Further testing is needed to validate WARNING and CRITICAL conditions.

## 9. Automated Threshold Tests

A test script was created to validate the `check_threshold()` function independently.

Test file: `tests/test-thresholds.sh`

The following scenarios were tested:

| Test | Input | Expected Result | Actual Result |
|---|---:|---|---|
| Normal usage | 50% | OK | PASS |
| Warning threshold | 80% | WARNING | PASS |
| Critical threshold | 90% | CRITICAL | PASS |
| Between thresholds | 85% | WARNING | PASS |
| Below warning | 79% | OK | PASS |

**Test execution:**

```bash
./tests/test-thresholds.sh
```

**Result:** 5 out of 5 tests passed.

These tests validate the threshold evaluation function. They do not simulate actual system resource conditions.
