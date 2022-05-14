import os
import json
import struct
from click import command
import numpy as np
import cv2
import time
import face_recognition
import threading
import random
import pygame
import config
import config_helper as ch
import tkinter as tk
from PIL import ImageTk, Image
import enum

# from config
KNOW_PEOPLE_DIR_PATH_NAME = config.KNOW_PEOPLE_DIR_PATH_NAME
JSON_FILE_NAME = config.JSON_FILE_NAME
UNKNOWN_NAME = config.UNKNOWN_NAME
WELCOMES_DIR_PATH_NAME = config.WELCOMES_DIR_PATH_NAME
ALERT_DELAY_IGNORE = config.ALERT_DELAY_IGNORE
CAM_REF = config.CAM_REF

class Mods(enum.Enum):
    IDLE = 1
    PROCESSING = 2
    UNKNOWN = 3
    KNOWN = 4
    
class Mod2Show:
    time_start = 0
    time_end = 0
    name = None
    activeMode = None
    modTimes = {
        Mods.IDLE: -1,         # inf
        Mods.PROCESSING: 0,    # 0s
        Mods.UNKNOWN: 3,       # 3s
        Mods.KNOWN: 6,         # 6s
    }
    def __init__(self, appActiveMode, name = None):
        self.time_start = time.time();
        self.time_end = self.time_start + self.modTimes[appActiveMode]
        self.activeMode = appActiveMode
        if name != None:
            self.name = name
        else:
            self.name = "Przybyszu"
    def __lt__(self, other):
        return self.time_start < other.time_start
    pass

# Initialize some variablesQ
PATH_TO_ROOT = os.getcwd()
ALERT_PEOPLE = {}
face_locations = []
face_encodings = []
appBackground = {
    Mods.IDLE: '#000000',      # black
    Mods.PROCESSING: '#4b4b4b', # grey (darker)
    Mods.UNKNOWN: '#696969',   # gray (lighter)
    Mods.KNOWN: '#00ff00',     # green
}
appImages = {
    'QuestionMark': None,
    'Hello': None,
}
Tk = None
mods2ShowQueue = []
lastMods2Show = None
appLastColor = None
appActiveColor = appBackground[Mods.IDLE]
lGreeting = None
lName = None
appLastMode = None

def load_encoded_files(path2root=PATH_TO_ROOT):
    # go to directory with people sub-directories & get people names
    people_dir_path = os.path.join(path2root, KNOW_PEOPLE_DIR_PATH_NAME)
    os.chdir(people_dir_path)
    names = list(filter(os.path.isdir, os.listdir(os.curdir)))

    # get path to faces.json
    encoded_faces_json_path = []
    for name in names:
        if name == "welcomes_unknown":
            continue
        encoded_faces_json_path.append(
            os.path.join(path2root, KNOW_PEOPLE_DIR_PATH_NAME, name, JSON_FILE_NAME)
        )

    # get file.json to python array
    encoded_faces = {}
    for encoded_face_json in encoded_faces_json_path:
        with open(encoded_face_json) as json_file:
            data = json.load(json_file)
        for name in data:
            encoded_faces[name] = data[name]

    # get python array to np array
    encoded_faces_np = {}
    for name in encoded_faces:
        encoded_faces_np[name] = []
        for encoded_face in encoded_faces[name]:
            encoded_face_np = np.array(encoded_face)
            # encoded_face_np = np.ndarray(encoded_face)
            encoded_faces_np[name].append(encoded_face_np)

    # prepare to return
    known_face = {
        "encodings": [],
        "names": []
    }
    for name in encoded_faces_np:
        for encoded_face_np in encoded_faces_np[name]:
            known_face["names"].append(name)
            known_face["encodings"].append(encoded_face_np)

    return known_face

def encodeThisFrameFaces(frame):
    # global addPersoneMode2queue
    timeStart = time.time()
    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face["encodings"], face_encoding)
        name = UNKNOWN_NAME

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face["encodings"], face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face["names"][best_match_index]

        face_names.append(name)
    # check if person desnt repeat too soon
    face_names_to_alert = []
    time_differences = {}
    for regognized_face in face_names:
        if regognized_face in ALERT_PEOPLE.keys():
            # check last seen time
            time_difference = time.time() - ALERT_PEOPLE[regognized_face]
            time_differences[regognized_face] = time_difference
            ALERT_PEOPLE[regognized_face] = time.time()
            if time_difference >= ALERT_DELAY_IGNORE:
                # notify
                face_names_to_alert.append(regognized_face)
                pass
            else:
                # skip
                pass
            pass
        else:
            # add to ALERT_PEOPLE
            # notify
            ALERT_PEOPLE[regognized_face] = time.time()
            face_names_to_alert.append(regognized_face)
            pass
    # print(f"[{threading.active_count()}] ", *face_names_to_alert, f" ({(time.time() - timeStart):.4}s)\t\t\t{time_differences}")
    
    for face in face_names_to_alert:
        if name == "Unknown":
            addPersoneMode2queue(Mods.UNKNOWN)
        else:
            addPersoneMode2queue(Mods.KNOWN, name)
        # say_hello(face)
        pass
    # back2idle()
    pass

