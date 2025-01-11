class Module:
    def __init__(self):
        pass

    def enabled(self) -> bool:
        return True

    # Message type request
    def process_request(self, request: dict) -> dict:
        return request

    # The state of the system
    def process_status(self, status: dict) -> dict:
        return status