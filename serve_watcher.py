import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


# This class handles file change events and restarts the app
class RestartOnChangeHandler(PatternMatchingEventHandler):
    def __init__(self, command):
        # Watch only Python files (*.py)
        super().__init__(patterns=["*.py"], ignore_directories=True)
        self.command = command  # Command to run (e.g., "make serve")
        self.process = None
        self.restart()  # Start the app initially

    def restart(self):
        # If the app is already running, stop it
        if self.process:
            print("Terminating existing process...")
            self.process.terminate()  # Stop the process
            self.process.wait()  # Wait for it to fully exit
        # Start the app again by running the command
        print(f"Running command: {self.command}")
        self.process = subprocess.Popen(self.command, shell=True)

    # This method is called when a watched file changes
    def on_modified(self, event):
        print(f"Detected change in {event.src_path}. Restarting...")
        self.restart()  # Restart the app on file change


if __name__ == "__main__":
    cmd = "make serve"  # The command to run your app

    # Create the event handler for file changes
    event_handler = RestartOnChangeHandler(cmd)

    # Create an Observer to watch the file system
    observer = Observer()

    # Watch the 'src' folder and its subfolders recursively
    observer.schedule(event_handler, path="src", recursive=True)

    # Start watching in the background
    observer.start()
    print("Watching for changes in 'src/' folder...")

    try:
        # Keep the script running indefinitely
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # On Ctrl+C, stop watching and terminate the app
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()
