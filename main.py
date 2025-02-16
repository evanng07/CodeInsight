# main.py
import sys
import os
import json
import threading
import tkinter as tk
from tkinter import filedialog
import time
import webview

# Import your Flask app, analyzer function, and updater from app.py
from app import app, analyze_directory, update_call_graph_data, analyze_file

def select_directory():
    """Open a file dialog to select a project directory."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window.
    return filedialog.askdirectory(title="Select Project Directory")

def analyze_directory(directory):
    """Analyze the directory and return only functions with code, ignoring node_modules and any env folders."""
    complete_graph = {}
    for root, dirs, files in os.walk(directory):
        # Ignore node_modules and any directories that contain 'env'
        if 'node_modules' in dirs:
            dirs.remove('node_modules')  # This prevents os.walk from going into node_modules
        
        # Remove any directory that contains 'env' in its name
        dirs[:] = [d for d in dirs if 'env' not in d.lower()]  # Ignore any directory with 'env' in its name

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                file_graph = analyze_file(filepath)
                # Only add functions with code to the complete graph
                for func_name, func_info in file_graph.items():
                    if func_info.get('code'):  # Check if there is code
                        complete_graph[func_name] = func_info
    return complete_graph

if __name__ == "__main__":
    # 1. Ask the user to select a project directory.
    selected_dir = select_directory()
    if not selected_dir:
        print("No directory selected. Exiting.")
        exit(1)
    
    # 2. Derive the project name from the selected directory.
    project_name = os.path.basename(os.path.normpath(selected_dir))
    
    # 3. Determine the base directory for storing JSON files.
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 4. Create a "jsons" folder inside the base directory if it doesn't exist.
    jsons_dir = os.path.join(base_dir, "jsons")
    os.makedirs(jsons_dir, exist_ok=True)
    
    # 5. Define the JSON file path for this project.
    json_file_path = os.path.join(jsons_dir, f"{project_name}.json")
    
    # 6. Check if the JSON file already exists; if not, perform analysis.
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
        app.run(host='0.0.0.0', port=5001, debug=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Wait briefly for the Flask server to start.
    time.sleep(1)
    
    # 9. Open the application in an embedded browser window using pywebview.
    webview.create_window("Call Graph Visualizer", "http://localhost:5001")
    webview.start()
