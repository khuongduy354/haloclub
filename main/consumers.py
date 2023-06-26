import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # scope contain socket info
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        # self.userList = []

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # group_send -> group handler -> send to all client socket

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json["type"]
        payload = text_data_json.get("payload")

        # only leaderboard single socket
        # rest should be send whole room
        if type == "leaderboard":
            await self.send()
        else:
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": type, "payload": payload}
            )

    # HANDLER

    async def select_video(self, event):
        video_id = event["video_id"]
        # await self.send(text_data=json.dumps({"video_id": video_id}))
        pass

    async def finish_singing(self, event):

        pass

    async def rating(self, event):
        pass

    # group handler
    # type: chat_message forward to this

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
