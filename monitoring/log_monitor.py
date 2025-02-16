import re
import time

# Path to your existing log file
log_file_path = "C:\\Users\\ryanl\\affirmAI\\logs\\flask_log.txt"

# Define patterns to look for
error_pattern = re.compile(r"\bERROR\b", re.IGNORECASE)
warning_pattern = re.compile(r"\bWARNING\b", re.IGNORECASE)

def monitor_logs():
    print("Starting log monitoring...")
    with open(log_file_path, "r") as log_file:
        # Start reading from the end of the file
        log_file.seek(0, 2)
        while True:
            line = log_file.readline()
            if not line:
                time.sleep(1)  # Wait for new lines
                continue

            if error_pattern.search(line):
                print("Error detected:", line.strip())
                # Add notification logic here

            if warning_pattern.search(line):
                print("Warning detected:", line.strip())
                # Add notification logic here

if __name__ == "__main__":
    monitor_logs()
