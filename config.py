from os import environ 

class Config:
    API_ID = environ.get("API_ID", "21291")
    API_HASH = environ.get("API_HASH", "ed3c9220b55911903f3fb61f3")
    BOT_TOKEN = environ.get("BOT_TOKEN", "6558508467Fy7bWSpD-2qd-LPH9tAnL2GW8T1Qe4") 
    BOT_SESSION = environ.get("BOT_SESSION", "bot") 
    DATABASE_URI = environ.get("DATABASE", "mongodb+rward@cluster0.pnwq7om.mongodb.net/")
    DATABASE_NAME = environ.get("DATABASE_NAME", "forward-bot")
    BOT_OWNER_ID = [int(id) for id in environ.get("BOT_OWNER_ID", '6245042947').split()]

class temp(object): 
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []
    
