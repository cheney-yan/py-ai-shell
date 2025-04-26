import subprocess
import sys
import threading

def stream_output(pipe, prefix):
    """Stream output from a pipe to stdout with a prefix."""
    for line in iter(pipe.readline, ''):
        sys.stdout.write(f"{prefix}: {line}")
        sys.stdout.flush()

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

# Create threads to stream stdout and stderr
stdout_thread = threading.Thread(target=stream_output, args=(process.stdout, "STDOUT"))
stderr_thread = threading.Thread(target=stream_output, args=(process.stderr, "STDERR"))

# Start the threads
stdout_thread.start()
stderr_thread.start()

# Wait for the process to complete
process.wait()

# Wait for the threads to complete
stdout_thread.join()
stderr_thread.join()

print("-" * 40)
print(f"Command completed with exit code: {process.returncode}")
