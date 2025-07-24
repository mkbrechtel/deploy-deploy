#!/usr/bin/env python3
# Test script to verify deploy.py logic
import subprocess
import json
from datetime import datetime

# Simulate some journal entries
test_entries = [
    {
        "__REALTIME_TIMESTAMP": str(int(datetime.now().timestamp() * 1000000)),
        "_PID": "1234",
        "_COMM": "systemd",
        "MESSAGE": "Starting Deploy test!..."
    },
    {
        "__REALTIME_TIMESTAMP": str(int(datetime.now().timestamp() * 1000000)),
        "_PID": "1235",
        "_COMM": "deploy.init",
        "MESSAGE": "Initializing deployment..."
    },
    {
        "__REALTIME_TIMESTAMP": str(int(datetime.now().timestamp() * 1000000)),
        "_PID": "1234",
        "_COMM": "systemd",
        "MESSAGE": "Started Deploy test!."
    },
    {
        "__REALTIME_TIMESTAMP": str(int(datetime.now().timestamp() * 1000000)),
        "_PID": "1236",
        "_COMM": "deploy",
        "MESSAGE": "Deployment started successfully"
    },
    {
        "__REALTIME_TIMESTAMP": str(int(datetime.now().timestamp() * 1000000)),
        "_PID": "1236",
        "_COMM": "deploy",
        "MESSAGE": "Processing tasks..."
    }
]

print("Test journal entries that would be processed:")
print("=" * 60)

# Simulate the processing logic from deploy.py
message_buffer = []
service_started = False
unit_name = "deploy@test.service"

for entry in test_entries:
    timestamp = datetime.fromtimestamp(int(entry.get('__REALTIME_TIMESTAMP', 0)) / 1000000)
    pid = entry.get('_PID', '-')
    comm = entry.get('_COMM', 'deploy')
    message = entry.get('MESSAGE', '')
    
    # Check for systemd service start message
    if not service_started and comm == 'systemd':
        if 'Started' in message and 'test' in message:
            service_started = True
            print(f"\n[SERVICE STARTED DETECTED]\n")
            # Output all buffered messages
            for buffered_msg in message_buffer:
                print(f"[BUFFERED] {buffered_msg}")
            message_buffer.clear()
    
    # Format the message for output
    if message and comm != 'systemd':
        formatted_msg = f"{timestamp.strftime('%b %d %H:%M:%S')} {comm}[{pid}]: {message}"
        
        if service_started:
            print(f"[LIVE] {formatted_msg}")
        else:
            print(f"[BUFFERING] {formatted_msg}")
            message_buffer.append(formatted_msg)

print("\n" + "=" * 60)
print(f"Final state: service_started={service_started}")
print(f"Remaining buffered messages: {len(message_buffer)}")