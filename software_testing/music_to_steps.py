import os
import sys
import json
import random
import librosa
import yt_dlp
import numpy as np

DIRECTIONS = ["left", "down", "up", "right"]

def download_audio(youtube_url, output_path="song.mp3"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio...")
        ydl.download([youtube_url])
    os.rename("temp_audio.mp3", output_path)
    return output_path

def generate_steps(mp3_path, step_density=1.0):
    print("Analyzing audio...")
    y, sr = librosa.load(mp3_path)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(tempo)
    beat_times = librosa.frames_to_time(beats, sr=sr)

    if step_density < 1.0:
        beat_times = beat_times[::int(1/step_density)]

    print(f"Detected {len(beat_times)} beats at ~{tempo:.1f} BPM")

    steps = []
    for beat_time in beat_times:
        direction = random.choice(DIRECTIONS)
        steps.append({
            "time": round(float(beat_time), 3),
            "direction": direction
        })
    return tempo, steps

def save_steps_json(song_title, tempo, steps, output_file="static/output_steps.json"):
    data = {
        "song": song_title,
        "bpm": round(tempo, 2),
        "arrows": steps
    }
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved step file to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_ddr_from_youtube.py <YouTube_URL>")
        sys.exit(1)

    youtube_url = sys.argv[1]
    song_file = "static/downloaded_song.mp3"

    try:
        download_audio(youtube_url, song_file)
        tempo, steps = generate_steps(song_file)
        save_steps_json("YouTube Song", tempo, steps)
    except:
        print('Error occurred.')