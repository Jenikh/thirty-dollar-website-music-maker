import os
from time import sleep

from sounds import find_all_sounds,download_all_sounds
from tools import clear


sounds_list = find_all_sounds()
print("DOWNLOADING ALL SOUNDS")
download_all_sounds(sounds_list)
print("DOWNLOAD COMPLETE!")

sleep(1)

try:
    while True:
        clear()
        print("Thirty dolar music maker")
        print("-----------------------")
        
        print("1) Make song from mp3")
        print("X) Exit")
        
        cmd = input("Action: ")
        if cmd == "X" or cmd == "x":
            raise KeyboardInterrupt()
        elif cmd == "1":
            song_file = input("Song file: ")
            if os.path.exists(song_file) and os.path.isfile(song_file):
                print("Starting...")
            else:
                print("Invalid file path")
                sleep(1)
except KeyboardInterrupt,EOFError:
    print()
    print("Exiting...")
    exit()
except Exception as e:
    print(e)
    exit()