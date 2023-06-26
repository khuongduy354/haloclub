runsocket:
	docker run -p 6379:6379 -d redis:5

testsock:
	python -m unittest tests/websocket_test.py

