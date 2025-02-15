import ast
import os
import json

class CallGraphAnalyzer(ast.NodeVisitor):
    def __init__(self):
        # Dictionary mapping function names to a list of functions they call
        self.call_graph = {}
        self.current_function = None

    def visit_FunctionDef(self, node):
        # Set current function context
        prev_function = self.current_function
        self.current_function = node.name
        
        # Initialize the node in our call graph if it doesn't exist
        if node.name not in self.call_graph:
            self.call_graph[node.name] = []
        
        # Traverse the body of the function
        self.generic_visit(node)
        
        # Restore the previous context
        self.current_function = prev_function

    def visit_Call(self, node):
        # Try to extract the called function's name
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            # For method calls (e.g., obj.method())
            func_name = node.func.attr
        else:
            func_name = "unknown"
        
        # Record the call under the current function if set
        if self.current_function:
            self.call_graph[self.current_function].append(func_name)
        
        self.generic_visit(node)

def analyze_file(filepath):
    with open(filepath, "r") as file:
        tree = ast.parse(file.read(), filename=filepath)
    analyzer = CallGraphAnalyzer()
    analyzer.visit(tree)
    return analyzer.call_graph

def analyze_directory(directory):
    complete_graph = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                file_graph = analyze_file(filepath)
                # Merge the file's call graph into the complete graph
                complete_graph.update(file_graph)
    return complete_graph

if __name__ == "__main__":
    import os

    directory_to_analyze = input("Enter the directory path to analyze: ").strip()
    
    # Check if the input is a valid directory
    if not os.path.isdir(directory_to_analyze):
        print("Invalid directory. Please make sure the path is correct.")
        exit(1)
        
    call_graph = analyze_directory(directory_to_analyze)
    with open("call_graph.json", "w") as f:
        json.dump(call_graph, f, indent=2)
    print("Analysis complete! Call graph saved to call_graph.json")
