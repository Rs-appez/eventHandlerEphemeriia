from twitchHandler import TwitchHandler
from streamlabsHandler import StreamlabsHandler

import asyncio

async def main():
    # ta = TwitchHandler()
    sa = StreamlabsHandler()

    try :
        # Run both handlers concurrently
        # await asyncio.gather(
        #     ta.run(),
        #     sa.run()
        # )
        await sa.run()
    finally:
        await StreamlabsHandler.close_client()

if __name__ == "__main__":
    try :
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user. Exiting...")
