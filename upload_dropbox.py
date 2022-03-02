import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError
import os
from dotenv import load_dotenv


class Uploader:

    def __init__(self):
        self.TOKEN = ""
        self.REMOTE_PATH = "/"

        load_dotenv()
        self.TOKEN = os.getenv("DROPBOX_TOKEN")


    def upload(self, local_path):
        dbx = dropbox.Dropbox(self.TOKEN)
        with open(local_path, 'rb') as f:
            try:
                dbx.files_upload(f.read(), self.REMOTE_PATH + local_path, mode=WriteMode.overwrite)
                # print("successful upload")
                return 0
            except ApiError as err:
                # print("something went wrong " + str(err))
                return -1



