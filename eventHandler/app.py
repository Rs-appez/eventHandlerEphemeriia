from flask import Flask
from .twitchHandler import TwitchHandler
from .streamlabsHandler import StreamlabsHandler
import os
import threading
import asyncio

app = Flask(__name__)


if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    ta = TwitchHandler()

    ta_thread =  threading.Thread(target=asyncio.run, args=(ta.run(),))
    ta_thread.start()

    sa = StreamlabsHandler()
    sa.run()



