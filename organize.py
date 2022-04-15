import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError
from dropbox.exceptions import AuthError
from dotenv import load_dotenv
import os
import sys


def upload_file(file_name, year_str):
    path = "/all_years/" + year_str + "/" + file_name
    with open("saved_tables/" + file_name, 'rb') as f:
        try:
            dbx.files_upload(f.read(), path, mode=WriteMode.overwrite)
            return 0
        except (ApiError, AuthError):
            dbx.refresh_access_token()
            return -1


def get_last_uploaded_set():
    file_name = "last_uploaded.txt"
    last_up = set()
    with open(file_name, 'r') as file:
        for line in file.readlines():
            last_up.add(line.strip())
    return last_up



def exit_program(exctype=None, value=None, traceback=None):
    file_name = "last_uploaded.txt"
    with open(file_name, "a") as file:
        for new in newly_uploaded:
            file.write(new)
            file.write("\n")
    if exctype is not None:
        sys.__excepthook__(exctype, value, traceback)
    sys.exit(-1)



load_dotenv()
USER = os.getenv("DROPBOX_KEY")
PASS = os.getenv("DROPBOX_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")




dbx = dropbox.Dropbox(oauth2_access_token=ACCESS_TOKEN, app_key=USER, app_secret=PASS, oauth2_refresh_token=REFRESH_TOKEN)
dbx.refresh_access_token()

last_uploaded = get_last_uploaded_set()
newly_uploaded = set()

sys.excepthook = exit_program


all_files = os.listdir("saved_tables")
for csv_file in all_files:
    if csv_file in last_uploaded:
        continue

    newly_uploaded.add(csv_file)
    year = csv_file.split("_")[0]
    file_path_incomplete = csv_file
    res = upload_file(file_path_incomplete, year)
    if res != 0:
        print(csv_file)


exit_program()









