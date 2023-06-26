import websocket
import unittest


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
        # Implement your message handling logic here
        # Assert the expected result based on the received message
        self.assertEqual(message, "Expected message")

    def on_error(self, ws, error):
        pass
        # # Handle error scenarios
        # # Assert the expected error or handle it appropriately
        # self.fail(f"WebSocket error: {error}")

    def on_close(self, ws):
        # Perform cleanup or assertions on connection closure
        # Assert the expected behavior upon connection closure
        self.assertTrue(True)

    def on_open(self, ws):
        # Send a message to the server
        ws.send("Hello, server!")
        # Assert any expected behavior after sending a message
        self.assertTrue(True)

    def test_websocket_connection(self):
        websocket.enableTrace(True)
        self.websocket.on_open = self.on_open
        self.websocket.run_forever()


if __name__ == '__main__':
    unittest.main()
