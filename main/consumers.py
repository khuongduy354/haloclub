import json
from numpy import argpartition, random
from pytube import YouTube
from channels.generic.websocket import AsyncWebsocketConsumer


def get_winner(userList):
    max_user = userList[0]
    for user in userList:
        if user["score"] > max_user["score"]:
            max_user = user
    return max_user


def get_user(userList: list, attr: str, value):
    for user in userList:
        if user[attr] == value:
            return user
    return None


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # scope contain socket info
        self.startedSinging = False
        self.room_name = self.scope["url_route"]["kwargs"]["roomname"]
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

        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": type, "payload": payload}
        )

        # HANDLER
    async def initialize(self, event):
        user_id = event["payload"]["user_id"]
        username = event["payload"]["username"]

        if not hasattr(self, "userList"):
            self.userList = []
        userInfo = {
            "user_id": user_id,
            "username": username,
            "score": 0,
            "ratedThisRound": False,
            "isSinging": False
        }
        for user in self.userList:
            if user["user_id"] == user_id:
                return
        self.userList.append(userInfo)

        await self.send(text_data=json.dumps({"event_type": "initialize", "userList": self.userList, "new_user": userInfo}))

     # broadcast video, determined the current singing user
    async def select_video(self, event):
        user_id = event["payload"]["user_id"]
        video_id = event["payload"]["video_id"]

        user = get_user(self.userList, "user_id", user_id)
        if not user:
            return
        if not self.startedSinging:
            self.startedSinging = True
            if not self.userList:
                return

            self.userList = [
                x for x in self.userList if x["user_id"] != user_id]
            random.shuffle(self.userList)
            self.userList.insert(0, user)

            user["isSinging"] = True

            await self.send(text_data=json.dumps({"video_id": video_id, "user_id": user_id, "singer_name": user["username"], "event_type": "select_video"}))
        elif user["isSinging"]:
            await self.send(text_data=json.dumps({"video_id": video_id, "user_id": user_id, "singer_name": user["username"], "event_type": "select_video"}))


# end the rating, annouce scores, next singer

    async def finish_rating(self, event):
        user_id = event["payload"]["user_id"]
        for (id, user) in enumerate(self.userList):
            # is singer
            if user["user_id"] == user_id:
                user["isSinging"] = False

                # if singer is the last one singing
                print(self.userList)
                if id == len(self.userList) - 1:
                    winner = get_winner(self.userList)

                    # reset everything
                    for user in self.userList:
                        user["score"] = 0
                        user["ratedThisRound"] = False
                        user["isSinging"] = False
                    self.startedSinging = False

                    quote = "You are a super star!"
                    await self.send(text_data=json.dumps({"winner": winner,  "quote": quote, "userList": self.userList, "event_type": "finish_game"}))
                    break

                # next singer
                else:
                    next_singer = self.userList[id+1]
                    await self.send(text_data=json.dumps({"next_singer": next_singer, "current_singer": user, "event_type": "finish_rating"}))
                    break

    # start the rating, each user rate the singer once
    async def start_rating(self, event):
        score = event["payload"]["score"]
        user_id = event["payload"]["user_id"]

        target = get_user(self.userList, "isSinging", True)
        user = get_user(self.userList, "user_id", user_id)
        if target == None or user == None:
            # TODO
            return

        if target["user_id"] == user["user_id"]:
            await self.send(text_data=json.dumps({"user_id": user_id,  "event_type": "start_rating", "singer_name": user["username"]}))
        elif user["ratedThisRound"] == False:
            target["score"] += int(score)
            user["ratedThisRound"] = True
            await self.send(text_data=json.dumps({"user_id": user_id, "rate_for": target, "rated_score": score, "event_type": "rating"}))
#     # group handler
#     # type: chat_message forward to this
#

    async def chat_message(self, event):
        message = event["payload"]
        await self.send(text_data=json.dumps({"message": message, "event_type": "chat_message"}))
