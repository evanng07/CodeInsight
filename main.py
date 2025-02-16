# main.py
import sys
import os
import json
import threading
import tkinter as tk
from tkinter import filedialog
import time
import webview
import builtins
from dotenv import load_dotenv  # Load environment variables
from groq import Groq
from flask import Flask
from app import app, update_call_graph_data,analyze_file  # Import the Flask app from app.py

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Access the GROQ_API_KEY
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

# Initialize the Groq client with the API key
client = Groq(api_key=api_key)

# Pass the client to the app
app.config['GROQ_CLIENT'] = client  # Store the client in the app's config

def analyze_directory(directory):
    """
    Analyze all Python files in the given directory (ignoring 'node_modules' and directories with 'env' in their name).
    For each function found, add the following metadata:
      - "file": Relative file path from the project root.
      - "breadcrumbs": A string showing the file's directory hierarchy.
    Then filter out call references to functions that are built-ins or not defined anywhere in the project.
    """
    complete_graph = {}
    for root, dirs, files in os.walk(directory):
        # Ignore 'node_modules' and any directory that contains 'env' in its name.
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        dirs[:] = [d for d in dirs if 'env' not in d.lower()]
        
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                file_graph = analyze_file(filepath)
                # Compute the relative path from the project root.
                relative_path = os.path.relpath(filepath, directory)
                # Create breadcrumbs by joining the parts of the relative path.
                breadcrumbs = " > ".join(relative_path.split(os.sep))
                # Add file metadata for each function.
                for func_name, func_info in file_graph.items():
                    if func_info.get('code'):  # Only include functions with code.
                        file_graph[func_name]["file"] = relative_path
                        file_graph[func_name]["breadcrumbs"] = breadcrumbs
                        complete_graph[func_name] = file_graph[func_name]
    
    # Filtering step:
    # Only keep calls that refer to functions defined in the project and that are not built-ins.
    defined_functions = set(complete_graph.keys())
    built_in_names = {name for name, obj in vars(builtins).items() if callable(obj)}
    for func, details in complete_graph.items():
        details["calls"] = [
            call for call in details.get("calls", [])
            if call in defined_functions and call not in built_in_names
        ]
    return complete_graph

def select_directory():
    """Open a file dialog to select a project directory."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window.
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
