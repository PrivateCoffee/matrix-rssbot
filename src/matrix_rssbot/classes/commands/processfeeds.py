from nio.events.room_events import RoomMessageText
from nio import RoomPutStateError
from nio.rooms import MatrixRoom

from datetime import datetime

import feedparser

async def command_processfeeds(room: MatrixRoom, event: RoomMessageText, bot):
    bot.logger.log(f"Processing feeds for room {room.room_id}")

    state = await bot.get_state_event(room, "rssbot.feeds")

    if not state:
        feeds = []
    else:
        feeds = state["content"]["feeds"]

    for feed in feeds:
        feed_state = await bot.get_state_event(room, "rssbot.feed_state", feed)

        if feed_state:
            bot.logger.log(f"Identified timestamp as {feed_state['content']['timestamp']}")
            timestamp = int(feed_state["content"]["timestamp"])
        else:
            timestamp = 0

        try:
            feed_content = feedparser.parse(feed)
            new_timestamp = timestamp
            for entry in feed_content.entries:
                entry_timestamp = int(datetime(*entry.published_parsed[:6]).timestamp())
                if entry_timestamp > timestamp:
                    entry_message = f"__{feed_content.feed.title}: {entry.title}__\n\n{entry.description}\n\n{entry.link}"
                    await bot.send_message(room, entry_message)
                    new_timestamp = max(entry_timestamp, new_timestamp)

            await bot.send_state_event(room, "rssbot.feed_state", {"timestamp": new_timestamp}, feed)
        except:
            raise
            await bot.send_message(
                room,
                f"Could not access or parse RSS feed at {feed}. Please ensure that you got the URL right, and that it is actually an RSS feed.",
                True
            )