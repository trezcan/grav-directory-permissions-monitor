import os
import time
import subprocess
import logging


monitor_dir = "/var/www/DOMAIN-DIRECTORY/"
excluded_dirs = ['.git', '.svn']
scan_interval = 30  # Time between scans (in seconds)
print_scan_time = True  # Toggle for printing directory scan time (True/False)
script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'perms-script.sh')




timer_initiated = False
first_change_logged = False  # Initialize a flag for one-time logging

# Initialize logger settings
logging.basicConfig(filename='./logs/changes.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def initial_scan(directory):
    initial_state = {}
    for root, dirs, files in os.walk(directory):
        for name in files + dirs:
            full_path = os.path.join(root, name)
            stat_info = os.stat(full_path)
            initial_state[full_path] = (stat_info.st_uid, stat_info.st_mode)
    return initial_state

def monitor_directory(initial_state, directory, excluded_dirs=[]):
    global timer_initiated
    global first_change_logged

    while True:
        start_time = time.time()

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for name in files + dirs:
                full_path = os.path.join(root, name)
                if full_path.split('/')[-1] in excluded_dirs:
                    continue

                current_stat = os.stat(full_path)
                
                if full_path in initial_state:
                    if initial_state[full_path] != (current_stat.st_uid, current_stat.st_mode):
                        if not first_change_logged:
                            logging.info(f"Change detected in {full_path}. Ownership changed from {initial_state[full_path][0]} to {current_stat.st_uid}, permissions changed from {initial_state[full_path][1]} to {current_stat.st_mode}")
                            first_change_logged = True

                        if not timer_initiated:
                            initiate_timer(full_path)
                            initial_state = initial_scan(directory)
                else:
                    # New file or folder detected
                    logging.info(f"New file or folder detected: {full_path}")
                    initial_state[full_path] = (current_stat.st_uid, current_stat.st_mode)
                    # Trigger the script to reset permissions and ownership
                    initiate_timer(full_path)

        end_time = time.time()
        elapsed_time = end_time - start_time
        if print_scan_time:  
            print(f"Directory scan took {elapsed_time:.4f} seconds.")
        
        time.sleep(scan_interval)


def initiate_timer(changed_file):
    global timer_initiated
    global first_change_logged

    timer_initiated = True
    print(f"Change detected in {changed_file}. Waiting 5 seconds before initiating perms script.")
    time.sleep(5)
    execute_script()
    timer_initiated = False
    first_change_logged = False  # Reset the flag for one-time logging

def execute_script():
    print("Executing perms script")
    subprocess.run([script_path])
    print("Perms updated")

if __name__ == "__main__":
    initial_state = initial_scan(monitor_dir)
    monitor_directory(initial_state, monitor_dir)
