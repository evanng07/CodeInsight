# app.py
from flask import Flask, jsonify, render_template
import os
import ast
import json

app = Flask(__name__)

# --- Analyzer Functions (unchanged) ---
class CallGraphAnalyzer(ast.NodeVisitor):
    def __init__(self, source):
        self.call_graph = {}
        self.function_code = {}
        self.source = source
        self.current_function = None

    def visit_FunctionDef(self, node):
        prev_function = self.current_function
        self.current_function = node.name
        if node.name not in self.call_graph:
            self.call_graph[node.name] = []
        code_snippet = ast.get_source_segment(self.source, node)
        self.function_code[node.name] = code_snippet if code_snippet else ""
        self.generic_visit(node)
        self.current_function = prev_function

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        else:
            func_name = "unknown"
        if self.current_function:
            self.call_graph[self.current_function].append(func_name)
        self.generic_visit(node)

def analyze_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        source = file.read()
    tree = ast.parse(source, filename=filepath)
    analyzer = CallGraphAnalyzer(source)
    analyzer.visit(tree)
    result = {}
    for func in analyzer.call_graph:
        result[func] = {
            "code": analyzer.function_code.get(func, ""),
            "calls": analyzer.call_graph[func]
        }
    return result

def analyze_directory(directory):
    complete_graph = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                file_graph = analyze_file(filepath)
                complete_graph.update(file_graph)
    return complete_graph

# --- Flask Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    # Read the call graph data from the JSON file.
    if os.path.exists("call_graph.json"):
        with open("call_graph.json", "r", encoding="utf-8") as f:
            call_graph_data = json.load(f)
        return jsonify(call_graph_data)
    else:
        return jsonify({"error": "No call graph data available"}), 404

if __name__ == "__main__":
    app.run(debug=True)
