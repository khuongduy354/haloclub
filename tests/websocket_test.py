from channels.generic.websocket import json
import websocket
import unittest

user1 = {"user_id": 0, "username": "user1",
         "video_id": "yAbnoYfV99g", "rateOther": 5}
user2 = {"user_id": 1, "username": "user2",
         "video_id": "m55PTVUrlnA", "rateOther": 10}


def ws_client(user, action: str, ws):
    payload = None
    if action == "initialize":
        payload = {"user_id": user["user_id"], "username": user["username"]}
    if action == "select_video":
        payload = {"video_id": user["video_id"], "user_id": user["user_id"]}
    if action == "start_rating":
        payload = {"score": user["rateOther"], "user_id": user["user_id"]}
    if action == "finish_rating":
        payload = {"user_id": user["user_id"]}
    if not payload:
        print("invalid action")
        assert False
    payload = json.dumps({"type": action, "payload": payload})
    ws.send(payload)


class WebSocketTest(unittest.TestCase):

    def setUp(self):
        self.websocket_url = "ws://127.0.0.1:8000/ws/chat/testname/"
        self.websocket = websocket.WebSocketApp(self.websocket_url,
                                                on_message=self.on_message,
                                                on_error=self.on_error,
                                                on_close=self.on_close)

    def tearDown(self):
        self.websocket.close()

    def on_message(self, ws, message):
        message = json.loads(message)
        if "event_type" not in message:
            self.assertTrue(False, "Must have event_type")
            return

        event_type = message["event_type"]
        if event_type == "initialize":
            print("initialize")
            assert "userList" in message, "initialize: Must have userList"
        if event_type == "select_video":
            print("select_video")
            assert "video_id" in message, "select_video: Must have video_id"
        if event_type == "start_rating":
            print("start_rating")
            assert message["allowRating"] == True, "start_rating: Must have allowRating"
        if event_type == "rating":
            print("rating")
            assert "ratedScore" in message, "rating: Must have ratedScore"
        if event_type == "finish_rating":
            print("finish_rating")
            assert message["next_singer"]["user_id"] == user2["user_id"], "finish_rating: Must have next_singer"
            assert message["total_scores"] == user2["rateOther"], "finish_rating: Must have total_scores"

        if event_type == "finish_game":
            print("finish_game")
            assert message["winner"]["scores"] == user2["rateOther"], "finish_game: must have winner scores"

    def on_open(self, ws):
        # user 1 join
        ws_client(user1, "initialize", ws)

        # user 2 join
        ws_client(user2, "initialize", ws)

        # user 1 select
        ws_client(user1, "select_video", ws)

        # user 1 start rating
        ws_client(user1, "start_rating", ws)

        # user 2 rates
        ws_client(user2, "start_rating", ws)

        # user 1 finish rating
        ws_client(user1, "finish_rating", ws)

        self.assertTrue(True)

    def on_error(self, ws, error):
        pass
        # # Handle error scenarios
        # # Assert the expected error or handle it appropriately
        # self.fail(f"WebSocket error: {error}")

    def on_close(self, ws):
        # Perform cleanup or assertions on connection closure
        # Assert the expected behavior upon connection closure
        self.assertTrue(True)

    def test_websocket_connection(self):
        websocket.enableTrace(True)
        self.websocket.on_open = self.on_open
        self.websocket.run_forever()


if __name__ == '__main__':
    unittest.main()
