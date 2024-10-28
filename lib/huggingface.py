from decouple import config
import requests

class HuggingFace():
    def __init__(self) -> None:
        self.token = config("HF_TOKEN")
        self.headers = {"Authorization": f"Bearer {self.token}"}