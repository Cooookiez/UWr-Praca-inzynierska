

import tkinter as tk
import os
import enum
import config as cf
import json
import numpy as np

#* classes
class Mods(enum.Enum):
    IDLE = 1
    PROCESSING = 2
    UNKNOWN = 3
    KNOWN = 4

#* declare variables with none value
window = None
lGreeting = None
lName = None

#* declare global variables
PATH_TO_ROOT = os.getcwd()
appBackground = {
    Mods.IDLE: '#000000',      # black
    Mods.PROCESSING: '#4b4b4b', # grey (darker)
    Mods.UNKNOWN: '#696969',   # gray (lighter)
    Mods.KNOWN: '#00ff00',     # green
}

#* functions
def load_encoded_files():
    # go to directory with people sub-directories & get people names
    people_dir_path = os.path.join(PATH_TO_ROOT, cf.KNOW_PEOPLE_DIR_PATH_NAME)
    os.chdir(people_dir_path)
    names = list(filter(os.path.isdir, os.listdir(os.curdir)))
    
    # get path to faces.json
    encoded_faces_json_path = []
    for name in names:
        if name != cf.UNKNOWN_WELCOMES_DIR_PATH:
            encoded_faces_json_path.append(
                os.path.join(PATH_TO_ROOT, cf.KNOW_PEOPLE_DIR_PATH_NAME, name, cf.JSON_FILE_NAME)
            )
    
    # get file.json to python array
    encoded_faces_py = {}
    for encoded_face_json_path in encoded_faces_json_path:
        with open(encoded_face_json_path) as json_file:
            data = json.load(json_file)
        for name in data:
            encoded_faces_py[name] = data[name]
    
    # get python array to np array
    encoded_faces_np = {}
    for name in encoded_faces_py:
        encoded_faces_np[name] = []
        for encoded_face_py in encoded_faces_py:
            encoded_faces_np[name].append(np.array(encoded_face_py))
    
    # prepare to return
    known_faces = {
        "encodings": [],
        "names": []
    }
    for name in encoded_faces_np:
        for encoded_face_np in encoded_faces_np[name]:
            known_faces["names"].append(name)
            known_faces["encodings"].append(encoded_face_np)
    
    return known_faces

#* main
if __name__ == '__main__':
    
    # create app window
    window = tk.Tk()
    window.title("Face Recognition")
    window.geometry("480x320")
    #// window.attributes("-fullscreen", True) #! fullscreen na puźniej
    window.configure(background=appBackground[Mods.IDLE])
    
    # window labels
    lGreeting = tk.Label(
        window,
        anchor="center",
        text=f"Witaj",
        fg='#000000',
        font=("Helvetica", 64, "bold")
    )
    lName = tk.Label(
        window,
        anchor="center",
        text=f"_____ ___",
        fg='#000000',
        font=("Helvetica", 48)
    )
    
    #window.update()
    
    # load known faces
    known_face = load_encoded_files()
    print(known_face)