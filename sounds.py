import requests


class Sound:
    def __init__(self,url) -> None:
        self.url=url
    def download(self) -> int:
        """Downloads song (returns status code)"""
        print(f"DOWNLOADING: {self.url}")
        req = requests.get(self.url)
        if req.ok:
            with open(f"sounds/{self.url.split('/')[-1]}", "wb") as f:
                f.write(req.content)
            print(f"DOWNLOADED: {self.url}")
        else:
            print(f"REQUEST FAILED FOR URL: {self.url}")
        
        return req.status_code
    def __repr__(self) -> str:
        return f"Sound(url={self.url})"

def find_all_sounds():
    sounds = requests.get("https://thirtydollar.website/sounds.json")
    sounds_list = []
    sound_url = "https://thirtydollar.website/sounds/{sound_name}.wav"
    for sound in sounds.json():
        sounds_list.append(Sound(sound_url.format(sound_name=sound["id"])))
        
    return sounds_list

def download_all_sounds(sounds_list:list):
    for sound in sounds_list:
        sound.download()
    return sounds_list