from dotenv import load_dotenv
load_dotenv()

import os

class BOT:
    TOKEN = os.environ.get("TOKEN", "7861502352:AAFcS7xZk2NvN7eJ3jcPm_HyYh74my8vRyU")

class API:
    HASH = os.environ.get("API_HASH", "0c44906a4feff3b947db76dfa7c57d88")
    ID = int(os.environ.get("API_ID", "27696177"))

class OWNER:
    ID = int(os.environ.get("OWNER", "6987799874"))

class CHANNEL:
    ID = int(os.environ.get("CHANNEL_ID", "-1002178270630"))

class WEB:
    PORT = int(os.environ.get("PORT", 8000))

class DATABASE:
    URI = os.environ.get("DB_URI", "mongodb+srv://drozmarizabel991hull:Xh89XLrFTYOPgupl@cluster0.x8qoe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    NAME = os.environ.get("DB_NAME", "MN_Bot_DB")
