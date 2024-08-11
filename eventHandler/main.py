from twitchHandler import TwitchHandler
from streamlabsHandler import StreamlabsHandler

import threading
import asyncio



ta = TwitchHandler()

ta_thread =  threading.Thread(target=asyncio.run, args=(ta.run(),))
ta_thread.start()

sa = StreamlabsHandler()
sa.run()



