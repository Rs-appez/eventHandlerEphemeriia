# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from eventHandler.twitchHandler import TwitchHandler
from eventHandler.streamlabsHandler import StreamlabsHandler

import threading
import asyncio

app = Flask(__name__)


ta = TwitchHandler()

ta_thread =  threading.Thread(target=asyncio.run, args=(ta.run(),))
ta_thread.start()

sa = StreamlabsHandler()
sa.run()



