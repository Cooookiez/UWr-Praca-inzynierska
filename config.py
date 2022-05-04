import config_helper as ch
# Get a reference to webcam #
# (the default one)
# for mac: 1
# for pi: 0
CAM_REF = 1
CAM_ROTATION = ch.rotate[0] # 0, 90, 180, 270

valid_image_exts = [".jpg", ".jpeg", ".png"]
KNOW_PEOPLE_DIR_PATH_NAME = "known_people"
JSON_FILE_NAME = "faces.json"
UNKNOWN_NAME = "Unknown"
WELCOMES_DIR_PATH_NAME = "welcomes"
ALERT_DELAY_IGNORE = 5 # seconds