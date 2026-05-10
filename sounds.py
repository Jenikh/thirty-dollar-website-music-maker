import requests
from tqdm import tqdm
import os

class Sound:
    def __init__(self, url) -> None:
        self.url = url

    def download(self) -> int:
        """Downloads song (returns status code)"""
        filename = os.path.join("sounds", self.url.split("/")[-1])
        if os.path.exists(filename):
            return 200
        # Stream download for efficiency
        with requests.get(self.url, stream=True) as req:
            if req.status_code == 200:
                total_size = int(req.headers.get("content-length", 0))

                with open(filename, "wb") as f, tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    desc=f"Downloading {self.url.split('/')[-1]}",
                    leave=True
                ) as bar:
                    for chunk in req.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))

                return req.status_code
            else:
                print(f"REQUEST FAILED FOR URL: {self.url}")
                return req.status_code

    def __repr__(self) -> str:
        return f"Sound(url={self.url})"


def find_all_sounds():
    sounds = requests.get("https://thirtydollar.website/sounds.json").json()
    sound_url = "https://thirtydollar.website/sounds/{sound_name}.wav"

    sounds_list = []
    for sound in tqdm(sounds, desc="Building sound list"):
        sounds_list.append(
            Sound(sound_url.format(sound_name=sound["id"]))
        )

    return sounds_list


def download_all_sounds(sounds_list: list):
    os.makedirs("sounds", exist_ok=True)

    for sound in tqdm(sounds_list, desc="Downloading all sounds"):
        sound.download()

    return sounds_list