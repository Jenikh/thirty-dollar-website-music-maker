from sounds import find_all_sounds,download_all_sounds
import os

os.makedirs("sounds", exist_ok=True)

sounds_list = find_all_sounds()
download_all_sounds(sounds_list)