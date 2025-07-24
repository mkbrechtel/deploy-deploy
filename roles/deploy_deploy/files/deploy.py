#!/usr/bin/env python3
import sys
import subprocess
import json
import time
import random
from datetime import datetime

def main():
    if len(sys.argv) != 2:
        print("Usage: deploy.py <instance>", file=sys.stderr)
        sys.exit(1)
        
    instance = sys.argv[1]
    unit_name = f"deploy@{instance}.service"
    
    # Check if already running and wait
    result = subprocess.run(['systemctl', 'is-active', unit_name], 
                          capture_output=True, text=True)
    if result.stdout.strip() == 'active':
        print(f"Waiting for {unit_name} to finish...")
        subprocess.run(['systemctl', 'status', unit_name, '--wait'])
        # Random wait after service stops
        wait_time = random.uniform(0.5, 3.0)
        time.sleep(wait_time)
    
    # Start the unit
    result = subprocess.run(['systemctl', 'start', unit_name])
    if result.returncode != 0:
        sys.exit(1)
    
    # Wait a moment for systemd to register the start
    time.sleep(0.1)
    
    # Get the start time of our service
    result = subprocess.run(['systemctl', 'show', unit_name, '--property=ExecMainStartTimestamp'], 
                          capture_output=True, text=True)
    start_time = result.stdout.strip().split('=')[1]
    
    # Start logging from journal, only showing entries since service start
    proc = subprocess.Popen(['journalctl', '-f', '-u', unit_name, '--output=json', '--since', start_time],
                           stdout=subprocess.PIPE, text=True)
    
    try:
        for line in proc.stdout:
            entry = json.loads(line)
            timestamp = datetime.fromtimestamp(int(entry.get('__REALTIME_TIMESTAMP', 0)) / 1000000)
            pid = entry.get('_PID', '-')
            comm = entry.get('_COMM', 'deploy')
            message = entry.get('MESSAGE', '')
            
            # Skip systemd's own messages
            if comm == 'systemd':
                continue
                
            if message:
                print(f"{timestamp.strftime('%b %d %H:%M:%S')} {comm}[{pid}]: {message}")
            
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
    except KeyboardInterrupt:
        proc.terminate()
        sys.exit(130)

if __name__ == "__main__":
    main()