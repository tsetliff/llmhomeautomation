import json
import pyttsx3
import subprocess
from .say import Say

class RunCommand:
    def __init__(self):
        #self.say_engine = pyttsx3.init()
        # self.say_engine.setProperty('voice', 'english')  # Change to 'french', 'german', etc., as available
        # self.say_engine.setProperty('rate', 150)  # Speed (words per minute)
        # self.say_engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

        pass

    def run(self, command):
        print(command)
        command_list = json.loads(command)
        print(command_list)
        for command in command_list:
            if "response" in command:
                Say().say(command["response"])