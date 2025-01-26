from dotenv import load_dotenv
load_dotenv()

import json
import sys
import os
import requests

from llmhomeautomation.modules.module import Module

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
        url_root = f"http://{self.bridge_ip_address}/api/{self.bridge_api_key}/"
        lights = self.reduce_lights(self.get_url(f"{url_root}lights"))
        groups = self.reduce_groups(self.get_url(f"{url_root}groups"))

        status.setdefault('hue', {})
        status['hue']['lights'] = lights
        status['hue']['groups'] = groups
        print(json.dumps(status))
        return status

    def get_url(self, url: str) -> dict:
        print(f"Making a call to url: {url}")
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()


    def reduce_lights(self, lights: dict) -> dict:
        """
        Reduces the lights to a dictionary keyed by the light ID with specific attributes.
        """
        reduced_lights = {}
        for light_id, light_info in lights.items():
            reduced_lights[light_id] = {
                "name": light_info.get("name"),
                "on": light_info.get("state", {}).get("on"),
                "bri": light_info.get("state", {}).get("bri"),
                "sat": light_info.get("state", {}).get("sat"),
                "hue": light_info.get("state", {}).get("hue"),
            }
        return reduced_lights

    def reduce_groups(self, groups: dict) -> dict:
        """
        Reduces the groups to a dictionary array keyed by the name of the group and a list of lights.
        """
        reduced_groups = {}
        for group_id, group_info in groups.items():
            group_name = group_info.get("name")
            lights = group_info.get("lights", [])
            reduced_groups[group_name] = lights
        return reduced_groups

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
