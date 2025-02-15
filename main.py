# main.py
import threading
import tkinter as tk
from tkinter import filedialog
import webview
import os
import time

# Import your Flask app and analyzer functions
from app import app, analyze_directory, call_graph_data

def select_directory():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    directory = filedialog.askdirectory(title="Select Project Directory")
    return directory

def run_flask():
    # Run the Flask app on port 5000
    app.run(port=5000, debug=False)

if __name__ == "__main__":
    # 1. Ask the user to select a directory
    selected_dir = select_directory()
    if not selected_dir:
        print("No directory selected. Exiting.")
        exit(1)

    # 2. Analyze the selected directory and update the global call graph
    print("Analyzing directory:", selected_dir)
    call_graph_data.update(analyze_directory(selected_dir))
    print("Analysis complete.")

    # 3. Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Wait a bit for the Flask server to start up
    time.sleep(1)

    # 4. Open the application in an embedded browser window using pywebview
    webview.create_window("Call Graph Visualizer", "http://localhost:5000")
    webview.start()
