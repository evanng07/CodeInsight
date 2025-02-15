from flask import Flask, jsonify, render_template
import json

app = Flask(__name__)

# Load your call graph data (generated from the previous step)
with open("call_graph.json", "r") as f:
    call_graph = json.load(f)

@app.route("/data")
def data():
    return jsonify(call_graph)

@app.route("/")
def index():
    return render_template("index.html")  # This will be your front-end

if __name__ == "__main__":
    app.run()
