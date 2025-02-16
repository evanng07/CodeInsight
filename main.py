import sys
import os
import json
import threading
import tkinter as tk
from tkinter import filedialog
import time
import webview

# Import your Flask app and analyzer function from app.py
from app import app, analyze_directory

def select_directory():
    """Open a file dialog to select a project directory."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    return filedialog.askdirectory(title="Select Project Directory")

if __name__ == "__main__":
    # 1. Ask the user to select a directory
    selected_dir = select_directory()
    if not selected_dir:
        print("No directory selected. Exiting.")
        exit(1)

    # 2. Analyze the selected directory
    print("Analyzing directory:", selected_dir)
    call_graph_data = analyze_directory(selected_dir)

    # 3. Determine the base directory for the JSON file.
    # If the app is frozen (packaged), use the executable's directory.
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    json_file_path = os.path.join(base_dir, "call_graph.json")

    # 4. Write the analysis result to the JSON file.
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(call_graph_data, f, indent=2)
    print("Analysis complete. JSON file generated at:", json_file_path)

    # 5. Start the Flask app in a separate thread.
    def run_flask():
        app.run(port=5000, debug=False)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Give the Flask server a moment to start up.
    time.sleep(1)

    # 6. Open the application in an embedded browser window using pywebview.
    webview.create_window("Call Graph Visualizer", "http://localhost:5000")
    webview.start()
