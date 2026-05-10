import librosa
import numpy as np
import os
from sklearn.neighbors import NearestNeighbors

STEP_BEAT = 1.0  # work per beat instead of micro-slices

SOUNDS = []  # filled from your library

def load_library(folder):
    features = []
    files = []

    for f in os.listdir(folder):
        if f.endswith((".wav", ".mp3")):
            path = os.path.join(folder, f)
            y, sr = librosa.load(path, sr=None)

            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            feat = np.mean(mfcc, axis=1)

            features.append(feat)
            files.append(path)

    return np.array(features), files


def get_features(y, sr):
    print("Calculating features...")
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return np.mean(mfcc, axis=1)


def energy(y):
    print("Calculating energy...")
    return np.mean(librosa.feature.rms(y=y))


def transpose_from_pitch(y, sr):
    print("Transposing...")
    f0, _, _ = librosa.pyin(y, fmin=50, fmax=500, sr=sr)

    if f0 is None or np.isnan(f0).all():
        return 0

    pitch = np.nanmean(f0)

    # More flexible pitch mapping
    if pitch < 100:
        return -2
    elif pitch < 150:
        return -1
    elif pitch > 300:
        return 2
    elif pitch > 220:
        return 1
    return 0


def detect_loops(sequence):
    """
    Very simple loop detection:
    finds repeated patterns of same sound
    """
    print("Detecting loops...")
    loops = []
    i = 0

    while i < len(sequence) - 2:
        if sequence[i] == sequence[i+1]:
            loops.append((i, sequence[i]))
            i += 2
        else:
            i += 1
    print(f"Found {len(loops)} loops")
    return loops


def build_next_level(mp3_path, sounds_folder):
    print("Loading...")
    lib_features, lib_files = load_library(sounds_folder)

    nn = NearestNeighbors(n_neighbors=1)
    nn.fit(lib_features)

    y, sr = librosa.load(mp3_path, sr=None)

    duration = librosa.get_duration(y=y, sr=sr)

    beats = librosa.beat.beat_track(y=y, sr=sr)[1]
    beat_times = librosa.frames_to_time(beats, sr=sr)

    output = ["!speed@300"]

    last_time = 0.0
    prev_sound = None
    run_length = 0

    sequence_buffer = []

    for i in range(len(beat_times)):
        start = int(last_time * sr)
        end = int(beat_times[i] * sr)

        chunk = y[start:end]

        if len(chunk) == 0:
            continue

        feat = get_features(chunk, sr).reshape(1, -1)
        _, idx = nn.kneighbors(feat)

        sound_file = lib_files[idx[0][0]]
        sound = os.path.splitext(os.path.basename(sound_file))[0]

        t = transpose_from_pitch(chunk, sr)
        vol = int(np.clip(energy(chunk) * 7000, 20, 100))

        cmd = f"!volume@{vol}"

        if t != 0:
            cmd += f"|{sound}@{t}"
        else:
            cmd += f"|{sound}"

        # --- detect repetition for loops ---
        if sound == prev_sound:
            run_length += 1
        else:
            if run_length >= 3:
                cmd = f"!loopmany@{run_length}|" + cmd
            run_length = 1

        # --- occasional combine for density ---
        if i % 6 == 0:
            cmd += "|!combine"

        # --- occasional stops for structure ---
        if energy(chunk) < 0.01:
            cmd += "|!stop@1"

        sequence_buffer.append(cmd)
        output.append(cmd)

        prev_sound = sound
        last_time = beat_times[i]

    # --- add final duration control ---
    print("Finalizing...")
    current_duration = last_time
    if current_duration < duration:
        output.append(f"!stop@{int(duration - current_duration)}")

    print(f"Input duration: {duration:.3f}s")
    print(f"Output beats: {len(sequence_buffer)}")

    return "|".join(output)


if __name__ == "__main__":
    result = build_next_level("tadm_soundtrack.mp3", "sounds")
    print("\n=== FINAL STRING ===\n")
    print(result)