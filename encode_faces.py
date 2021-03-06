"""
encode faces to file
python3 encode_faces "Krzysztof Kukiz" – encode single face
python3 encode_faces – encode all faces
"""
import os
import time
import face_recognition
import json
import sys
import gtts

VALID_IMAGES_EXTENSIONS = [".jpg", ".jpeg", ".png"]
KNOW_PEOPLE_DIR_PATH_NAME = "known_people"
IMAGES_DIR_PATH_NAME = "images"
WELCOMES_DIR_PATH_NAME = "welcomes"
BASIC_WELCOME_FILE_NAME = "welcome01.mp3"
JSON_FILE_NAME = "faces.json"
PATH_TO_ROOT = os.getcwd()

def prepare_dir(name, path2root=PATH_TO_ROOT):

    # get person directory
    person_dir_path = os.path.join(path2root, KNOW_PEOPLE_DIR_PATH_NAME, name)

    # list all image files in person's main directory
    paths_to_images_in_wrong_dir = {}
    for file in os.listdir(person_dir_path):
        extension = os.path.splitext(file)[1] # extension of file
        if extension.lower() in VALID_IMAGES_EXTENSIONS:
            paths_to_images_in_wrong_dir[file] = os.path.join(person_dir_path, file)

    # chech if subpath for pictures does exist. otherwise create it
    images_dir = os.path.join(person_dir_path, IMAGES_DIR_PATH_NAME)
    if not os.path.isdir(images_dir): # path is not dir, create it
        # chechk if there is no file named "images". If is, delete it
        if os.path.isfile(images_dir): # file named "images" exist
            os.remove(images_dir) # delete it
        os.chdir(person_dir_path)
        os.mkdir(IMAGES_DIR_PATH_NAME) # create directory "images"
        
    # chech if subpath for welcomes does exist. otherwise create it
    welcomes_dir = os.path.join(person_dir_path, WELCOMES_DIR_PATH_NAME)
    if not os.path.isdir(welcomes_dir):
        if os.path.isfile(welcomes_dir):
            os.remove(welcomes_dir)
        os.chdir(person_dir_path)
        os.mkdir(WELCOMES_DIR_PATH_NAME)
    
    # copy all images from current directory to "images" directory
    for item in paths_to_images_in_wrong_dir:
        # create new file path
        new_file_path = os.path.join(images_dir, f"{item}")
        # if image alredy exist, add (number) at the end of its name
        index = 0
        while os.path.isfile(new_file_path):
            index += 1
            item_name, item_ext = os.path.splitext(item)
            new_file_path = os.path.join(images_dir, f"{item_name} ({index}){item_ext}")
        # move to new path
        os.replace(paths_to_images_in_wrong_dir[item], new_file_path)

def encode_face(name, path2root=PATH_TO_ROOT):
    person_dir_path = os.path.join(path2root, KNOW_PEOPLE_DIR_PATH_NAME, name)
    images_dir_path = os.path.join(person_dir_path, IMAGES_DIR_PATH_NAME)
    images_path = {}
    face_encodings = []

    # load image files paths
    print("Collecting image files...", end="\t")
    for file in os.listdir(images_dir_path):
        extension = os.path.splitext(file)[1] # extension of file
        if extension.lower() in VALID_IMAGES_EXTENSIONS:
            images_path[file] = os.path.join(images_dir_path, file)
    print("Collected")

    # encode faces
    image_count = len(images_path)
    index = 0
    print(f"Encoding {image_count} images...")
    for image_name in images_path:
        ts = time.time()
        index += 1
        print(f"\tEncoding image {index}/{image_count} (\"{image_name}\")...", end="\t\t")
        try:
            person_image = face_recognition.load_image_file(images_path[image_name])
            person_face_encoding = face_recognition.face_encodings(person_image)
            if len(person_face_encoding) == 1:
                person_face_encoding = person_face_encoding[0]
                face_encodings.append(person_face_encoding)
            else:
                raise BaseException(f"too many faces, no faces or face too similar to other({len(person_face_encoding)})")
            print("FINISH", end="\t")
        except BaseException as e:
            # print(f"FAILD\t{e}", end="\t")
            print(f"FAILD", end="\t")
        print(f"{(time.time() - ts):.4}s")
    print(f"Encoded {len(face_encodings)} images")

    print(f'Saving to file...', end="\t")
    # convert np array to array
    face_encodings_no_np = []
    for i in range(len(face_encodings)):
        face_encodings_no_np.append(face_encodings[i].tolist())

    # save to file
    json_file_path = os.path.join(person_dir_path, JSON_FILE_NAME)
    with open(json_file_path, 'w') as outfile:
        # json.dump(face_encodings_no_np, outfile)
        json.dump({name:face_encodings_no_np}, outfile)
    print("Saved")

