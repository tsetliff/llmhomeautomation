import json
import sys

from llmhomeautomation.modules.module import Module
import os
import requests

# Add the personality to tell the system that it does home automation.
class Hue(Module):
    def __init__(self):
        self.bridge_ip_address = None
        self.bridge_api_key = os.getenv("HUE_BRIDGE_API_KEY")
        self.inject_status = False

        self.discover_hue_bridge()

        super().__init__()

    # For setup curl -X POST -d '{"devicetype":"my_hue_app"}' http://192.168.1.100/api
    # curl -X PUT -d '{"on": true}' http://192.168.1.100/api/your_generated_username/lights/1/state

    def process_request(self, request: dict) -> dict:
        keywords = ["light", "lights", "bright", "dim"]
        if any(keyword.lower() in request["message"].lower() for keyword in keywords):
            self.inject_status = True
        else:
            self.inject_status = False

        return request

    # The state of the system
    def process_status(self, status: dict) -> dict:
        # curl -X PUT -d '{"on": true}' http://192.168.1.100/api/your_generated_username/lights/1/state
        url = f"http://{self.bridge_ip_address}/api/{self.bridge_api_key}/lights"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        houseState = response.json()
        print(json.dumps(houseState, indent=4, sort_keys=True))
        #sys.exit()
        response.raise_for_status()
        return status

    def process_command_examples(self, command_examples: list) -> list:
        # Home automation command to change the state of the house
        # [{{"Location": "Device": {{ "setting": "value"}}}}]
        # You may add additional commands to the array like this:
        # [{{"Location": "Device": {{ "setting": "value"}}}}, {{"Location": "Device": {{ "setting": "value"}}}}]
        # You may also use the response command to confirm the change is made:
        # [{{"Location": "Device": {{ "setting": "value"}}}},{{"response": "Concise answer to the question."}}]
        return command_examples

    def discover_hue_bridge(self):
        url = "https://discovery.meethue.com/"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses

            bridges = response.json()
            if bridges:
                for bridge in bridges:
                    print(f"Hue Bridge ID: {bridge['id']}")
                    print(f"Internal IP: {bridge['internalipaddress']}")
                    self.bridge_ip_address = bridge['internalipaddress']
                    break
            else:
                print("No Hue Bridges found on the network.")

        except requests.exceptions.RequestException as e:
            print(f"Error discovering Hue Bridge: {e}")