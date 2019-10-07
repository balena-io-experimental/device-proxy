#!/usr/bin/env bash

if [ -n "${START_PROXY}" ]; then
    echo "Starting proxy service as START_PROXY was set "
    glider_extra=()
    if [ -n "$VERBOSE" ]; then
        glider_extra+=('-verbose')
    fi
    glider -config glider.conf "${glider_extra[@]}"
else
    # No proxy requested, just idle, and send reminders every now and again.
    while : ; do
        echo "No START_PROXY variable is set, no proxy service is run"
        sleep 3600
    done
fi

if [ -n "${DEBUG}" ]; then
    while : ; do
        echo "Application exited, idling to debug."
        sleep 300
    done
fi
