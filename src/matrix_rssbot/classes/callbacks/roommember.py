from nio import RoomMemberEvent, MatrixRoom


async def roommember_callback(room: MatrixRoom, event: RoomMemberEvent, bot):
    if event.membership == "leave":
        bot.logger.log(
            f"User {event.state_key} left room {room.room_id} - am I alone now?",
            "debug",
        )

        if len(room.users) == 1:
            bot.logger.log("Yes, I was abandoned - leaving...", "debug")
            await bot.matrix_client.room_leave(room.room_id)
            return
