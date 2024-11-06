from twitchHandler import TwitchHandler
from streamlabsHandler import StreamlabsHandler

import asyncio

async def main():
    ta = TwitchHandler()
    sa = StreamlabsHandler()

    # Run both handlers concurrently
    await asyncio.gather(
        ta.run(),
        # sa.run()
    )

if __name__ == "__main__":
    asyncio.run(main())