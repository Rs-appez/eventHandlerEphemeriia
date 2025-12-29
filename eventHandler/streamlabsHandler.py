from decouple import config
import requests
import socketio

from utils import write_log


class StreamlabsHandler:
    def __init__(self):
        self.app_id = config("STREAMLABS_CLIENT_ID")
        self.app_secret = config("STREAMLABS_CLIENT_SECRET")
        self.backend_URL = f"{config('BACKEND_URL')}"
        self.timer_URL = f"{self.backend_URL}/timer/api/timer"
        self.goal_URL = f"{self.backend_URL}/goal/api/campaigns"
        self.token = config("BACKEND_TOKEN")

        self.streamlabs_access_json = self.get_streamlabs_auth()

        self.streamlab_url_socket = f"wss://sockets.streamlabs.com?token={self.streamlabs_access_json['socket_token']}"

    def get_streamlabs_auth(self):
        res = requests.get(
            f"{self.backend_URL}/oauth/api/auth/streamlabs/first",
            headers={"Authorization": self.token},
        )
        if res.status_code == 200:
            return res.json()

        else:
            return None

    def on_donation(self, data):
        name = data["message"][0]["from"]
        amount = data["message"][0]["amount"]
        id = data["event_id"]

        print(f"\n{name} donated {amount}")
        print("-" * 100)
        write_log(f"{name} donated {amount}!")

        res = requests.post(
            f"{self.timer_URL}/donation/",
            json={"name": name, "amount": amount, "id": id},
            headers={"Authorization": self.token},
        )

        # if the request is not successful, retry
        if res.status_code != 200 and res.status_code != 400:
            res = requests.post(
                f"{self.timer_URL}/donation/",
                json={"name": name, "amount": amount, "id": id},
                headers={"Authorization": self.token},
            )

        self.__update_campaign(amount, id, "donation")

    def on_subscription(self, data):
        name = data["message"][0]["name"]
        tier_plan = data["message"][0]["sub_plan"]
        id = data["message"][0]["_id"]
        gifter = data["message"][0]["gifter"] if "gifter" in data["message"][0] else ""

        match tier_plan:
            case "1000":
                print("Tier 1")
                tier = 1
            case "2000":
                print("Tier 2")
                tier = 2
            case "3000":
                print("Tier 3")
                tier = 3
            case _:
                print("Prime")
                tier = 1

        message = f"\n{name} subscribed with tier {tier}"
        if gifter:
            message += f" from {gifter}"
        print(message)
        print("-" * 100)
        write_log(message)

        res = requests.post(
            f"{self.timer_URL}/sub/",
            headers={"Authorization": self.token},
            json={"username": name, "tier": tier, "id": id, "gifter": gifter},
        )

        write_log(f"Response status code: {res.status_code}")
        write_log(f"Response content: {res.content}")


        # if the request is not successful, retry
        if res.status_code != 200 and res.status_code != 400:
            res = requests.post(
                f"{self.timer_URL}/sub/",
                headers={"Authorization": self.token},
                json={"username": name, "tier": tier, "id": id, "gifter": gifter},
            )

        self.__update_campaign(1, id, "sub")

    def on_cheer(self, data):
        name = data["message"][0]["name"]
        amount = data["message"][0]["amount"]
        id = data["message"][0]["_id"]

        print(f"\n{name} cheered {amount} bits!")
        print("-" * 100)
        write_log(f"{name} cheered {amount} bits!")

        res = requests.post(
            f"{self.timer_URL}/bits/",
            headers={"Authorization": self.token},
            json={"username": name, "bits": amount, "id": id},
        )

        # if the request is not successful, retry
        if res.status_code != 200 and res.status_code != 400:
            res = requests.post(
                f"{self.timer_URL}/bits/",
                headers={"Authorization": self.token},
                json={"username": name, "bits": amount, "id": id},
            )

    async def run(self):
        sio = socketio.Client()

        @sio.event
        def connect():
            print("I'm connected!")

        @sio.event
        def connect_error(data):
            print("The connection failed!")

        @sio.event
        def disconnect():
            print("I'm disconnected!")

        @sio.on("event")
        def on_event(data):
            if data["type"] == "donation":
                self.on_donation(data)

            if data["type"] == "subscription":
                self.on_subscription(data)

            if data["type"] == "bits":
                self.on_cheer(data)

        sio.connect(self.streamlab_url_socket, transports="websocket")

    def __update_campaign(self, amount, id, type):
        res = requests.post(
            f"{self.goal_URL}/update_progress/",
            json={"amount": amount, "id": id, "type": type},
            headers={"Authorization": self.token},
        )

        if res.status_code != 200 and res.status_code != 400:
            res = requests.post(
                f"{self.goal_URL}/update_progress/",
                json={"amount": amount, "id": id, "type": type},
                headers={"Authorization": self.token},
            )