def create_welcome_voice_for_known_person(name, path2root=PATH_TO_ROOT):
    person_dir_path = os.path.join(path2root, KNOW_PEOPLE_DIR_PATH_NAME, name)
    welcomes_dir = os.path.join(person_dir_path, WELCOMES_DIR_PATH_NAME)
    basic_welcome_file = os.path.join(welcomes_dir, BASIC_WELCOME_FILE_NAME)
    create_and_save_welcome_message(f"Witaj {name}", basic_welcome_file)

def create_welcome_voice_for_unknown_person(path2root=PATH_TO_ROOT):
    # create folder for unknow face
    unknowe_dir_name = f"{WELCOMES_DIR_PATH_NAME}_unknown"
    know_people_dir = os.path.join(path2root, KNOW_PEOPLE_DIR_PATH_NAME)
    unknown_dir_path = os.path.join(know_people_dir, unknowe_dir_name)
    if not os.path.isdir(unknown_dir_path):
        if os.path.isfile(unknown_dir_path):
            os.remove(unknown_dir_path)
        os.chdir(know_people_dir)
        os.mkdir(unknowe_dir_name)
    
    # create welocme message
    file_path = os.path.join(unknown_dir_path, BASIC_WELCOME_FILE_NAME)
    create_and_save_welcome_message("Witaj nieznajomy nieznajoma", file_path)

def create_and_save_welcome_message(message, path):
    tts = gtts.gTTS(message, lang='pl')
    tts.save(path)
    print("[mp3] create?")

def encode_for_all(path2root=PATH_TO_ROOT):
    # go to directory with people sub-directories
    people_dir_path = os.path.join(path2root, KNOW_PEOPLE_DIR_PATH_NAME)
    os.chdir(people_dir_path)
    # get people names
    names = list(filter(os.path.isdir, os.listdir(os.curdir)))
    print()
    namesc = len(names)
    index = 0
    for name in names:
        index += 1
        print(f"({index}/{namesc})", end=" ")
        encode_for(name)
        print(end="\n\n")
    pass

def encode_for(name):
    if (name == "welcomes_unknown"):
        pass
    else:
        # preparing files
        # print(f"Start preparing files", end="\t")
        # ts = time.time()
        prepare_dir(name)
        # print(f"Finiszed in {(time.time() - ts):.4} seconds!")

        # encoding
        print(f"Start encoding \"{name}\":")
        ts = time.time()
        encode_face(name)
        create_welcome_voice_for_known_person(name)
        print(f"Finiszed in {(time.time() - ts):.4} seconds!")

def check_if_person_exist(name, path2root=PATH_TO_ROOT):
    # get person directory path
    person_dir_path = os.path.join(path2root, KNOW_PEOPLE_DIR_PATH_NAME, name)
    return not os.path.isfile(person_dir_path) and os.path.isdir(person_dir_path)

if __name__ == '__main__':

    ts = time.time()
    argc = len(sys.argv)
    if argc == 1: # encode ALL people
        encode_for_all()
        create_welcome_voice_for_unknown_person()
    elif argc == 2: # encode SINGLE person
        name = sys.argv[1]
        if check_if_person_exist(name):
            print()
            encode_for(name)
            create_welcome_voice_for_unknown_person()
        else:
            print(f"There is no \"{name}\" folder in {KNOW_PEOPLE_DIR_PATH_NAME}")
    else:
        pass

    print(f"Program execiuted in {(time.time() - ts):.4} seconds!")