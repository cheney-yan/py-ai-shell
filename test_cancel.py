import subprocess
import signal
import time
import sys

# Execute a command that produces output over time
process = subprocess.Popen(
    "for i in {1..10}; do echo $i; sleep 1; done",
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1  # Line buffered
)

print("Command started, streaming output:")
print("-" * 40)

# Stream output for a few seconds
for i in range(3):
    # Read a line from stdout (non-blocking)
    line = process.stdout.readline()
    if line:
        sys.stdout.write(f"STDOUT: {line}")

    # Sleep a bit
    time.sleep(1)

# Simulate Ctrl+C by sending SIGINT
print("\nSimulating Ctrl+C by sending SIGINT...")
process.send_signal(signal.SIGINT)

# Wait for the process to terminate
process.wait()

# Check the exit code
print(f"Process terminated with exit code: {process.returncode}")

# In our implementation, we manually set the exit code to 130 when a KeyboardInterrupt is caught
print("Note: In the actual implementation, we manually set the exit code to 130 when a KeyboardInterrupt is caught.")
print("This is the standard exit code for SIGINT and indicates the process was cancelled by the user.")
