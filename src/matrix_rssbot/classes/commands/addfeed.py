from nio.events.room_events import RoomMessageText
from nio import RoomPutStateError
from nio.rooms import MatrixRoom

from datetime import datetime
from urllib.request import urlopen

import feedparser


async def command_addfeed(room: MatrixRoom, event: RoomMessageText, bot):
    url = event.body.split()[2]

    bot.logger.log(f"Adding new feed to room {room.room_id}")

    state = await bot.get_state_event(room, "rssbot.feeds")

    if not state:
        feeds = []
    else:
        feeds = state["content"]["feeds"]

    feeds.append(url)

    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            print(entry)
    except:
        await bot.send_state_event(
            f"Could not access or parse feed at {url}. Please ensure that you got the URL right, and that it is actually an RSS/Atom feed.",
            True,
        )

    try:
        await bot.send_state_event(
            room,
            "rssbot.feed_state",
            {"timestamp": int(datetime.now().timestamp())},
            url,
        )
        await bot.send_state_event(room, "rssbot.feeds", {"feeds": feeds})
        await bot.send_message(room, f"Added {url} to this room's feeds.", True)
    except:
        await bot.send_message(
            room, "Sorry, something went wrong. Please try again.", true
        )
