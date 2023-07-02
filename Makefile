runsocket:
	python manage.py runserver
testsock:
	echo "Make sure server is running"
	python -m unittest tests/websocket_test.py

