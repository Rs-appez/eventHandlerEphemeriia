
from decouple import config
import requests
import socketio

from .utils import write_log

class StreamlabsHandler:
    def __init__(self):
        self.app_id = config("STREAMLABS_CLIENT_ID")
        self.app_secret = config("STREAMLABS_CLIENT_SECRET")
        self.backend_URL = f"http://{config('BACKEND_URL')}:8000"
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

               
    def run(self):
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

        sio.connect(self.streamlab_url_socket, transports='websocket')

