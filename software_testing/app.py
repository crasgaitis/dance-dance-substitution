from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/steps")
def steps():
    with open("static/output_steps.json") as f:
        step_data = json.load(f)
    return jsonify(step_data)

if __name__ == "__main__":
    app.run(debug=True, port=3000)
