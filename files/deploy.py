#!/usr/bin/env python3
import sys
import subprocess
import json
import time
import random
from datetime import datetime
from collections import deque

def main():
    if len(sys.argv) != 2:
        print("Usage: deploy.py <instance>", file=sys.stderr)
        sys.exit(1)
        
    instance = sys.argv[1]
    unit_name = f"deploy@{instance}.service"
    
    # First attach to the log - start journalctl immediately
    # Use --lines=0 to start from now, --follow to keep following
    proc = subprocess.Popen(['journalctl', '-f', '-u', unit_name, '--output=json', '--lines=0'],
                           stdout=subprocess.PIPE, text=True)
    
    # Buffer for messages until service starts
    message_buffer = deque()
    service_started = False
    
    try:
        # Check if service is already running
        result = subprocess.run(['systemctl', 'is-active', unit_name], 
                              capture_output=True, text=True)
        if result.stdout.strip() == 'active':
            print(f"Waiting for {unit_name} to finish...")
            # Wait for service to stop
            subprocess.run(['systemctl', 'status', unit_name, '--wait'])
            # Random wait after service stops
            wait_time = random.uniform(0.5, 3.0)
            time.sleep(wait_time)
        
        # Start the unit
        result = subprocess.run(['systemctl', 'start', unit_name])
        if result.returncode != 0:
            proc.terminate()
            sys.exit(1)
        
        # Now process log messages
        for line in proc.stdout:
            try:
                entry = json.loads(line)
                timestamp = datetime.fromtimestamp(int(entry.get('__REALTIME_TIMESTAMP', 0)) / 1000000)
                pid = entry.get('_PID', '-')
                comm = entry.get('_COMM', 'deploy')
                message = entry.get('MESSAGE', '')
                
                # Check for systemd service start message
                if not service_started and comm == 'systemd':
                    # Look for the special field indicating service has started
                    # Systemd sends a message when the main process starts
                    if 'Started' in message and unit_name in message:
                        service_started = True
                        # Output all buffered messages
                        for buffered_msg in message_buffer:
                            print(buffered_msg)
                        message_buffer.clear()
                
                # Format the message for output
                formatted_msg = f"{timestamp.strftime('%b %d %H:%M:%S')} {comm}[{pid}]: {message}"
                
                if service_started:
                    # Service has started, output immediately
                    print(formatted_msg)
                else:
                    # Buffer messages until service starts
                    message_buffer.append(formatted_msg)
                
                # Check if unit finished
                result = subprocess.run(['systemctl', 'is-active', unit_name], 
                                      capture_output=True, text=True)
                if result.stdout.strip() != 'active':
                    proc.terminate()
                    # Get exit code
                    result = subprocess.run(['systemctl', 'show', unit_name, '--property=ExecMainStatus'], 
                                          capture_output=True, text=True)
                    return_code = int(result.stdout.split('=')[1].strip())
                    print(f"\nProcess finished with exit code: {return_code}")
                    sys.exit(return_code)
                    
            except json.JSONDecodeError:
                # Log malformed JSON to stderr
                print(f"Warning: Malformed JSON in journalctl output: {line.strip()}", file=sys.stderr)
                continue
                
    except KeyboardInterrupt:
        proc.terminate()
        sys.exit(130)

if __name__ == "__main__":
    main()