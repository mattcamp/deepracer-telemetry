# Deepracer live telemetry graphics

This project reads the telemetry data from a physical AWS DeepRacer car and displays the current throttle as a live Gauge chart.

The background is set as a bright green colour, designed to be used as an overlay graphic in OBS for use in the DeepRacer Underground series of streamed races.

There are two moving parts:

1. A small web server which published the gauge chart as a simple HTML page.
2. A client app which SSH's to the DeepRacer car and streams the telemetry data, and then pushes to the web server via a websocket connection.

### Prerequisites

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```



### Starting the server

The server can be installed anywhere, locally or elsewhere (I use a micro EC2 instance when it needs to be public)

```
source venv/bin/activate (if not already active)
cd server
uvicorn main:app --reload
```

Note that by default it will only listen on http://127.0.0.1:8000

If you want the server to be exposed publically then use the following command instead:

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Starting the client 

Do this in another terminal window.

Edit telemetry_client.py and set the car IP and password. You also need to set the hostname/IP of the server URL. If you're running the server locally then you can leave this at it's default.

```
source venv/bin/activate
python ./telemetry_client.py
```

Now browse to the URL of the server (defaults to http://127.0.0.1:8000) to view the gauge. When you change the throttle via the standard DeepRacer web interface the gauge should update.
