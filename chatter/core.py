
# chatter/core.py
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
import os

DB_PATH = os.getenv("CHATTER_DB", "sqlite:///chatterbot.sqlite3")

chatbot = ChatBot(
    "VikhrBot",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database_uri=DB_PATH
)

def train_default():
    trainer = ChatterBotCorpusTrainer(chatbot)
    trainer.train("chatterbot.corpus.russian")

def train_custom(phrases: list):
    trainer = ListTrainer(chatbot)
    trainer.train(phrases)

def get_response(message: str) -> str:
    return str(chatbot.get_response(message))

def reset_db():
    if DB_PATH.startswith("sqlite:///"):
        path = DB_PATH.replace("sqlite:///", "")
        if os.path.exists(path):
            os.remove(path)
        return True
    return False
