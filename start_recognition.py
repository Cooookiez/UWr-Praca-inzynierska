
import os
import cv2
import json
import enum
import time
import random
import numpy as np
import config as cf
import tkinter as tk
import face_recognition
import config_helper as ch

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
alertPeople = {}

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
        for encoded_face_py in encoded_faces_py[name]:
            encoded_faces_np[name].append(np.array(encoded_face_py))
    
    # prepare to return
    known_faces = {
        "encoding": [],
        "name": []
    }
    for name in encoded_faces_np:
        for encoded_face_np in encoded_faces_np[name]:
            known_faces["name"].append(name)
            known_faces["encoding"].append(encoded_face_np)
    
    return known_faces

def encodeThisFrameFaces(frame, known_faces):
    # rotate frame if needed
    if cf.CAM_ROTATION != ch.rotate[0]:
        frame = cv2.rotate(frame, ch.CAM_ROTATION)
        
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small_frame = small_frame[:, :, ::-1]
    
    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_faces['encoding'], face_encoding)
        name = cf.UNKNOWN_NAME

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_faces['encoding'], face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_faces['name'][best_match_index]

        face_names.append(name)
    return face_names

def names2alert(face_names):
    face_names2alert = []
    for face_name in face_names:
        if face_name in alertPeople.keys():
            # check last seen time
            time_difference = time.time() - alertPeople[face_name]
            if time_difference >= cf.ALERT_DELAY_IGNORE:
                # notify
                face_names2alert.append(face_name)
            alertPeople[face_name] = time.time()
        else:
            # notify
            alertPeople[face_name] = time.time()
            face_names2alert.append(face_name)
    return face_names2alert

def mainloop(known_faces):
    # get reference to camera
    video_capture = cv2.VideoCapture(cf.CAM_REF)
    
    # Initialize some variables
    process_this_frame = True
    
    # loop
    while True:
        # print(random.randint(100000, 999999))
        # Grab a single frame of video
        ret, frame = video_capture.read()
        
        # evryy second frame
        if process_this_frame:
            # get all faces in frame
            names = encodeThisFrameFaces(frame, known_faces)
            print(random.randint(100000, 999999), names)
            
            # get faces taht do not repeet too soon
            names = names2alert(names)
            print(random.randint(10000000, 99999999), names)

        process_this_frame = not process_this_frame

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
    known_faces = load_encoded_files()
    mainloop(known_faces)