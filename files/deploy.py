#!/usr/bin/env python3
import sys
import subprocess
import systemd.journal
import time

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
        print(f"Unit {unit_name} is already running, waiting for completion...")
        # Wait for it to finish
        subprocess.run(['systemctl', 'status', unit_name, '--wait'])
    
    # Start the unit
    result = subprocess.run(['systemctl', 'start', unit_name], capture_output=True)
    if result.returncode != 0:
        print(f"Failed to start {unit_name}: {result.stderr.decode()}", file=sys.stderr)
        sys.exit(1)
    
    # Setup journal reader
    reader = systemd.journal.Reader()
    reader.this_boot()
    reader.add_match(_SYSTEMD_UNIT=unit_name)
    
    # Move to end and wait for new entries
    reader.seek_tail()
    reader.get_previous()  # Position at the end
    
    # Stream logs
    completed = False
    timeout_count = 0
    
    while not completed:
        # Wait for new entries
        if reader.wait(0.1) == systemd.journal.APPEND:
            for entry in reader:
                msg = entry.get('MESSAGE', '')
                if msg and not msg.startswith('No notifiers'):
                    print(msg)
                    if 'kthxbye' in msg:
                        completed = True
                        break
            timeout_count = 0
        else:
            timeout_count += 1
            if timeout_count > 150:  # 15 seconds timeout
                break
            
        # Check if unit is still active
        if not completed and timeout_count % 10 == 0:
            result = subprocess.run(['systemctl', 'is-active', unit_name], 
                                  capture_output=True, text=True)
            if result.stdout.strip() != 'active':
                completed = True

if __name__ == "__main__":
    main()