
import os
import cv2
import json
import enum
import time
import pygame
import random
import numpy as np
import config as cf
import tkinter as tk
import face_recognition
import config_helper as ch

#* classes
class Mod(enum.Enum):
    IDLE = 1
    PROCESSING = 2
    UNKNOWN = 3
    KNOWN = 4

class Mod2Show:
    time_start = 0
    time_end = 0
    name = None
    activeMod = None
    durationTimes = {
        Mod.UNKNOWN: 3, # 3s
        Mod.KNOWN: 6,   # 6s
    }
    
    def __init__(self, appActiveMode, name=None, timeStart=None, timeEnd=None):
        self.activeMod = appActiveMode
        self.name = name or cf.UNKNOWN_DISPLAY_NAME
        self.time_start = timeStart or time.time()
        self.time_end = timeEnd or self.time_start + self.durationTimes[self.activeMod]
        
    def __lt__(self, other):
        return self.time_start < other.time_start

#* declare variables with none value
window = None
lGreeting = None
lName = None
lastEntry = None

#* declare global variables
PATH_TO_ROOT = os.getcwd()
appBackground = {
    Mod.IDLE: '#000000',      # black
    Mod.PROCESSING: '#4b4b4b', # grey (darker)
    Mod.UNKNOWN: '#696969',   # gray (lighter)
    Mod.KNOWN: '#00ff00',     # green
}
alertPeople = {}
mods2ShowQueue = []

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
        frame = cv2.rotate(frame, cf.CAM_ROTATION)
        
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

def addPersone2queue(mode, name = None):
    mods2ShowQueue.sort()
    if len(mods2ShowQueue) > 0:
        lastPersoneEndTime = mods2ShowQueue[-1].time_end
        mods2ShowQueue.append(Mod2Show(mode, name, timeStart=lastPersoneEndTime))
    else:
        mods2ShowQueue.append(Mod2Show(mode, name))

def printQueue(end="\n"):
    print('[', end='')
    for entry in mods2ShowQueue:
        print(entry.name, end=", ")
    print(']', end=end)

def sayHello(name):
    # get mp3' dir
    path_to_welcomes_for_name = os.path.join(PATH_TO_ROOT, cf.KNOW_PEOPLE_DIR_PATH_NAME)
    if name == cf.UNKNOWN_NAME:
        path_to_welcomes_for_name = os.path.join(path_to_welcomes_for_name, cf.UNKNOWN_WELCOMES_DIR_PATH)
    else:
        path_to_welcomes_for_name = os.path.join(path_to_welcomes_for_name, name, cf.WELCOMES_DIR_PATH_NAME)
        
    # get mp3s
    mp3s = []
    for file in os.listdir(path_to_welcomes_for_name):
        # print(file)
        extension = os.path.splitext(file)[1] # extension of file
        # print(extension)
        if extension.lower() == ".mp3":
            mp3s.append(os.path.join(path_to_welcomes_for_name, file))
            
    # random file to play
    mp3_to_paly = random.choice(mp3s)
        
    # play
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_to_paly)
    pygame.mixer.music.play()
    pass

def screenVisualization():
    # global appLastMode
    global lastEntry
    global lGreeting
    global lName
    global window
    
    if len(mods2ShowQueue) > 0:
        mods2ShowQueue.sort()
        
        # is queues entry still valid
        # if not, delete and go to next
        if time.time() >= mods2ShowQueue[0].time_end:
            mods2ShowQueue.pop(0)
            lGreeting.pack_forget()
            lName.pack_forget()
            screenVisualization()
            
        # queues entry is still valid
        else:
            entry = mods2ShowQueue[0]
            if entry != lastEntry:
                # background color
                window.configure(background=appBackground[entry.activeMod])
                lGreeting.configure(background=appBackground[entry.activeMod])
                lName.configure(background=appBackground[entry.activeMod])
                
                # zmien textu
                lGreeting.config(text=cf.GREETINGS_WORD)
                lName.config(text=entry.name)
                
                # wyswietl text
                lGreeting.pack()
                lName.pack()
                
                # render
                window.update()
                
                # play sound
                if entry.activeMod == Mod.UNKNOWN:
                    sayHello(cf.UNKNOWN_NAME)
                else:
                    sayHello(entry.name)
                
                lastEntry = entry
    
    # queue is empty, go to IDLE
    else:
        lGreeting.pack_forget()
        lName.pack_forget()
        window.configure(background=appBackground[Mod.IDLE])
        window.update()

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
            
            # add peaple to queue
            for name in names:
                if name == cf.UNKNOWN_NAME:
                    addPersone2queue(Mod.UNKNOWN)
                else:
                    addPersone2queue(Mod.KNOWN, name)
            
            printQueue()
            screenVisualization()

        process_this_frame = not process_this_frame

#* main
if __name__ == '__main__':
    
    # create app window
    window = tk.Tk()
    window.title("Face Recognition")
    #//window.geometry("480x320")
    window.attributes("-fullscreen", True)
    window.configure(background=appBackground[Mod.IDLE])
    
    # window labels
    lGreeting = tk.Label(
        window,
        anchor="center",
        text=cf.GREETINGS_WORD,
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