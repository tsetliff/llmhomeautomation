from llmhomeautomation.modules.module import Module
from datetime import datetime

class Time(Module):
    def __init__(self):
        self.inject_time = False
        super().__init__()

    # Message type request
    def process_request(self, request: dict) -> dict:
        if "time" in request["message"]:
            self.inject_time = True
        else:
            self.inject_time = False

        return request

    # The state of the system
    def process_status(self, status: dict) -> dict:
        print(f"Status time with value {self.inject_time}")
        if self.inject_time:
            status.setdefault('general', {})
            status['general']['date'] = datetime.now().strftime("%Y-%m-%d")
            status['general']['time'] = datetime.now().strftime("%H:%M:%S")
        return status