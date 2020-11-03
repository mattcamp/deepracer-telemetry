import sys
import re
import traceback
import paramiko
from websocket import create_connection
import websockets

HOSTNAME = "192.168.0.117"
USERNAME = "deepracer"
PASSWORD = "D33prac3r!"
SERVER_URL = "ws://localhost:8000/ws/0"

p = re.compile('msg: "Setting throttle to (\d+\.\d+)"')

ws = create_connection(SERVER_URL)
ws2 = websockets.connect(SERVER_URL, timeout=0.1)

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, 22, USERNAME, PASSWORD)

    print("connected")

    stdin, stdout, stderr = client.exec_command("source /opt/ros/kinetic/setup.bash; rostopic echo /rosout_agg")
    stdin.close()
    for line in iter(lambda: stdout.readline(2048), ""):
        # print(line, end="")
        if "Setting throttle to" in line:
            match = p.match(line)
            throttle_raw = float(match.group(1))
            throttle = round(throttle_raw * 100)
            print(throttle)
            try:
                # ws.send(str(throttle))
                ws2.send(str(throttle))
            except:
                print("Failed to send to websocket")
                # ws = create_connection(SERVER_URL)
                ws2 = websockets.connect(SERVER_URL, timeout=0.1)
                # ws.send(str(throttle))
                ws2.send(str(throttle))

except Exception as e:
    print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
    traceback.print_exc()
    try:
        client.close()
    except:
        pass
    sys.exit(1)
