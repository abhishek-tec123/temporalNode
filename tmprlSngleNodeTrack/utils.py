import subprocess
import threading

def start_temporal_server():
    # Start Temporal server in dev mode as a subprocess
    proc = subprocess.Popen([
        "temporal", "server", "start-dev"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc

def print_temporal_logs(proc):
    def print_stream(stream, prefix):
        for line in iter(stream.readline, ''):
            print(f"[Temporal {prefix}] {line}", end='')
    threading.Thread(target=print_stream, args=(proc.stdout, "STDOUT"), daemon=True).start()
    threading.Thread(target=print_stream, args=(proc.stderr, "STDERR"), daemon=True).start() 