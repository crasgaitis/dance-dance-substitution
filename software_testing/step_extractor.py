from essentia.standard import MonoLoader, FrameGenerator, Windowing, Spectrum, MelBands
import numpy as np
from pytubefix import YouTube
import os
import subprocess

def download_audio(youtube_url, output_path="audio.mp3"):
    yt = YouTube(youtube_url)
    audio_stream = yt.streams.get_audio_only()
    temp_file = "temp_audio.m4a"
    audio_stream.download(filename=temp_file)
    if not output_path.endswith(".m4a"):
        subprocess.run([
            "ffmpeg", "-y", "-i", temp_file, output_path
        ], check=True)
        os.remove(temp_file)
    else:
        os.rename(temp_file, output_path)
    print(f"Audio downloaded as {output_path}")
    return output_path

def create_analyzers(fs=44100.0,
                     nhop=512,
                     nffts=[1024, 2048, 4096],
                     mel_nband=80,
                     mel_freqlo=27.5,
                     mel_freqhi=16000.0):
    analyzers = []
    for nfft in nffts:
        window = Windowing(size=nfft, type='blackmanharris62')
        spectrum = Spectrum(size=nfft)
        mel = MelBands(inputSize=(nfft // 2) + 1,
                       numberBands=mel_nband,
                       lowFrequencyBound=mel_freqlo,
                       highFrequencyBound=mel_freqhi,
                       sampleRate=fs)
        analyzers.append((window, spectrum, mel))
    return analyzers

def extract_mel_feats(audio_fp, analyzers, fs=44100.0, nhop=512, nffts=[1024, 2048, 4096], log_scale=True):
    loader = MonoLoader(filename=audio_fp, sampleRate=fs)
    samples = loader()
    feat_channels = []
    for nfft, (window, spectrum, mel) in zip(nffts, analyzers):
        feats = []
        for frame in FrameGenerator(samples, nfft, nhop):
            frame_feats = mel(spectrum(window(frame)))
            feats.append(frame_feats)
        feat_channels.append(feats)

    feat_channels = np.transpose(np.stack(feat_channels), (1, 2, 0))

    if log_scale:
        feat_channels = np.log(feat_channels + 1e-16)

    return feat_channels