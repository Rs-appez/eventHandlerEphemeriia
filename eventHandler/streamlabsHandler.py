
from decouple import config
import requests
import socketio

from utils import write_log

class StreamlabsHandler:
    def __init__(self):
        self.app_id = config("STREAMLABS_CLIENT_ID")
        self.app_secret = config("STREAMLABS_CLIENT_SECRET")
        self.backend_URL = f"{config('BACKEND_URL')}"
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
        name = data['message'][0]['from']
        amount = data['message'][0]['amount']
        id = data['event_id']
        # our event happend, lets do things with the data we got!
        print(
            f"\n{name} donated {amount}"
        )
        print("-" * 100)
        write_log(f"{name} donated {amount}!")

        requests.post(
            f"{self.backend_URL}/api/timer/donation/",
            json={
                "name": name,
                "amount": amount,
                "id": id
            },
            headers={"Authorization": self.token},
        )

    def on_subscription(self, data ):
        # our event happend, lets do things with the data we got!

        name = data['message'][0]['name']
        tier_plan = data['message'][0]['sub_plan']
        id = data['event_id']

        print(
            f"\n{name} now subscribes !"
        )
        write_log(f"{name} now subscribes !")

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

        print("-" * 100)

        res = requests.post(
            f"{self.backend_URL}/api/timer/sub/",
            headers={"Authorization": self.token},
            json={
                "username": name,
                "tier": tier,
                "id" : id
            },
        )

        print(res.json())
               
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
        
        @sio.on('event')
        def on_event(data):
            if data['type'] == 'donation':
                self.on_donation(data)

            if data['type'] == 'subscription':
                self.on_subscription(data)

        sio.connect(self.streamlab_url_socket, transports='websocket')

