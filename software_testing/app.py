from flask import Flask, render_template, request, jsonify
import json, os
from step_extractor import download_audio, create_analyzers, extract_mel_feats
import numpy as np
import random

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", song_ready=False)

@app.route("/create", methods=["POST"])
def create():
    # TODO: user interface to build new json file
    pass

@app.route("/process", methods=["POST"])
def process():
    youtube_url = request.form["youtube_url"]
    
    output_path = "static/downloaded_song.mp3"
    download_audio(youtube_url, output_path)

    # getting melody
    fs = 44100
    nhop = 512
    nffts = [1024, 2048, 4096]
    analyzers = create_analyzers(fs=fs, nhop=nhop, nffts=nffts, mel_nband=80)
    mel_feats = extract_mel_feats(output_path, analyzers, fs=fs, nhop=nhop, nffts=nffts)

    # melody steps
    energy = mel_feats.mean(axis=(1, 2))
    energy = (energy - energy.min()) / (energy.max() - energy.min())
    threshold = 0.5
    peak_indices = np.where(energy > threshold)[0]

    min_gap_frames = int(0.4 * fs / nhop)
    selected = [peak_indices[0]]
    for i in peak_indices[1:]:
        if i - selected[-1] >= min_gap_frames:
            selected.append(i)

    arrow_times = [round(i * nhop / fs, 3) for i in selected]
    directions = ['up', 'down', 'left', 'right']
    arrows = [{"time": t, "direction": random.choice(directions)} for t in arrow_times]

    step_chart = {
        "song": "downloaded_song",
        "arrows": arrows
    }

    with open("static/output_steps.json", "w") as f:
        json.dump(step_chart, f, indent=2)

    # wav to mp3
    os.system("ffmpeg -y -i static/downloaded_song.wav static/downloaded_song.mp3")

    return render_template("index.html", song_ready=True, num_steps=len(arrows))

@app.route("/steps")
def steps():
    with open("static/output_steps.json") as f:
        return jsonify(json.load(f))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)
