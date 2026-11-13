#!/bin/bash
# MDCOLAB-CHAIN AWS run (12 Nov 2026): EC2 user-data failsafe. Every instance was launched with
# --instance-initiated-shutdown-behavior terminate, so this 5-hour shutdown TERMINATES the instance if teardown
# is missed (cost cap protection). Feeds no table.
shutdown -h +300 "MDCOLAB failsafe 5h"
