import json
from pytube import YouTube
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # scope contain socket info
        payload = self.scope["url_route"]["kwargs"]
        self.room_name = payload["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

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
    async def initialize(self, event):
        userId = event["userId"]
        username = event["username"]

        if not hasattr(self, "userList"):
            self.userList = []
        userInfo = {
            "userId": userId,
            "username": username,
            "score": 0,
            "ratedThisRound": False,
            "isSinging": False
        }
        self.userList.append(userInfo)
        await self.send(text_data=json.dumps({"userList": self.userList}))

 # broadcast video, determined the current singing user
    async def select_video(self, event):
        # handle video
        video_id = event["video_id"]
        video_url = f'https://www.youtube.com/watch?v={video_id}'

        # Download the audio file from YouTube
        audio = YouTube(video_url).streams.filter(only_audio=True).first()
        if not audio:
            return

        # todo: handle video play here
        audio_file_path = audio.download()
        with open(audio_file_path, 'rb') as file:
            audio_data = file.read()

        # set the user to isSinging
        userId = event["userId"]
        for (id, user) in enumerate(self.userList):
            if user["userId"] == userId:
                user["isSinging"] = True
                break

        await self.send(bytes_data=audio_data, text_data=json.dumps({"video_id": video_id, "userId": userId}))

# end the rating, annouce scores, next singer
    async def finish_rating(self, event):
        userId = event["userId"]
        for (id, user) in enumerate(self.userList):
            if user["userId"] == userId:
                user["isSinging"] = False
                if id == len(self.userList) - 1:
                    winner = get_max_score(self.userList, "score")
                    # reset everything
                    for user in self.userList:
                        user["score"] = 0
                        user["ratedThisRound"] = False
                        user["isSinging"] = False
                    # TODO: quotes here
                    await self.send(text_data=json.dumps({"winner": winner, "scores": winner["score"], "quotes": ""}))
                else:
                    next_singer = self.userList[id+1]
                    await self.send(text_data=json.dumps({"next_singer": next_singer, "scores": user["score"], "userId": userId}))
                    break

    # start the rating, each user rate the singer once
    async def start_rating(self, event):
        score = event["score"]
        userId = event["userId"]
        target = None

        for user in self.userList:
            if user["isSinging"] == True and user["ratedThisRound"] == False and user["userId"] != userId:
                target = user
                user["score"] += score
                break

        for user in self.userList:
            if userId == user["userId"]:
                user["ratedThisRound"] = True

        await self.send(text_data=json.dumps({"userId": userId, "rateFor": target, "score": score}))
        pass

    # group handler
    # type: chat_message forward to this

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
