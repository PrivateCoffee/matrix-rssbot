from nio.events.room_events import RoomMessageText
from nio import RoomCreateError, RoomInviteError
from nio.rooms import MatrixRoom

from contextlib import closing

async def command_newroom(room: MatrixRoom, event: RoomMessageText, bot):
    room_name = " ".join(event.body.split()[
                         2:]) or bot.default_room_name

    bot.logger.log("Creating new room...")
    new_room = await bot.matrix_client.room_create(name=room_name)

    if isinstance(new_room, RoomCreateError):
        bot.logger.log(f"Failed to create room: {new_room.message}")
        await bot.send_message(room, f"Sorry, I was unable to create a new room. Please try again later, or create a room manually.", True)
        return

    bot.logger.log(f"Inviting {event.sender} to new room...")
    invite = await bot.matrix_client.room_invite(new_room.room_id, event.sender)

    if isinstance(invite, RoomInviteError):
        bot.logger.log(f"Failed to invite user: {invite.message}")
        await bot.send_message(room, f"Sorry, I was unable to invite you to the new room. Please try again later, or create a room manually.", True)
        return

    await bot.matrix_client.room_put_state(
        new_room.room_id, "m.room.power_levels", {"users": {event.sender: 100, bot.matrix_client.user_id: 100}})

    await bot.matrix_client.joined_rooms()
    await bot.send_message(room, f"Alright, I've created a new room called '{room_name}' and invited you to it. You can find it at {new_room.room_id}", True)