def say_hello(name, path2root=PATH_TO_ROOT):
    
    appActiveName = name
    
    # get mp3' dir
    mp3s = []
    path_to_welcomes_for_name = os.path.join(path2root, KNOW_PEOPLE_DIR_PATH_NAME)
    if name == "Unknown":
        path_to_welcomes_for_name = os.path.join(path_to_welcomes_for_name, "welcomes_unknown")
    else:
        path_to_welcomes_for_name = os.path.join(path_to_welcomes_for_name, name, WELCOMES_DIR_PATH_NAME)
        
    # get mp3s
    for file in os.listdir(path_to_welcomes_for_name):
        # print(file)
        extension = os.path.splitext(file)[1] # extension of file
        # print(extension)
        if extension.lower() == ".mp3":
            mp3s.append(os.path.join(path_to_welcomes_for_name, file))
    # print(mp3s)        
        
    # rand file to play
    mp3_to_paly = random.choice(mp3s)
    # print(mp3_to_paly)
    
    # play      
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_to_paly)
    pygame.mixer.music.play()
    while pygame.mixer.get_busy() == True:
        continue
    # back2idle()
    pass

def addPersoneMode2queue(mode, name = None):
    mods2ShowQueue.append(Mod2Show(mode, name))
    pass

def printQueue():
    for person in mods2ShowQueue:
        print(person.name, end=", ")
    print()
    pass

def start_cam_and_staff(known_face):
    video_capture = cv2.VideoCapture(CAM_REF)
    
    # Initialize some variables
    face_names = []
    process_this_frame = True

    # start
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        # rotate frame if needed
        if config.CAM_ROTATION != ch.rotate[0]:
            frame = cv2.rotate(frame, config.CAM_ROTATION)
        # Resize frame of video to 1/4 size for faster face recognition processing
        # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        # Only process every other frame of video to save time
        thread = threading.Thread(target=encodeThisFrameFaces, args=(rgb_small_frame,))
        if process_this_frame:
            # encodeThisFrameFaces(rgb_small_frame)
            # print("appActiveColor: ", appActiveColor, end="\t\t")
            thread.start()
            # thread.join()
            

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        process_this_frame = not process_this_frame
        screenVisualization();

def screenVisualization():
    printQueue()
    global appLastMode
    global lastMods2Show
    global lGreeting
    global lName
    # print(f"\t|{mods2ShowQueue}|")
    if len(mods2ShowQueue) > 0:
        mods2ShowQueue.sort()
        # is queue itme still valid
        if time.time() > mods2ShowQueue[0].time_end:
            # pop
            mods2ShowQueue.pop(0)
            lGreeting.pack_forget()
            lName.pack_forget()
            screenVisualization()
            pass
        else:
            activeMode2show = mods2ShowQueue[0]
            # change only if mod2show is new
            if activeMode2show != lastMods2Show:
                # background color
                Tk.configure(background=appBackground[activeMode2show.activeMode])
                lGreeting.configure(background=appBackground[activeMode2show.activeMode])
                lName.configure(background=appBackground[activeMode2show.activeMode])
                
                # zmien imie textu
                lName.config(text=activeMode2show.name)
                
                # wyswietl text
                lGreeting.pack()
                lName.pack()
                
                Tk.update()
                if activeMode2show.activeMode == Mods.UNKNOWN:
                    say_hello("Unknown")
                else:
                    say_hello(activeMode2show.name)
                lastMods2Show = activeMode2show
                appLastMode = activeMode2show.activeMode;
                pass
            pass
        pass
    else:
        # change to idle (expect it is not idle)
        if appLastMode != Mods.IDLE:
            Tk.configure(background=appBackground[Mods.IDLE])
            Tk.update()
        appLastMode = Mods.IDLE;

if __name__ == '__main__':
    # Tkiner app
    Tk = tk.Tk()
    Tk.geometry("480x320")
    Tk.title("Face Recognition")
    # Tk.attributes("-fullscreen", True) #! fullscreen na puźniej
    Tk.configure(background=appBackground[Mods.IDLE])
    # labels
    lGreeting = tk.Label(
        Tk,
        anchor="center",
        text=f"Witaj",
        fg='#000000',
        font=("Helvetica", 64, "bold")
    )
    lName = tk.Label(
        Tk,
        anchor="center",
        text=f"_____ ___",
        fg='#000000',
        font=("Helvetica", 48)
    )
    #
    Tk.update()
    
    known_face = load_encoded_files()
    start_cam_and_staff(known_face)
    
