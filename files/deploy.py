#!/usr/bin/env python3
import sys
import subprocess
import json
import time
import random
import re
from datetime import datetime
from collections import deque

def main():
    if len(sys.argv) != 2:
        print("Usage: deploy.py <instance>", file=sys.stderr)
        sys.exit(1)
        
    instance = sys.argv[1]
    
    # Validate instance name
    if not re.match(r'^[a-z0-9.-]+$', instance):
        print(f"Error: Instance name '{instance}' contains invalid characters. Only [a-z0-9.-] are allowed.", file=sys.stderr)
        sys.exit(1)
    
    if len(instance) > 128:
        print(f"Error: Instance name '{instance}' is too long. Maximum 128 characters allowed.", file=sys.stderr)
        sys.exit(1)
    
    unit_name = f"deploy@{instance}.service"
    
    # Buffer for messages until service starts
    message_buffer = deque()
    service_started = False
    
    try:
        # Check if service is already running
        result = subprocess.run(['systemctl', 'is-active', unit_name], 
                              capture_output=True, text=True)
        if result.stdout.strip() == 'active':
            print(f"Waiting for {unit_name} to finish...")
            
            # Attach to the log to wait for service completion
            # Use --lines=1000 to catch recent messages including the completion
            wait_proc = subprocess.Popen(['journalctl', '-f', '-u', unit_name, '--output=json', '--lines=1000'],
                                       stdout=subprocess.PIPE, text=True)
            
            # Read journal until we see the service stop
            for line in wait_proc.stdout:
                try:
                    entry = json.loads(line)
                    comm = entry.get('_COMM', '')
                    unit_field = entry.get('UNIT', entry.get('_SYSTEMD_UNIT', ''))
                    code_func = entry.get('CODE_FUNC', '')
                    
                    # Check for systemd's exit message
                    if comm == 'systemd' and unit_field == unit_name and (
                        code_func == 'unit_log_success' or 
                        code_func == 'unit_log_failure'):
                        # Service has stopped
                        wait_proc.terminate()
                        break
                except json.JSONDecodeError:
                    continue
            
            # Wait about a second after service stops
            time.sleep(1.0)
        
        # Now start following the log for the new service
        # Use --lines=0 to start from now, --follow to keep following
        proc = subprocess.Popen(['journalctl', '-f', '-u', unit_name, '--output=json', '--lines=0'],
                               stdout=subprocess.PIPE, text=True)
        
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
                
                # Check for systemd service start message using CODE_FUNC
                if not service_started and comm == 'systemd':
                    code_func = entry.get('CODE_FUNC', '')
                    
                    # Look for job_emit_done_message with 'Started' in message
                    if code_func == 'job_emit_done_message' and 'Started' in message and unit_name in message:
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
                    # Service stopped, but keep reading for systemd's exit message
                    
                    # Check if this is systemd's message about our specific unit using CODE_FUNC
                    unit_field = entry.get('UNIT', entry.get('_SYSTEMD_UNIT', ''))
                    code_func = entry.get('CODE_FUNC', '')
                    
                    if comm == 'systemd' and unit_field == unit_name and (
                        code_func == 'unit_log_success' or 
                        code_func == 'unit_log_failure'):
                        # This is systemd's final message about the service
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