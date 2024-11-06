from twitchAPI.twitch import Twitch
from twitchAPI.object.eventsub import (
    ChannelFollowEvent,
    ChannelPredictionEvent
)
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.helper import first
from twitchAPI.type import AuthScope

import requests
import json

from decouple import config
from utils import write_log


class TwitchHandler:
    def __init__(self):
        self.app_id = config("TWITCH_APP_ID")
        self.app_secret = config("TWITCH_APP_SECRET")
        self.backend_URL = f"{config('BACKEND_URL')}"
        self.token = config("BACKEND_TOKEN")

        self.twich_access_json = self.get_twitch_auth()

    def get_twitch_auth(self):
        res = requests.get(
            f"{self.backend_URL}/oauth/api/auth/twitch/first",
            headers={"Authorization": self.token},
        )
        if res.status_code == 200:
            return res.json()

        else:
            return None

    async def on_follow(self, data: ChannelFollowEvent):
        # our event happend, lets do things with the data we got!
        print(
            f"\n{data.event.user_name} now follows {data.event.broadcaster_user_name}!"
        )
        print("-" * 100)
        write_log(f"{data.event.user_name} now follows {data.event.broadcaster_user_name}!")

    async def on_prediction_start(self, data: ChannelPredictionEvent):
        # our event happend, lets do things with the data we got!
 
        write_log(f"Predi start! {data.event.to_dict(True)}!")

    async def run(self):
        print("Starting...")
        # create the api instance and get user auth either from storage or website
        twitch = await Twitch(self.app_id, self.app_secret)

        scope = []

        for s in json.loads(self.twich_access_json["scope"].replace("'", '"')):
            scope.append(AuthScope(s))


        await twitch.set_user_authentication(
            token=self.twich_access_json["access_token"],
            refresh_token=self.twich_access_json["refresh_token"],
            scope=scope,
        )

        user = await first(twitch.get_users())

        print(f"Logged in as {user.display_name}  ({user.id})")

        # create eventsub websocket instance and start the client.
        eventsub = EventSubWebsocket(twitch)
        eventsub.start()
        # subscribing to the desired eventsub hook for our user
        # the given function (in this example on_follow) will be called every time this event is triggered
        # the broadcaster is a moderator in their own channel by default so specifying both as the same works in this example
        # We have to subscribe to the first topic within 10 seconds of eventsub.start() to not be disconnected.
        await eventsub.listen_channel_follow_v2(user.id, user.id, self.on_follow)
        await eventsub.listen_channel_prediction_begin(user.id, self.on_prediction_start)
        

        # eventsub will run in its own process
        # so lets just wait for user input before shutting it all down again
        try:
            while True:
                pass
        except KeyboardInterrupt:
            pass
        finally:
            # stopping both eventsub as well as gracefully closing the connection to the API
            await eventsub.stop()
            await twitch.close()

    