import os
import json

PROJECT_PATH = os.getcwd()


class Configuration():
    @staticmethod
    def load():
        config_file_path = os.path.join(
            PROJECT_PATH,
            "configs",
            "config.json"
        )
        with open(config_file_path) as config_file:
            config_dict = json.loads(config_file.read())

        token_path = os.path.join(PROJECT_PATH, config_dict["token_path"])

        # load the token if available
        if not os.path.exists(token_path):
            print(f"You need the token file at {token_path}")
            exit(1)
        
        admins_path = os.path.join(PROJECT_PATH, config_dict["admins_path"])

        # load the token if available
        if not os.path.exists(admins_path):
            print(f"You need the admins file at {admins_path}")
            exit(1)
        
        config = Configuration()

        with open(token_path) as token_file:
            config.TOKEN = token_file.readline()
        
        with open(admins_path) as admins_file:
            admins = [int(admin) for admin in admins_file.read().split(";")]
            config.ADMINS = admins
        
        config.LOGS_PATH = os.path.join(PROJECT_PATH, config_dict["logs_path"])
        config.FFMPEG_OPTIONS = config_dict["ffmpeg_options"]
        config.DEFAULT_IMAGE = config_dict["default_image"]
        config.QUEUE_DUMPS_PATH = os.path.join(
            PROJECT_PATH,
            config_dict["queue_dumps_path"]
        )

        return config
