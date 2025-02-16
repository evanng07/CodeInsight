# main.py
import sys
import os
import json
import threading
import tkinter as tk
from tkinter import filedialog
import time
import webview

# Import your Flask app, analyzer function, and updater function from app.py
from app import app, analyze_directory, update_call_graph_data

def select_directory():
    """Open a file dialog to select a project directory."""
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window.
    return filedialog.askdirectory(title="Select Project Directory")

if __name__ == "__main__":
    # 1. Ask the user to select a project directory.
    selected_dir = select_directory()
    if not selected_dir:
        print("No directory selected. Exiting.")
        exit(1)
    
    # 2. Derive the project name from the selected directory.
    project_name = os.path.basename(os.path.normpath(selected_dir))
    
    # 3. Determine the base directory for storing JSON files.
    #    When packaged (frozen), use the executable's directory; otherwise, use the script's directory.
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 4. Create a "jsons" folder inside the base directory if it doesn't exist.
    jsons_dir = os.path.join(base_dir, "jsons")
    os.makedirs(jsons_dir, exist_ok=True)
    
    # 5. Define the JSON file path for this project.
    json_file_path = os.path.join(jsons_dir, f"{project_name}.json")
    
    # 6. Check if the JSON file already exists.
    if os.path.exists(json_file_path):
        print(f"JSON for project '{project_name}' found. Loading analysis from {json_file_path}.")
        with open(json_file_path, "r", encoding="utf-8") as f:
            project_data = json.load(f)
    else:
        print(f"Analyzing directory: {selected_dir}")
        project_data = analyze_directory(selected_dir)
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=2)
        print(f"Analysis complete. JSON file generated at: {json_file_path}")
    
    # 7. Update the Flask app's global data using the updater function.
    update_call_graph_data(project_data)
    
    # 8. Start the Flask app in a background thread.
    def run_flask():
        app.run(port=5000, debug=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Give the Flask server a moment to start up.
    time.sleep(1)
    
    # 9. Open the application in an embedded browser window using pywebview.
    webview.create_window("Call Graph Visualizer", "http://localhost:5000")
    webview.start()
