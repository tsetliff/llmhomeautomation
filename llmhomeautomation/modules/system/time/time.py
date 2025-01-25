import os
import pytz
from datetime import datetime
from llmhomeautomation.modules.module import Module

from dotenv import load_dotenv
load_dotenv()

class Time(Module):
    def __init__(self):
        self.inject_time = False
        self.timezone = os.getenv("TIMEZONE")
        super().__init__()

    def process_whoami(self, whoami: list) -> list:
        whoami.append("You write out times and numbers using english words in a pattern people will enjoy listening to.")
        return whoami

    # Message type request
    def process_request(self, request: dict) -> dict:
        keywords = ["time", "date", "clock", "when"]
        if any(keyword.lower() in request["message"].lower() for keyword in keywords):
            self.inject_time = True
        else:
            self.inject_time = False

        return request

    # The state of the system
    def process_status(self, status: dict) -> dict:
        print(f"Status time with value {self.inject_time}")

        utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
        if not self.timezone:
            raise ValueError("TIMEZONE environment variable is not set or is invalid.")
        local_timezone = pytz.timezone(self.timezone)
        local_time = utc_time.astimezone(local_timezone)

        if self.inject_time:
            status.setdefault('general', {})
            status['general']['date'] = local_time.strftime("%Y-%m-%d")
            status['general']['time'] = local_time.strftime("%H:%M:%S")
        return status
